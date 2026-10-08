# AI Skills Library

Agent Skills for Userflow. Add them to your AI coding agent once, then describe what you need and your agent picks the right skill.

## What's in the library

- **Userflow Installation skills:** install, verify and improve Userflow.js in your app. No Userflow MCP needed.
- **Skills that report on your data:** read your Userflow data and return a report you can share.
- **Skills that build things:** create content in your Userflow account after you confirm.

Browse the `[skills/](skills)` folder.

## Install

### skills.sh (Cursor, Codex, and other agents)

```bash
npx skills add userflow/ai-skills-library
```

This lists every skill in the library so you can pick the ones you want. Add `-g` for a global install, or `-a <agent>` to target a specific agent.

### Claude Code

```bash
/plugin marketplace add userflow/ai-skills-library
/plugin install userflow@ai-skills-library
```

The plugin adds every skill in the library. Run one with `/userflow:<skill-name>`, or describe what you want and Claude picks the right skill.

### Manual (any agent)

```bash
git clone https://github.com/userflow/ai-skills-library
cp -r ai-skills-library/skills/<skill-name> ~/.claude/skills/
```

Change the destination to wherever your agent reads skills.

### Download (Claude and other apps that take a file)

1. Open the [skills/](skills) folder and pick a skill.
2. Open its `SKILL.md` and click **Download raw file**.
3. Upload it in your AI tool. In Claude, go to **Settings → Customize → Skills**.

## Need help?

Reach out to your Userflow contact or post in the in-app help.