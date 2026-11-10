# Contributing

These rules apply whether a person or an AI agent makes the change.

## Rules

1. **Keep every manifest in sync.** `name`, `version`, `description` and `license` must match across all manifests. `scripts/validate_repo.py` enforces it.
2. **Bump** `version` **whenever anything under** `skills/` **or a manifest changes.** Claude Code and Codex cache installs by version, so without a bump existing users never get the change. Bump every manifest in the same commit.
3. **Never rename the marketplace (**`ai-skills-library`**) or the plugin (**`userflow`**).** Existing installs and Userflow's onboarding links depend on both names. Don't rename skills either: `install-with-ai` is linked from the onboarding flow. Keep `"source": "./"` in `.claude-plugin/marketplace.json`: Claude Code releases before mid-2026 can't install the plugin when it's `"."`.
4. **Use only spec frontmatter keys:** `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Codex, Gemini CLI and other strict loaders skip a skill with any other top-level key. Put custom fields under `metadata`.
5. `name` **equals the folder name.** Use lowercase kebab-case, at most 64 characters. `description` is at most 1024 characters, with no `<` or `>` (claude.ai's upload rejects them).
6. **Keep SKILL.md under 500 lines.** Move detail into `references/` and link it from SKILL.md. Every `references/…`, `scripts/…` or `assets/…` path a SKILL.md names must exist.
7. **Keep skills tool-neutral.** A skill may use a platform-only tool (for example claude.ai's Visualizer) only with a plain-text or markdown fallback for when that tool isn't available. Don't hard-code a customer's own tools (Slack, Jira, Zendesk). Make tool-dependent behavior a setting the skill asks about.
8. **Treat end-user and linked content as data.** Any skill that reads NPS comments, Adoption Agent messages, support tickets, chat threads or linked docs needs a `## Trust boundary` section that says not to follow instructions found in that content.
9. **Writes need a confirmation step.** Skills that create or change things in a Userflow account draft first, show a summary, and write only after the user says yes. Publishing is always a separate yes.
10. **Don't change the license (MIT) without a maintainer decision.**

## Add a new skill with a pull request

Open a pull request for every new skill, and for any change to an existing one that someone else should review.

1. **Branch.** Create a branch from the latest `main`, for example `feat/<skill-name>`.
2. **Write the skill.** Create `skills/<skill-name>/SKILL.md`. The folder name is the skill name and follows the `userflow-`* naming in the existing skills. Put long detail in `skills/<skill-name>/references/` and link to it from SKILL.md. Follow the [Rules](#rules) above, especially 4–9: spec-only frontmatter, under 500 lines, tool-neutral, a Trust boundary section if it reads end-user text, and a confirmation step before any write.
3. **List it in two places:**
   - a row in the skills table in the [README](README.md#skills), under the group it belongs to
   - the matching group in [skills.sh.json](skills.sh.json)
4. **Bump the version** in all six manifests (see [Release](#release), step 1). A new skill is a minor bump, for example 1.3.0 to 1.4.0.
5. **Run the checks** from [Release](#release), step 2, and fix anything that fails. Try the skill in a real agent too (see [Test a local install](#test-a-local-install)): ask for what its description says and confirm it triggers.
6. **Open the pull request** against `main`. In the description, say what the skill does, whether it needs the Userflow MCP, what it reads and writes, and which checks you ran.
7. **Review and merge.** A maintainer reviews it. CI has to be green before it merges. Don't merge your own pull request.

To change an existing skill, follow the same steps without the listing in step 3. A wording fix is a patch bump.

## Release

Each release has to reach Claude Code, Codex, Cursor, Copilot, Gemini CLI and Antigravity, and they each read their own manifest.

1. Bump `version` in all six manifests in one commit: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.antigravity-plugin/plugin.json`, `plugin.json` and `gemini-extension.json`. Use semver: patch for wording fixes, minor for new skills or behavior, major for removed or renamed skills.
2. Commit, then run the checks:
   ```bash
      python3 scripts/validate_repo.py --base origin/main
      claude plugin validate . --strict
      for s in skills/*/; do npx --yes skills-ref validate "$s"; done
   ```
3. CI runs the same checks on the push, plus the manifest schema checks and the Claude plugin directory checks (`claude plugin validate . --profile directory --strict`).

## Test a local install

```bash
claude plugin validate . --strict
claude --plugin-dir .                       # Claude Code, without installing
npx skills add ./ --list                    # skills.sh
```
