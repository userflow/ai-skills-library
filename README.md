# Userflow AI Skills Library

![skills.sh](https://skills.sh/b/userflow/ai-skills-library)

Install and verify Userflow with AI. This repository packages Userflow's Agent Skills so AI coding agents can install, configure, and audit Userflow in your codebase for you.

It ships as a single plugin, `userflow`, that currently bundles three skills:


| Skill                                                | What it does                                                                                                                              |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `[install-with-ai](skills/install-with-ai/SKILL.md)` | Installs Userflow.js into new or existing applications.                                                                                   |
| `[verify-with-ai](skills/verify-with-ai/SKILL.md)`   | Audits an existing Userflow.js install (init, identify, MAU risk, tokens) and reports findings.                                           |
| `[suggest-with-ai](skills/suggest-with-ai/SKILL.md)` | Recommends attributes, stable selectors, and advanced Userflow.js functions for an existing install, and implements only what's selected. |


## Install

Pick the route that matches your agent.

### Claude Code

```bash
/plugin marketplace add userflow/ai-skills-library
/plugin install userflow@ai-skills-library
```

Or run `/plugin` and use the **Discover** tab to browse and install.

All three skills come with the plugin. Invoke one with `/userflow:install-with-ai`, `/userflow:verify-with-ai`, or `/userflow:suggest-with-ai` — or just describe what you want and Claude will pick the matching skill.

### Codex

```bash
npx skills add userflow/ai-skills-library -a codex
```

Or copy the skill folders into `.agents/skills/` in your repository, or `~/.agents/skills/` to make them available everywhere:

### [skills.sh](http://skills.sh)

```bash
npx skills add userflow/ai-skills-library
```

Lists the available skills so you can pick the ones you want. Use `-g` for a global install, or `-a <agent>` to target a specific agent.

### Manual / git clone (any agent)

```bash
git clone https://github.com/userflow/ai-skills-library
cp -r ai-skills-library/skills/* ~/.claude/skills/
```

That copies all three skills at once. To install just one, name it instead:

```bash
cp -r ai-skills-library/skills/install-with-ai ~/.claude/skills/
```

Works with any agent that reads `SKILL.md` skills. Adjust the destination for your agent — Claude Code uses `.claude/skills/`, Codex uses `.agents/skills/`.

### Direct SKILL.md link

Point your agent at the raw skill file:

```
https://raw.githubusercontent.com/userflow/ai-skills-library/refs/heads/main/skills/<skill>/SKILL.md
```

Replace `<skill>` with `install-with-ai`, `verify-with-ai`, or `suggest-with-ai`. For example:

```
Read https://raw.githubusercontent.com/userflow/ai-skills-library/refs/heads/main/skills/install-with-ai/SKILL.md and install Userflow.js in this project.
```

## Documentation

- [Install with AI](https://help.userflow.com/docs/install-with-ai)
- [Verify with AI](https://help.userflow.com/docs/verify-with-ai)
- [Suggest with AI](https://help.userflow.com/docs/suggest-with-ai)

