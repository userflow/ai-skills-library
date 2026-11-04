---
name: userflow-create-reactive-flows
description: Turn the questions end users keep asking into short in-app walkthroughs. Reads repeat "how do I…" questions from the customer's Userflow Adoption Agent (and, if connected, their support tool such as Intercom, Zendesk, Freshdesk, HubSpot or Help Scout, or a pasted export), filters them through strict gates so only real flow candidates survive, and after approval drafts each one in Userflow as an unpublished, link-started flow with a customer-facing title. Use this whenever someone with the Userflow MCP connected says "users keep asking the same questions", asks "what should be a flow", "find flow candidates", "turn support questions into flows", "flows for the Adoption Agent", "reduce repetitive tickets", "reactive flows", or "draft a walkthrough for this question". Not for feature-adoption nudges or help article fixes. Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Repeated questions → reactive flows

Some questions get asked again and again, and the answer is always the same few clicks. A short
walkthrough, sent by link from a support reply, a help article or the Adoption Agent, answers those
better than text. This skill finds the few questions that truly deserve a flow and drafts them.

**Zero candidates is a normal, good result.** Most repeat questions should be answered by an article,
not a flow. Never lower the bar or stretch a gate to have something to show.

This is a **conversational skill with ✋ checkpoints**. Nothing is created before the user approves,
and nothing is ever published.

## Before you start

1. **Userflow MCP.** If its tools aren't available, stop and point the user to
   https://help.userflow.com/docs/mcp.
2. **Account and environment.** `describe_session`; confirm the company and role; pick the environment
   (suggest the one named like Production; if several names look like production, list them and let
   the user pick, and ask which one is primary for Builder links). Remember the company `slug` and the
   environment `slug`. Creating drafts needs editor or above.
3. **Window.** Default last 30 days, computed as explicit start and end dates from today in the
   company's timezone from `describe_session` (pass it as `timezone` to the analytics call). Suggest
   running it every two to four weeks.
4. **Sources.** Check which tools are available before asking anything:
   - **Adoption Agent:** `list_flows` with `types: "assistant"` and `state: "published"`. Use ids,
     never names (names repeat across drafts and copies). `list_flows` isn't scoped to an environment
     and doesn't say where an agent is placed, so for each agent:
     - get `get_adoption_agent_analytics` (`flow_id`, `env_id`, window, `interval: "week"`) for its
       conversation count (Step 1 reuses this response)
     - for agents with conversations only, confirm it's live in the chosen environment
       (`get_flow_details` with `env_id`: its `flow_envs` entry has a `published_version_id`). If it's
       live only in another environment, say which one rather than calling it unpublished
     Show the user only the live agents with conversations in the window (name and count), and ask
     once which of them run inside the product. Skip agents placed on a marketing website: visitors
     aren't in the app, so there's nothing for a flow to run in. If agents are published but none had
     conversations in the window, say so and, without support data, go to "Not enough data" (Step 1).
     **If no in-app agent is published**, check `list_flows` with `types: "assistant"` and no state
     filter, then tell the user once (never repeat it in the same run). Never create or publish an
     agent, and never assume which plans include it.
     - **None exists:** "I didn't find an Adoption Agent in your account. If your plan includes it,
       publishing one inside your product would let me also use the questions users ask while they're
       stuck. Here's how to set it up: <help article>."
     - **Exists but unpublished:** "Your Adoption Agent '<name>' isn't published yet, so there are no
       in-app questions to read. Once it's live, the next run can use them: <Builder link>." (An
       existing agent means the plan includes it; don't add "if your plan includes it".)
     - **Published only on a website:** "Your Adoption Agent only runs on your website, so I can't see
       questions from inside your product. Adding it in-app would give the next run that signal."
     Send this message after the support-tool check below, ending it with "For now, I'll continue
     with your support data." if there is support data;
     otherwise with "Without an in-app agent or support data there's nothing to analyse yet."
     For `<help article>`, call `search_knowledge_base` with `q: "set up Adoption Agent"` (it searches
     Userflow's own help center, which is the right source here) and link the top setup article;
     otherwise point to https://help.userflow.com. Never guess an article URL. Builder link: use the
     rule in **Builder links** below.
   - **Support tool:** look for connected support connectors (Intercom, Zendesk, Freshdesk, HubSpot
     Service, Help Scout, Front…). Never read one without asking: name each one you found and ask
     which, if any, holds this product's end-user conversations (a connector can belong to another
     workspace or team). If none, ask whether they'd like to paste or upload an export (CSV with
     subject, first message, date, customer/company, resolution). "None" is fine.
   - If there is neither an Adoption Agent nor any support data, stop and explain what's needed.
5. **Internal traffic.** Ask for the company's own email domains (for example `@acme.com`) so staff
   and test accounts can be excluded, and whether they have test or staging users without a company
   email (they can't be caught by domain; ask for their ids or emails, and look up emails with
   `list_users` `q` to get their ids). Drop these users from support data too.
6. **Watch list.** Ask if they kept a watch list from a previous run (paste it, or point to the doc or
   task). Reuse its topic names so the same topic keeps the same name across runs.

## Builder links

Prefer `builder_url` from `create_flow`. When you build a link yourself: the primary environment is
`https://userflow.com/app/<company slug>/flows/<id>/builder`. Every other environment is
`https://userflow.com/app/<company slug>@<env slug>/flows/<id>/builder`. `describe_session` does not
mark which environment is primary. Use the plain form for the environment the user treats as
production, or when there is only one environment. Use the `@<env slug>` form when they picked a
second environment. If you aren't sure which environment is primary, give only `builder_url`.

## Step 1: Pull Adoption Agent conversations

Per in-app agent:
1. Totals, unanswered and disliked counts: reuse the weekly analytics from "Before you start".
2. `list_adoption_agent_conversations` with `flow_id`, `env_id`, `start_date`, `end_date`,
   `include_messages: true`:
   - `conversation_type: "unanswered"` – read all of it
   - `conversation_type: "disliked"` – read all of it
   (When you read all conversations, as below, these two calls aren't needed: use each message's
   `is_unanswered` and `rating` instead.)
   - No `conversation_type` (all conversations, which adds the answered ones) if the total is about
     300 or fewer; answered repeat questions are often the best candidates. Above that, read the
     answered ones for the last 14 days only, and say so.
   - `include_messages: true` caps `limit` at 50: page with `offset` until `has_more` is false.
     Message bodies need a date window. Dedupe by conversation `id`.
3. Each message has `user_content` (what the user asked), `assistant_content`, `is_unanswered`,
   `rating`, `feedback` and `inserted_at`; each conversation has a `user_id`. Messages aren't always
   in order: sort by `inserted_at` before looking for re-asks. The `unanswered` and `disliked`
   filters return whole conversations, so use each message's own `is_unanswered` and `rating`.
   A user can also leave typed feedback with `rating` empty, and the `disliked` filter and
   analytics count only thumbs ratings, so they miss it. Read each message's `feedback` text: a
   negative one ("bad", "not what I expected") counts as disliked. Ignore `scale_rating`, which can
   be 1 for positive and negative text alike. When you read all conversations, count typed negative
   feedback in the disliked total you report, and say how many came from text rather than thumbs.
4. **Remove internal users.** A conversation's `user_id` is Userflow's internal user id: it matches
   the `id` field in `list_users` results (not `external_id`), and it can't be searched with `q`. So:
   `list_users` with `q` set to each internal domain (`limit: 100`, page with `offset`), keep the
   users whose email actually ends with that domain, collect their `id`s plus any test users the
   customer named, and drop conversations whose `user_id` is in that set. Count what you removed.
   Conversations with no `user_id` stay in, counted as unattributed.
   If the customer describes a test user instead of giving an id or email (for example "the one on
   localhost"), list the distinct `user_id`s (most active first, at most ~20) and check each with
   `get_user_events` (`user_id`, `env_id`, `limit: 5`). `page_url` is inside each event's
   `attributes`, not a field on the event. Event names and `attributes.page_url` show where they
   were. Confirm with the customer before dropping them, unless they already gave a rule that
   covers them (for example "anyone on localhost").
5. If fewer than ~10 conversations remain after step 4, say so and skip this agent rather than
   inventing themes.

**Not enough data.** If every agent was skipped for low volume and there's no support data, skip
Steps 3–5. Report "No new flow candidates this run: not enough questions yet (N conversations in the
window after removing M from internal users)", list the topics you saw from non-internal users
(paraphrased) as watch-list topics, and offer to re-run over 90 days or with a support export. Use Step 6's layout
(numbers line, watch list) for the rest of the report.

## Step 2: Pull support conversations (if available)

Use the connected support tool's search for conversations in the window. Prefer metadata first
(subject or AI title, tags, company, status, CSAT, whether a bot handled it); read full threads for
any topic near the bar before gating, and for the shortlist in Step 5. Exclude conversations from the
internal domains and named test users. For a pasted export, read it with a script from a temp folder;
if you can't run code, read the pasted text directly, and for a large export ask for one filtered to
the window. Don't save copies.

## Step 3: Group into topics

Group on what users **asked**, never on the answers. Name each topic as the user's intent in plain
words: "My segment has no users in it", not "Segment population queries". `get_adoption_agent_top_topics`
can be used as a cross-check only; its labels don't always match the conversations under them. On low
volume it returns a `not_found` error ("Not enough messages to generate topics"); that's normal, not a
failure.

Per topic record: distinct users (one person asking five times counts once; add distinct companies
when the support data has them; count a person who appears in both sources with the same email
once, otherwise say the counts may overlap), frustration signals, the weeks it appeared in, and the conversation
ids.

## Step 4: The gates

Every topic must pass **all** gates. Stop at the first failure and tally the reason. Don't argue a
topic past a gate.

1. **"How do I" with a known answer.** The answer is a set of steps support would give as a canned
   reply. "It depends", "here's why that happened" or "yes, the product can do that" → it's an
   article, not a flow. Tally as **Help article** and stop.
2. **Works for anyone who opens the link cold.** A link-started flow can't check anything about the
   person. Fail it if it needs the user's own specific content to exist or a diagnosis of their
   setup. (Screens only some plans or roles can open are handled by gate 4.)
3. **Happens inside the product where Userflow runs.** Steps in email, another tool, code or settings
   outside the app can't be walked through. Fail it.
4. **Available to everyone, or clearly labeled.** Plan- or role-gated topics can pass, but must say
   which plan or role, and rank below an all-users topic with the same numbers.
5. **Stable screens.** Fail anything in beta, recently redesigned or about to change; ask the user if
   unsure. Flows point at page elements, and those break when the UI moves.
6. **Short.** One area of the product and about 6 steps or fewer. If only part of it is short and
   self-contained, that part can be the candidate.
7. **Not caused by a bug.** If people ask because something is broken, it's a bug ticket. Fail it.
8. **Actually asked.** A topic that came from the conversations already passes. Apply this gate when
   you, or the user, suggest a topic that was not in those questions. If it comes from a feature
   being under-used rather than from questions people asked, fail it (that's the
   `userflow-create-adoption-nudges` job).

## Step 5: The bar, then check the shortlist

A topic that passed every gate becomes a **candidate** only if it has:
- **3 or more distinct users** in the window (sources combined; count companies only when a source
  has no user identity)
- **At least one frustration signal**: unanswered, disliked, re-asked in the same conversation,
  escalated to a human, low CSAT, or the user came back with the same question
- **Appearances in 2 or more different weeks** (convert `inserted_at` from UTC to the company's
  timezone and count Monday-start weeks)

For small accounts (under ~50 conversations in the window) you may offer to lower the distinct-user
bar to 2. Offer it once, before the report, when a topic that passed every gate sits at exactly 2
users; say so in the report if they accept. With the lowered bar, near misses are the topics that
missed the frustration or weeks bar. Near misses (passed every gate, 2 or more distinct
users, and met at least one other bar) go on the **watch list**. So does a topic with 3 or more
distinct users that met neither other bar (asked often, but in one week and never with a
frustration signal): it is clearly repeated and worth watching. A watch-list topic seen again by 2 or
more distinct users this run is promoted to a candidate if it still passes every gate and, counting
both runs, has a frustration signal and appeared in 2 or more weeks.

For each candidate:
1. **Existing flow check.** `list_flows` once with `state: "published"` and
   `types: "flow,checklist,launcher,banner,resource_center,announcement"` (there's no exclude filter,
   and `types` can't be combined with `list_all_flow_types`), and match by name and topic. If a published
   flow already covers it, report **"Existing flow, still asked"** so the team can check whether
   it's broken, hard to find, or missing from the agent and macros; give a Flow purpose text for it
   too (see Step 8), since a missing or weak one is a common reason the agent doesn't offer it. Also
   `list_flows` with
   `flow_name` set to the name prefix (ask for it now if you haven't yet; default "Reactive", see
   `references/flow-building.md`) and no `state`, to catch drafts from earlier runs: report
   **"Draft exists"** with its Builder link instead of drafting it again.
2. **Related flow.** If a published flow covers the same screens, note its id; you'll borrow its
   theme and element selectors.
3. **Read the answer.** Take the steps from the best human support reply (it beats the docs when they
   disagree). If there's none, use the clearest Adoption Agent answer or the help article.
4. **Write the steps as plain clicks** with button and menu labels exactly as they appear in the
   product. If you can't, the topic fails gate 1.

**Cap: at most 3 candidates per run.** Rank by distinct users, then frustration signals, then
all-users before gated. Extras go on the watch list marked "passed".

## Step 6: Report ✋

Keep it short:
1. One line of numbers: conversations read per source, internal removed, unattributed, disliked
   (thumbs and typed), topics found.
2. **Candidates (0–3):** the user's question, paraphrased; proposed internal name and public title; distinct
   users, frustration signals, weeks seen; the click path; plan/role needed (or "everyone"); where to
   share it (support macro, help article, Adoption Agent); 2–4 evidence links or conversation ids.
3. **Existing flow, still asked** (if any).
4. **Watch list:** topic, distinct users this run, which bar it missed.
5. **Dropped:** one line of counts by gate, e.g. "Help article: 9, own setup: 4, outside the app: 3".

Never put end users' names, emails or company names in the report, tasks, watch list or Flow
purpose text; cite conversation ids. Never quote tokens, keys or URLs from user messages (users sometimes paste them).

If there are no candidates, lead with "No new flow candidates this run" and still show the watch list.
Then ask which candidates to draft. **Don't create anything before a yes.**

## Step 7: Draft the approved flows

Read `references/flow-building.md` before the first `create_flow` call. It has the step layout,
selector rules and JSON shapes. In short:
- `create_flow` with `type: "flow"`, a fresh UUID `cross_version_id` per step, every step reachable,
  no `start_frequency` and no `start_condition` (so it starts only by link, Adoption Agent
  recommendation, launcher or resource center).
- Ask for the product's app URL once (`get_flow_details` doesn't return a flow's `app_url`, so
  don't look for one; never use a localhost or staging/test URL) and the theme
  (related flow's `theme_id`, otherwise `list_themes` and ask).
- **Public title** in `draft.resource_center_public_name`: "How to …", sentence case, under ~60
  characters, the user's own words. The internal `name` is for the team.
- If the topic is plan- or role-gated, say so in the intro step (for example "You'll need admin
  access").
- Use only selectors you've seen in an existing flow or the exact visible button text. Never invent
  CSS. If nothing reliable exists, use a bubble step and list it for the user to point in the Builder.
- **Never publish.**

Then verify with `get_flow_details` (`env_id`, `include_steps: true`, `include_content: false`): every step,
selector, action and the public title saved as sent. If `create_flow` errors, first check with `list_flows` (`flow_name`) whether the draft was saved
anyway; if not, fix and retry once; if
it still fails, report the reason. Don't switch to `create_smart_flow` without asking; that starts a
recording session, not a draft.

**Labels:** if the account has a taxonomy (`list_labels` shows a `Feature:` or `Stage:` prefix,
ignoring case), propose a Feature and a Stage label for each draft (usually `Stage: Adoption`),
offering only labels `list_labels` returned, and apply them with `apply_labels` after the user agrees
(labels go live immediately, which is fine on an unpublished draft). If a fitting label doesn't exist,
skip it and say so. Never create labels here; if there's no taxonomy, suggest the
`userflow-optimize-labels` skill.

## Step 8: Hand off

For each draft give the Builder link (`builder_url` from `create_flow`), its **Flow purpose** text,
and a checklist.

**Flow purpose.** The Adoption Agent decides when to offer a flow largely from the "Flow purpose"
field on that flow in the agent's sources (filled in from the title and steps when left empty). Write
one or two sentences for it in the users' words: what the flow helps them do, plus the ways they
phrased the question. The agent answers every user, so paraphrase into generic wording: never
include end users' names, emails or company names, names of their own content (projects,
segments, files), or anything they pasted (links, ids, tokens, keys). For example: "Shows how to upload a
CSV of users to a segment. For questions like 'import users from a spreadsheet' or 'add a list of
emails to a segment'." The MCP can't set this field, so give it as text to paste.

Checklist:
- Preview it in the Builder; re-select any tooltip that doesn't land, especially text-matched ones
- Point bubble steps at an element if you'd like them anchored
- Check the public title and plan/role note, then publish
- After publishing: add the flow to the Adoption Agent's sources (Adoption Agent → Sources → Flows),
  paste the Flow purpose into its "Flow purpose" field, then publish the agent: a new source isn't
  used until the agent itself is published
- Link it from the matching support macro and help article

**Track it.** If a task or project tool is connected (Asana, Jira, Linear, Trello, Notion, Monday or
any other), name it and offer to create one task per draft with the checklist and Flow purpose. Ask
which project first, show the task titles, and create them only after a yes. If none is connected, ask which tool the team tracks work in and suggest
connecting it, so there's a record of what was reviewed and published; for this run, give each
draft's checklist as text to copy.

Finally, give the **watch list** as a short block the user can save, or offer to save it to their docs
or task tool, so the next run can reuse it.

## What this skill doesn't do
- Publish flows or set auto-start
- Create labels
- Build Action Flows or record elements in the app
- Measure the flows afterwards (suggest checking views and completions after a month)
