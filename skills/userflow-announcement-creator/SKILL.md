---
name: userflow-announcement-creator
description: Create an in-app announcement in Userflow through a guided, conversational flow — gather context (a short summary, OR a linked doc/ticket via a connected MCP or Cowork, OR pasted content), draft and refine the copy with the user, set the notification level (silent / badge / boosted → pop-out, modal, or notification), optionally target specific users, show a confirmation card, create the unpublished draft via the Userflow MCP, hand back the Builder link, and offer to publish. Use this whenever a user with the Userflow MCP connected wants to "create an announcement", "announce a feature / update / release / fix", "post an in-app announcement", "draft an announcement", "let users know about X in Userflow", or turn a release note / changelog entry / Jira ticket / Notion doc into a Userflow announcement. Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow Announcement Creator

Guide the user from a rough idea (or a linked doc/ticket) to a finished, ready-to-publish
Userflow announcement. This is a **conversational, step-by-step** skill: move through the phases
below in order, and **pause for the user at each ✋ checkpoint** — never barrel ahead and create or
publish anything without an explicit yes.

The single most important habit: **create is not publish**. `create_flow` only saves an unpublished
draft and returns a Builder link. Nothing is live until the user confirms and you call
`set_flow_publication`. When in doubt, do less and ask.

## Before you start

1. Confirm the **Userflow MCP** is connected (its tools are available). If not, tell the user this
   skill needs the Userflow connector and stop.
2. Resolve the **environment**. Call `describe_session` to list environments. If there's exactly
   one, use it. If there are several (e.g. production vs. a test env), ask which one this
   announcement is for, and pass that `env_id` on every subsequent Userflow call that accepts it.
   Default to the user's usual working environment if they've made it clear in conversation.

Don't over-explain the plumbing — a brief "Which environment — production?" is enough.

---

## Phase 1 — Gather the context

Ask the user for the source material, offering three ways to provide it:

> "What's this announcement about? You can give me a short summary, share a link to a doc or ticket
> that has the context (Notion, Jira, a Google Doc, etc.), or just paste the content in."

**If they share a link**, fetch it with the matching connected tool — Notion for a Notion page,
the Atlassian tools for a Jira issue or Confluence page, Google Drive for a Doc, Intercom, etc., or
`web_fetch` for a public URL. In Cowork, read an attached/linked file directly. If you can't access
it (no connector, permissioned, returns nothing), say so plainly and ask them to paste the relevant
part instead — don't guess at the contents.

**If they give a summary or paste text**, work from that.

Pull out what an announcement needs: what changed, who it's for, why it matters, and any link or
action users should take. If something important is missing (e.g. there's no obvious user benefit),
ask one short follow-up rather than inventing it.

---

## Phase 2 — Draft and refine the copy

Write the announcement as a **title** plus a short **body**. Keep it clear, specific, and benefit-led
— lead with what the user gets, not internal jargon. If the `userflow-brand-copy` skill is
available, follow its voice rules; otherwise default to concise, friendly, plain language.

✋ **Show the draft and get a read on it.** Present the title and body in the chat (plain, readable —
not raw JSON) and ask:

> "Here's a first draft. Does this capture it? Want any changes to **tone**, **length**, or
> **messaging**?"

Iterate until the user is happy. Small, fast loops beat one giant rewrite. Only move on once they've
confirmed the copy is good.

> Note: image handling is intentionally out of scope for this skill. If the user asks for an image,
> tell them they can add it in the Builder after the draft is created, and continue.

---

## Phase 3 — Delivery settings

Only once the copy is finalized, gather the delivery details. Ask these as a short, natural
sequence — one topic at a time, not a wall of questions.

### 3a. Audience targeting

> "Should this go to **everyone**, or only a **specific set of users**?"

If they want to target, ask them to describe the audience in plain language ("paid plans only",
"companies on the EU region", "users who haven't completed onboarding"). Then translate it into a
`filter_condition` using the predicate DSL:

- Call `list_attribute_definitions` (and `list_event_definitions` / `list_segments` as needed) to
  find the **real** attribute FQNs, event names, and segment IDs — never invent them.
- Build predicates per `references/mcp-reference.md` → *Targeting*.
- **Echo the interpreted audience back in plain English** and get a ✋ nod before treating it as
  final. Data-type mismatches (string `"true"` vs boolean `true`) silently break targeting, so it's
  worth confirming.

If they say everyone, leave `filter_condition` unset.

### 3b. Notification level (post type)

> "How prominent should it be — **Silent**, **Badge**, or **Boosted**? If boosted: **Pop-out**,
> **Modal**, or **Notification**?"

Map their answer to the `level` value (see the table in `references/mcp-reference.md`):

| User says | `level` |
|-----------|---------|
| Silent | `silent` |
| Badge (default) | `badge` |
| Boosted → Pop-out | `popout` |
| Boosted → Modal | `modal` |
| Boosted → Notification / Toast | `toast` |

Briefly explain any option the user seems unsure about (Badge = quiet unread counter; Boosted =
proactively pops up).

### 3c. Resource Center readiness (informational — never blocks)

Every announcement, **even Modal and Toast**, only actually displays if the account has a
**published Resource Center that contains an Announcements block**. Do a quick check with
`list_flows` (`types: "resource_center"`, `state: "published"`). If none is published, mention it as
a heads-up so the announcement doesn't quietly get zero views — but **do not block**; let the user
proceed if they want:

> "Heads-up: I don't see a published Resource Center with an Announcements block, which is what
> actually surfaces announcements to users. You can still create this now and sort that out
> separately — just flagging it."

Keep it to a single informational line. Don't nag or re-raise it.

---

## Phase 4 — Confirmation card

✋ Before creating anything, show a **confirmation card** summarizing the whole announcement, and ask
for a clear go-ahead.

Render it with the visualizer (`visualize:show_widget`) as a compact card if available — otherwise a
tidy formatted summary in chat is fine. Include:

- **Title** and a short **body preview**
- **Notification level** (in the user's words, e.g. "Boosted — Modal")
- **Audience** (plain-English, e.g. "Paid plans only" or "Everyone")
- **Environment**
- The Resource Center heads-up, if it applied

Then ask:

> "Ready for me to create this as a draft in Userflow?"

Wait for the yes.

---

## Phase 5 — Create the draft

On confirmation, create the announcement with `create_flow`:

- `name`: the announcement's internal name (usually the title)
- `type`: `"announcement"`
- `draft.announcement`: `{ title, content (rich2), level }`
- `filter_condition`: only if the user targeted an audience
- `env_id`: the resolved environment

See `references/mcp-reference.md` → *Creating the announcement* for the exact JSON shape and a
copy-ready template. The body must be a **rich2** document, not an HTML string.

`create_flow` returns a **Builder URL**. Give it to the user:

> "Done — here's your announcement draft: [link]. It's saved but not live yet."

---

## Phase 6 — Offer to publish

✋ Publishing is a live, user-facing action — always ask, never auto-publish.

> "Want me to publish it now, or would you rather review it in the Builder first?"

If they say publish, call `set_flow_publication` with `action: "publish"`. It uses a **two-step
confirm**: the first call (without `confirm: true`) returns a confirmation payload; call again with
`confirm: true` to apply. Pass the same `env_id`. See `references/mcp-reference.md` → *Publishing*.

If a Resource Center wasn't published (from Phase 3c), gently remind them once here that the
announcement may not display until that's set up.

If they'd rather review first, leave it as a draft and point them to the Builder link. Done.

---

## Guardrails

- **Never publish without an explicit yes.** Creating a draft is safe and reversible; publishing is
  live. Keep them as two separate, confirmed steps.
- **Never invent** attribute FQNs, event names, segment IDs, or plan names — look them up.
- **Don't skip checkpoints.** The value of this skill is the pause-and-confirm rhythm; a great draft
  published to the wrong audience is worse than a slightly slower flow.
- **Stay in scope.** Copy + level + audience + create + publish. Changelog/distribution and image
  uploads are intentionally out of scope; if asked, note they can be handled in the Builder and move on.
- Keep the conversation light and human — you're a helpful teammate walking them through it, not a form.
