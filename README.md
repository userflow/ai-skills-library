# Userflow AI Skills Library

**Install Userflow with AI.** This repository packages Userflow's Agent Skills so AI coding agents can install and
configure Userflow in your codebase for you.

It ships as a single plugin, **`userflow`**, that currently bundles one skill:

| Skill | What it does |
|---|---|
| [`install-with-ai`](skills/install-with-ai/SKILL.md) | Installs Userflow.js into new or existing appications. |

## Install

Pick the route that matches your agent. Replace `userflow/ai-skills-library` with
this repository's actual `owner/repo` if it differs.

### Claude Code

```
/plugin marketplace add userflow/ai-skills-library
/plugin install userflow@ai-skills-library
```

Then invoke it with `/userflow:install-with-ai` — or just describe what you
want and Claude will auto-invoke the skill.

### skills.sh

```
npx skills add userflow/ai-skills-library@install-with-ai
```

Installs the skill into your agent's skills directory. Add `-g` for a global
install, or `-a <agent>` to target a specific agent.

### Manual / git clone (any agent)

```
git clone https://github.com/userflow/ai-skills-library
cp -r ai-skills-library/skills/install-with-ai ~/.claude/skills/
```

Works with any agent that reads `SKILL.md` skills — Claude Code (`.claude/skills/`),
Cursor, Codex, and others. Adjust the destination directory for your agent.

### Direct SKILL.md link

Point your agent at the raw skill file:

```
https://raw.githubusercontent.com/userflow/ai-skills-library/main/skills/install-with-ai/SKILL.md
```