# Security

## Reporting a vulnerability

If you find a security issue in this repository, please email **security@userflow.com** instead of opening a public issue.

Include the skill name, the steps to reproduce it and what you expected to happen. We'll confirm we've received your report and keep you updated while we look into it.

Userflow's security policies, SOC 2 report and DPA are in the [Userflow Trust Center](https://trust.userflow.com).

## How the skills work

- Skills that change a Userflow account show what they'll do and wait for a yes. Publishing is always a separate yes.
- Skills treat end-user text (NPS comments, Adoption Agent messages, support tickets) and linked docs as data, never as instructions.
- The repo doesn't bundle MCP credentials or API keys. The Userflow MCP signs each person in with their own Userflow login, so it can only do what that person's Userflow role allows.
