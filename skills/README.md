# Skills

Each folder here is one skill. The folder name is the skill name you use in install commands.

## Userflow Installation skills

Work in your app's code.

| Skill | What it does |
|---|---|
| [install-with-ai](install-with-ai/SKILL.md) | Installs Userflow.js into a new or existing web app. |
| [install-userflow-react-native-sdk-with-ai](install-userflow-react-native-sdk-with-ai/SKILL.md) | Installs the React Native SDK into an Expo or bare app. |
| [verify-with-ai](verify-with-ai/SKILL.md) | Audits an existing Userflow.js install and reports issues by severity. |
| [suggest-with-ai](suggest-with-ai/SKILL.md) | Recommends attributes, stable selectors and advanced Userflow.js functions for your app. |

## Skills that report on your data

Read your Userflow data and return a report.

| Skill | What it does |
|---|---|
| [userflow-adoption-agent-topics](userflow-adoption-agent-topics/SKILL.md) | Reports what people asked your Adoption Agent and where it fell short. |
| [userflow-flow-compare](userflow-flow-compare/SKILL.md) | Compares two flows of the same type side by side. |
| [userflow-flow-segment-compare](userflow-flow-segment-compare/SKILL.md) | Compares one piece of content across audience segments. |
| [userflow-nps-summariser](userflow-nps-summariser/SKILL.md) | Groups NPS comments into positive and negative themes. |

## Skills that build things

Create content in your Userflow account after you confirm.

| Skill | What it does |
|---|---|
| [userflow-announcement-creator](userflow-announcement-creator/SKILL.md) | Drafts an in-app announcement from a summary, doc or ticket. |
| [userflow-banner-creator](userflow-banner-creator/SKILL.md) | Drafts an in-app banner from a summary, doc or ticket. |
| [userflow-create-adoption-nudges](userflow-create-adoption-nudges/SKILL.md) | Finds under-used features and drafts unpublished nudges, walkthroughs and funnel charts. |
| [userflow-create-reactive-flows](userflow-create-reactive-flows/SKILL.md) | Turns repeated questions into unpublished link-started walkthroughs. |
| [userflow-segment-creator](userflow-segment-creator/SKILL.md) | Builds a segment from a plain-language audience description. |

## Skills that audit, then change

Read your Userflow account and any connected tools, show a plan, and write only after you approve.

| Skill | What it does |
|---|---|
| [userflow-knowledge-loop](userflow-knowledge-loop/SKILL.md) | Audits your help center from Adoption Agent and support questions, team-chat threads marked for the KB, and recent product changes, sends drafted articles for approval in your messaging tool, and publishes only what your reviewer approves to whatever help center tool you use (or hands them off to paste). Also drafts personal follow-ups, tracked as tasks, for users the Adoption Agent couldn't answer. |
| [userflow-optimize-autostart](userflow-optimize-autostart/SKILL.md) | Audits auto-starting flows, checklists, banners and popup announcements, then applies the fixes you approve as unpublished drafts. |
| [userflow-optimize-labels](userflow-optimize-labels/SKILL.md) | Builds a label taxonomy if needed, labels published content after you approve, and shows what is live. |

## Install one skill
```bash
npx skills add userflow/ai-skills-library@<skill-name>
```
Or copy the folder into your agent's skills directory. To install every skill, see the [main README](../README.md).