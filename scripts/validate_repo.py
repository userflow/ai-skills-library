#!/usr/bin/env python3
"""Repo checks that `claude plugin validate` and `skills-ref validate` don't cover.

Those validators check each manifest's schema on its own. They don't notice a
manifest that drifts from the others, a path that points at nothing, or a
skill that one platform's loader skips. This script does.

Usage:
    python3 scripts/validate_repo.py                  # all checks
    python3 scripts/validate_repo.py --base origin/main  # also require a version
                                                      # bump when shipped files changed
Exit code 1 on any failure. Needs PyYAML.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Plugin manifests that carry name/version/description and must agree.
PLUGIN_MANIFESTS = [
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "plugin.json",  # Agent Plugins 1.0 (VS Code / GitHub Copilot)
    "gemini-extension.json",
    ".antigravity-plugin/plugin.json",
]
# gemini-extension.json has no license field; every other manifest must match.
NO_LICENSE_FIELD = {"gemini-extension.json"}
MARKETPLACES = [
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",  # Codex
]
# Keys older Claude Code releases accept in a marketplace plugin entry. An
# unknown key (for example displayName) makes `/plugin marketplace add` fail
# for users on those releases.
CLAUDE_MARKETPLACE_ENTRY_KEYS = {
    "name", "source", "description", "version", "author", "homepage",
    "repository", "license", "category", "keywords",
}
# Frontmatter keys in the Agent Skills spec. Strict loaders (Codex, Cline,
# Gemini CLI) skip a skill that uses any other top-level key.
SPEC_FRONTMATTER_KEYS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
}
# Userflow MCP tools that return text written by end users. A skill that calls
# one needs a "## Trust boundary" section.
END_USER_CONTENT_TOOLS = ("list_adoption_agent_conversations", "list_survey_responses")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
JUNK_RE = re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini|__MACOSX)(/|$)")
# Files whose change reaches installed users and so needs a version bump.
SHIPPED_PATHS = ("skills/", "assets/", ".claude-plugin/", ".codex-plugin/", ".cursor-plugin/",
                 ".antigravity-plugin/", ".agents/", "plugin.json", "gemini-extension.json",
                 "GEMINI.md")

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def load_json(rel: str):
    path = ROOT / rel
    if not path.exists():
        fail(f"{rel}: missing")
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        fail(f"{rel}: invalid JSON ({e})")
        return None


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def check_manifests() -> dict:
    claude = load_json(".claude-plugin/plugin.json") or {}
    ref_name, ref_version, ref_desc = claude.get("name"), claude.get("version"), claude.get("description")

    for rel in PLUGIN_MANIFESTS:
        data = load_json(rel)
        if data is None:
            continue
        if data.get("name") != ref_name:
            fail(f"{rel}: name {data.get('name')!r} != {ref_name!r} in .claude-plugin/plugin.json")
        if data.get("description") != ref_desc:
            fail(f"{rel}: description differs from .claude-plugin/plugin.json")
        if data.get("version") != ref_version:
            fail(f"{rel}: version {data.get('version')!r} != {ref_version!r}. Bump every manifest together.")
        if ("license" in claude and rel not in NO_LICENSE_FIELD
                and data.get("license") != claude["license"]):
            fail(f"{rel}: license differs from .claude-plugin/plugin.json")
        # Every path a manifest points at must exist.
        for key in ("skills", "mcpServers", "hooks", "logo", "composerIcon", "icon", "contextFileName"):
            for src in (data, data.get("interface", {})):
                val = src.get(key)
                if isinstance(val, str) and not (ROOT / val).exists():
                    fail(f"{rel}: {key} points at {val!r}, which doesn't exist")

    for rel in MARKETPLACES:
        data = load_json(rel)
        if data is None:
            continue
        if data.get("name") != "ai-skills-library":
            fail(f"{rel}: marketplace name must stay 'ai-skills-library' (existing installs use it)")
        names = [p.get("name") for p in data.get("plugins", [])]
        if names != [ref_name]:
            fail(f"{rel}: plugins {names} != [{ref_name!r}]")
        for entry in data.get("plugins", []):
            if rel.startswith(".claude-plugin/"):
                extra = set(entry) - CLAUDE_MARKETPLACE_ENTRY_KEYS
                if extra:
                    fail(f"{rel}: entry keys {sorted(extra)} break older Claude Code releases")
                # "." fails to install on Claude Code releases before mid-2026; "./" works on all.
                if entry.get("source") != "./":
                    fail(f"{rel}: plugin source must be './' (older Claude Code releases reject {entry.get('source')!r})")
            if "license" in entry and entry["license"] != claude.get("license"):
                fail(f"{rel}: plugin license differs from .claude-plugin/plugin.json")
            if "description" in entry and entry["description"] != ref_desc:
                fail(f"{rel}: plugin description differs from .claude-plugin/plugin.json")
            if "version" in entry and entry["version"] != ref_version:
                fail(f"{rel}: plugin version differs from .claude-plugin/plugin.json")
    return claude


def parse_frontmatter(path: Path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"{path.relative_to(ROOT)}: no YAML frontmatter")
        return None, text
    try:
        return yaml.safe_load(m.group(1)) or {}, text[m.end():]
    except yaml.YAMLError as e:
        fail(f"{path.relative_to(ROOT)}: invalid frontmatter ({e})")
        return None, text


def check_skills() -> list[str]:
    names = []
    for d in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        rel = d.relative_to(ROOT)
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            fail(f"{rel}: no SKILL.md")
            continue
        fm, body = parse_frontmatter(skill_md)
        if fm is None:
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        names.append(d.name)
        if name != d.name:
            fail(f"{rel}: frontmatter name {name!r} must equal the folder name")
        if not NAME_RE.match(name) or len(name) > 64:
            fail(f"{rel}: name must be lowercase-kebab-case, at most 64 characters")
        if not isinstance(desc, str) or not desc.strip():
            fail(f"{rel}: description missing")
        else:
            if len(desc) > 1024:
                fail(f"{rel}: description is {len(desc)} characters (max 1024)")
            if "<" in desc or ">" in desc:
                fail(f"{rel}: description contains < or > (claude.ai upload rejects it)")
        extra = set(fm) - SPEC_FRONTMATTER_KEYS
        if extra:
            fail(f"{rel}: frontmatter keys {sorted(extra)} aren't in the Agent Skills spec; "
                 "strict loaders skip the skill. Move them under metadata.")
        # Every references/, scripts/ or assets/ path the skill names must exist.
        for ref in sorted(set(re.findall(r"(?:references|scripts|assets)/[A-Za-z0-9_.-]+", body))):
            if not (d / ref).exists():
                fail(f"{rel}: references {ref}, which doesn't exist")
        skill_text = body + "".join(p.read_text() for p in sorted(d.glob("references/*.md")))
        if any(t in skill_text for t in END_USER_CONTENT_TOOLS) and "\n## Trust boundary" not in body:
            fail(f"{rel}: reads end-user text but has no '## Trust boundary' section")
    return names


def check_indexes(skill_names: list[str]) -> None:
    index = (ROOT / "README.md").read_text()
    for n in skill_names:
        if f"](skills/{n}/SKILL.md)" not in index:
            fail(f"README.md: {n} isn't listed in a skills table")
    grouping = load_json("skills.sh.json") or {}
    grouped = [s for g in grouping.get("groupings", []) for s in g.get("skills", [])]
    for n in skill_names:
        if n not in grouped:
            fail(f"skills.sh.json: {n} isn't in any grouping")
    for n in grouped:
        if n not in skill_names:
            fail(f"skills.sh.json: {n} isn't a skill folder")


def check_tracked_files() -> None:
    for f in git("ls-files").splitlines():
        if JUNK_RE.search(f):
            fail(f"{f}: OS metadata file is tracked; the plugin directory refuses it")


def check_version_bump(base: str, version: str) -> None:
    try:
        changed = git("diff", "--name-only", f"{base}...HEAD").splitlines()
    except subprocess.CalledProcessError:
        # The base commit isn't in this checkout (for example after a force push).
        print(f"⚠ Skipped the version-bump check: can't compare with {base}")
        return
    shipped = [f for f in changed if f.startswith(SHIPPED_PATHS)]
    if not shipped:
        return
    try:
        old = json.loads(git("show", f"{base}:.claude-plugin/plugin.json")).get("version")
    except subprocess.CalledProcessError:
        return
    if old == version:
        fail(f"Shipped files changed ({', '.join(shipped[:5])}{'…' if len(shipped) > 5 else ''}) "
             f"but version is still {version}. Bump it in every manifest, or installed copies "
             "won't update.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to compare against for the version-bump check")
    args = ap.parse_args()

    claude = check_manifests()
    names = check_skills()
    check_indexes(names)
    check_tracked_files()
    if args.base:
        check_version_bump(args.base, claude.get("version"))

    if errors:
        print(f"✘ {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✔ Repo checks passed ({len(names)} skills, version {claude.get('version')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
