# AI Skills Library

Agent Skills for Userflow. Add them to your AI agent once, then describe what you need and your agent picks the right skill.

The skills follow the open [Agent Skills](https://agentskills.io) standard, so the same `skills/` folder works in Claude, ChatGPT and Codex, Cursor, GitHub Copilot, Gemini CLI, Antigravity and any other agent that reads `SKILL.md` files.

## What's in the library

- **Userflow Installation skills:** install, verify and improve Userflow.js in a web app, and install the React Native SDK in an Expo or bare app.
- **Skills that report on your data:** read your Userflow data and return a report you can share.
- **Skills that build things:** create content in your Userflow account after you confirm.
- **Skills that audit, then change:** read your Userflow account and any connected tools, show a plan, and write only after you approve.

## Skills

Each skill also has a page in the [Userflow help center](https://help.userflow.com/docs/ai-skills-library).

### Userflow Installation skills

Work in your app's code.

| Skill | What it does |
|---|---|
| [install-with-ai](skills/install-with-ai/SKILL.md) | Installs Userflow.js into a new or existing web app. |
| [install-userflow-react-native-sdk-with-ai](skills/install-userflow-react-native-sdk-with-ai/SKILL.md) | Installs the React Native SDK into an Expo or bare app. |
| [verify-with-ai](skills/verify-with-ai/SKILL.md) | Audits an existing Userflow.js install and reports issues by severity. |
| [suggest-with-ai](skills/suggest-with-ai/SKILL.md) | Recommends attributes, stable selectors and advanced Userflow.js functions for your app. |

### Skills that report on your data

Read your Userflow data and return a report.

| Skill | What it does |
|---|---|
| [userflow-adoption-agent-topics](skills/userflow-adoption-agent-topics/SKILL.md) | Reports what people asked your Adoption Agent and where it fell short. |
| [userflow-flow-compare](skills/userflow-flow-compare/SKILL.md) | Compares two flows of the same type side by side. |
| [userflow-flow-segment-compare](skills/userflow-flow-segment-compare/SKILL.md) | Compares one piece of content across audience segments. |
| [userflow-nps-summariser](skills/userflow-nps-summariser/SKILL.md) | Groups NPS comments into positive and negative themes. |

### Skills that build things

Create content in your Userflow account after you confirm.

| Skill | What it does |
|---|---|
| [userflow-announcement-creator](skills/userflow-announcement-creator/SKILL.md) | Drafts an in-app announcement from a summary, doc or ticket. |
| [userflow-banner-creator](skills/userflow-banner-creator/SKILL.md) | Drafts an in-app banner from a summary, doc or ticket. |
| [userflow-create-adoption-nudges](skills/userflow-create-adoption-nudges/SKILL.md) | Finds under-used features and drafts unpublished nudges, walkthroughs and funnel charts. |
| [userflow-create-reactive-flows](skills/userflow-create-reactive-flows/SKILL.md) | Turns repeated questions into unpublished link-started walkthroughs. |
| [userflow-segment-creator](skills/userflow-segment-creator/SKILL.md) | Builds a segment from a plain-language audience description. |

### Skills that audit, then change

Read your Userflow account and any connected tools, show a plan, and write only after you approve.

| Skill | What it does |
|---|---|
| [userflow-knowledge-loop](skills/userflow-knowledge-loop/SKILL.md) | Audits your help center from Adoption Agent and support questions, team-chat threads marked for the KB, and recent product changes, sends drafted articles for approval in your messaging tool, and publishes only what your reviewer approves to whatever help center tool you use (or hands them off to paste). Also drafts personal follow-ups, tracked as tasks, for users the Adoption Agent couldn't answer. |
| [userflow-optimize-autostart](skills/userflow-optimize-autostart/SKILL.md) | Audits auto-starting flows, checklists, banners and popup announcements, then applies the fixes you approve as unpublished drafts. |
| [userflow-optimize-labels](skills/userflow-optimize-labels/SKILL.md) | Builds a label taxonomy if needed, labels published content after you approve, and shows what is live. |

## Connect the Userflow MCP

The skills don't bundle the Userflow MCP, so connect it once in your AI tool. Use the same server URL everywhere:

```bash
https://api.userflow.com/mcp
```

Everyone signs in with their own Userflow login, so the MCP can only see and do what that person's Userflow role allows. Full steps and troubleshooting are in the [Userflow MCP guide](https://help.userflow.com/docs/mcp).

## Install

### Claude (claude.ai and Claude Desktop)

Upload the skills you want as files. See [Download](#download-claude-and-other-apps-that-take-a-file).

### Claude Code

```bash
/plugin marketplace add userflow/ai-skills-library
/plugin install userflow@ai-skills-library
```

The plugin adds every skill in the library. Run one with `/userflow:<skill-name>`, or describe what you want and Claude picks the right skill.

### Codex (CLI, IDE and the ChatGPT desktop app)

```bash
codex plugin marketplace add userflow/ai-skills-library
codex plugin add userflow@ai-skills-library
```

Start a new Codex session after installing.

### Cursor

Have a team admin import this repository as a team marketplace (**Dashboard → Settings → Plugins → Import**), or install the skills with skills.sh:

```bash
npx skills add userflow/ai-skills-library -a cursor
```

### VS Code and GitHub Copilot

1. In VS Code, turn on the `chat.plugins.enabled` setting.
2. Open the Command Palette and run **Chat: Install Plugin From Source**.
3. Enter `https://github.com/userflow/ai-skills-library`.

For the Copilot CLI:

```bash
copilot plugin install userflow/ai-skills-library
```

### Gemini CLI

```bash
gemini extensions install https://github.com/userflow/ai-skills-library
```

### Antigravity

```bash
agy plugin install https://github.com/userflow/ai-skills-library
```

### skills.sh (any agent)

```bash
npx skills add userflow/ai-skills-library
```

This lists every skill in the library so you can pick the ones you want. Add `-g` for a global install, or `-a <agent>` to target a specific agent.

### Manual (any agent)

```bash
git clone https://github.com/userflow/ai-skills-library
cp -r ai-skills-library/skills/<skill-name> ~/.agents/skills/
```

`~/.agents/skills/` is read by Codex, Cursor, Copilot and Gemini CLI. Some agents use their own folder:

| Agent | Skills folder |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` |
| Gemini CLI | `~/.gemini/skills/` |

### Download (Claude and other apps that take a file)

Apps that install skills from a file, like claude.ai and Claude Desktop, need one zip per skill.

1. Download this repository (**Code → Download ZIP**) and unzip it.
2. Zip the whole skill folder you want from `skills/`, for example `skills/install-with-ai`. The folder itself goes in the zip, with `SKILL.md` inside it.
3. Upload that zip in your app's skills settings.

Ready-made zips of every skill are on the [Userflow help center](https://help.userflow.com/docs/ai-skills-library).

## Need help?

Reach out to [Userflow](https://www.userflow.com/contact). To report a security issue, see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE)
