# Userflow AI Skills Library

[![skills.sh](https://skills.sh/b/userflow/ai-skills-library)](https://skills.sh/userflow/ai-skills-library)

**Install and verify Userflow with AI.** This repository packages Userflow's Agent Skills so AI coding agents can install, configure, and audit Userflow in your codebase for you.

It ships as a single plugin, **`userflow`**, that currently bundles two skills:

| Skill | What it does |
|---|---|
| [`install-with-ai`](skills/install-with-ai/SKILL.md) | Installs Userflow.js into new or existing applications. |
| [`verify-with-ai`](skills/verify-with-ai/SKILL.md) | Audits an existing Userflow.js install (init, identify, MAU risk, tokens) and reports findings. |

## Install

Pick the route that matches your agent. Replace `userflow/ai-skills-library` with
this repository's actual `owner/repo` if it differs.

### Claude Code

```
/plugin marketplace add userflow/ai-skills-library
/plugin install userflow@ai-skills-library
```

Then invoke a skill with `/userflow:install-with-ai` or `/userflow:verify-with-ai` — or just describe what you want and Claude will auto-invoke the matching skill.

### skills.sh

```
npx skills add userflow/ai-skills-library@install-with-ai
npx skills add userflow/ai-skills-library@verify-with-ai
```

Installs the skill into your agent's skills directory. Add `-g` for a global
install, or `-a <agent>` to target a specific agent.

### Manual / git clone (any agent)

```
git clone https://github.com/userflow/ai-skills-library
cp -r ai-skills-library/skills/install-with-ai ~/.claude/skills/
cp -r ai-skills-library/skills/verify-with-ai ~/.claude/skills/
```

Works with any agent that reads `SKILL.md` skills — Claude Code (`.claude/skills/`),
Cursor, Codex, and others. Adjust the destination directory for your agent.

### Direct SKILL.md link

Point your agent at the raw skill file:

```
https://raw.githubusercontent.com/userflow/ai-skills-library/refs/heads/main/skills/install-with-ai/SKILL.md
https://raw.githubusercontent.com/userflow/ai-skills-library/refs/heads/main/skills/verify-with-ai/SKILL.md
```