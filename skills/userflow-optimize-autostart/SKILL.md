---
name: userflow-optimize-autostart
description: Audit every published Userflow flow and checklist that auto-starts, plus banners and popup announcements that show on their own, to find where end users get too much at once or the wrong content. Checks every start condition against what real users actually saw, then gives each item a Keep / Fix / Retire / Review action with evidence and the exact change, in a decision tracker. Applies fixes only after the user approves, as unpublished drafts (a Retire unpublishes at once). Use this whenever someone with the Userflow MCP connected says users are "seeing too many flows", "getting bombarded", "too many pop-ups or modals", wants to "audit auto-start flows", "clean up old flows", "retire flows", "which flows show to new or trial users", "review our targeting", or asks why engagement with their in-app content is dropping. Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow auto-start audit

End users who get several modals, tours and checklists in a row stop reading all of them. This skill
finds every published item that starts on its own, works out which ones reach the same users at the
same moment, checks that against what users actually saw, and proposes a change for each one. The
customer decides; nothing goes live without them.

**How to use this skill.** Customers build start conditions in endless combinations, so this skill
gives you two things: the platform rules (how Userflow decides what to show, which you can't guess)
and a method for reasoning about any setup. It does not give you a checklist. Every list of problems
or fixes below is a set of examples. Never stop at the examples, and never apply one to an item
without checking it fits that item's purpose.

This is a **conversational skill with ✋ checkpoints**. Do not skip a checkpoint, and never publish,
unpublish or edit a flow before the user has said yes to that exact change. `update_flow` has no
confirmation step of its own, so the checkpoints are the only safeguard.

**Finish the whole audit before Checkpoint 1.** Apart from the setup questions and hard stops in
"Before you start", the checkpoints are the only places to stop. Before Checkpoint 1, every in-scope
item must have been read (Step 2), described (Step 3) and measured (Step 4), and all four checks in
Step 5 must have run. Size is not a reason to stop: accounts with 200+ items are normal. Work in
batches and give a one-line progress note after each ("checked 120 of 217 items"), then carry on
without waiting. Never end a turn by recommending that the audit be finished or by asking whether to
continue, and never present partial results as the audit or the tracker. Only a tool that keeps
failing is a reason to stop early: then name the error, say exactly what is done and what is left,
and still go through Checkpoint 1 with "checked X of Y". Items you didn't check go into the tracker
as "not checked yet", and only after the user says go on.

Talk to the user in plain words throughout (see **Writing style** at the end).

## Before you start

1. **Userflow MCP.** If its tools aren't available, stop and point the user to
   https://help.userflow.com/docs/mcp.
2. **Account and environment.** Call `describe_session`. Tell the user which company you're connected
   to and their role. If there's more than one environment, ask which one to audit: suggest the one
   named like Production, and if several names look like production, list them and let the user
   pick. Remember its `env_id` and `slug` for every call, and the company `slug` for Builder links.
   - If the role is viewer, say the audit will run read-only and fixes must be applied by an editor.
3. **Scope.** State these defaults in one short message and only ask if the user's request says
   otherwise:
   - **Audience:** all users. If the user named an audience ("trial users", "new signups", "our
     Enterprise customers", a segment), resolve it now: `list_segments` (with `include_conditions`)
     or `list_attribute_definitions` to find the real attribute and value. Never guess a value;
     string matches are exact and case-sensitive.
   - **Window:** last 30 days.
   - **Output:** a decision tracker (see Step 7) plus a short summary in chat. Settle now where the
     tracker will go, so it isn't a surprise at the end: name a spreadsheet connector if one is
     available and signed in (Google Sheets, Excel/OneDrive or similar), and ask whether to use it.
     If the user picks it, make one cheap read call with it now to confirm it works (a connector can
     be listed but turned off by an admin); if that fails, say so and switch to a file. Otherwise
     say you'll create an .xlsx or CSV file, or give the CSV in chat if you can't create files.

## Builder links

`https://userflow.com/app/<company slug>/flows/<id>/builder` for the primary environment.
`https://userflow.com/app/<company slug>@<env slug>/flows/<id>/builder` for every other environment.
The same path is used for flows, checklists, banners and announcements. `describe_session` does not
mark which environment is primary. Use the plain form for the environment the user treats as
production, or when there is only one environment. If several environments look like production,
ask which one is primary. Use the `@<env slug>` form when they picked a second environment.

## How Userflow decides what users see

These are platform facts. Reason from them; don't contradict them.

1. **Flows and checklists** auto-start only when `start_frequency` is not `never` and there is a
   `start_condition`. They share one slot:
   - An open **flow** blocks every other flow and every checklist.
   - An open **checklist** blocks other checklists. A flow may still start and interrupt it.
   - When several could start, the order is: one the user has never seen, then the one they saw
     longest ago, then higher `priority` (stored as 1–5, where 5 is "Highest" in the Builder and 1
     is "Lowest"), then the one created first, then flow id. Priority is not the first rule. A
     lower-priority flow they have never seen starts before a higher-priority flow they have
     already seen. Only one starts at a time; when it ends, the next can start straight away if its
     conditions still match and, for a `once` item, the user hasn't seen it yet.
   - The interruption guard (`throttle_value` and `throttle_unit` together) counts time since the
     user's last **flow** session only. Checklist and banner activity does not hold the next item
     back. One half without the other has no effect. `throttle_value: 0` is no guard.
   - `filter_condition` only limits who is eligible once something tries to start the item. It does
     not start it. `hidden_condition` hides the item while it is true.
   - `start_limit` is a lifetime count per user for `multiple`. A missing `start_limit` on
     `multiple` is not "unlimited": once the user has seen the item, the check compares the count to
     an empty limit and fails, so the item won't repeat.
   - `scope_by_group: true` counts starts and completion per company, so one teammate seeing or
     finishing it counts for their whole company. `once_per_group` needs it.
   - `only_start_if_not_completed` skips users who already completed it (for `multiple`/`always`).
   - `restart_enabled` lets users restart a flow themselves. Repeat views on a `once` item can come
     from restarts, not from the auto-start rule.
2. **Banners** do not use that queue. A published banner is shown when `filter_condition` is missing
   or the user matches it, including while a flow is open, and a flow can auto-start while a banner
   is showing. The user sees both together. Only **one banner shows per page** at a time: the higher
   `priority`, and on a tie the one created first. When the user dismisses it, the next banner whose
   condition still matches shows. So a second banner on the same page is delayed, not lost, and the
   user gets them one after another. A banner whose `start_frequency` is `never` is still on
   screen. Do not drop it for that.
3. **Announcements.** `silent` and `badge` only appear in the resource center. `modal`, `toast` and
   `popout` render as their own popup and can appear alongside a flow. They do not use
   `start_frequency` or the interruption guard. Their audience is `filter_condition` when present;
   with no condition they go to everyone on every page.
4. **When conditions are checked.** Auto-start conditions are evaluated when a page loads and when
   the user navigates, not continuously. A rule like "element is clicked" won't start the item again
   until the user navigates.
5. **One item can start another.** These starts are deliberate design, not overload by default:
   - a `start_condition` event rule on a flow event (for example `flow_step_seen`,
     `flow_completed`) whose `where_condition` has `attribute_name: "event/flow_id"`
   - a button or step action `{"type": "start_flow", "other_flow_id": "<id>"}` inside another item
     (visible only when you read that item's steps or announcement buttons)
   - checklist tasks and launcher actions that start a flow

Launchers, resource centers, embeds, sites, trackers and Adoption Agents are not part of this audit.
Launchers are pinned to a page (`draft.url_pattern`) and stay out of the flow queue.

## Step 1: List what starts or shows on its own

1. `list_flows` with `list_all_flow_types: true` and `state: "published"`. Large accounts return a
   big payload; if it's saved to a file, parse it with a script rather than reading it into context. If you can't
   run code, keep only each item's id, name, type and state.
   `list_flows` isn't scoped to an environment; Step 2 checks which items are live in the chosen one.
2. Split the list:
   - **Queue:** `flow` and `checklist`.
   - **Banners:** `banner`.
   - **Announcements:** `announcement` (popup or resource-center only is settled in Step 2).
   - Drop `tracker`, `assistant`, `launcher`, `resource_center`, `embed` and `site`. Count them in
     one line.
3. If the queue, the banner list and the announcement list are all empty, say so and stop.

## Step 2: Read each item's settings

For each remaining item call `get_flow_details` with `env_id`, `history_limit: 1` and
`include_steps: false`. For more than ~40 items, split the ids into batches (use parallel sub-agents
if your environment supports them) and have each batch return one compact JSON line per item.
Without sub-agents, go item by item and keep only that one-line record for each; never keep the raw
responses in your notes, so the audit fits however large the account is. If your turn ends before
the audit is done anyway (some AI tools cap how long one turn can run), say "checked X of Y so far,
continuing" and carry on from the next unchecked item on the user's next message: don't present it
as a stopping point or ask whether to continue.

Capture, per item (paths as `get_flow_details` returns them):
- `draft.start_frequency` (`never`, `once`, `once_per_group`, `multiple`, `always`)
- `draft.start_condition`, plus `draft.filter_condition` and `draft.hidden_condition` when present.
  A missing key means no condition of that kind.
- **URL rule.** For flows and checklists it is a condition inside `draft.start_condition` with
  `"type": "page"` and `url_pattern: {includes, excludes}`. For banners and announcements, look for
  that same page condition inside `draft.filter_condition`. `draft.url_pattern` is the launcher
  field; do not treat it as the rule for anything else. An item has no URL rule ("every page") only
  when that page condition is absent.
- `draft.throttle_value` and `draft.throttle_unit` (either missing, or value 0, means no
  interruption guard). Queue items only.
- `draft.priority`, `draft.start_limit`, `draft.start_interval_value` / `draft.start_interval_unit`
  (a missing `start_interval_value` means no gap between repeats of this same item; ignore
  `start_interval_unit` unless the frequency is `multiple` or `always`, because it is returned even
  when unused)
- `draft.scope_by_group`, `draft.only_start_if_not_completed`, `draft.restart_enabled`
- For announcements, `draft.announcement.level` (`silent`, `badge`, `popout`, `modal`, `toast`).
  `level` is returned without `include_content`.
- `flow_envs[0].draft_dirty` (unpublished edits exist; trust this flag even when the draft and
  published version numbers differ) and whether `flow_envs` is empty. `get_flow_details` already
  filters `flow_envs` to the `env_id` you passed, so `[0]` is that environment.
- `version_info.first_published_at` and `version_info.latest_publisher.name` (there is no top-level
  `first_published_at` here, unlike `list_flows`)
- top-level `edited_at` (the concurrency token for Step 8). Do not reuse `edited_at` from
  `list_flows`; the two differ.
- `labels` (names), when present: they often say what the item is for.
- Anything else in `draft` that changes who sees the item or when. If you don't recognise a field,
  record it as it is rather than dropping it.

Rules:
- **Queue, in scope** = type `flow` or `checklist`, `start_frequency` is not `never`, and there is a
  `start_condition`.
- Queue items with `start_frequency: never` start from a launcher, resource center, link, API or
  another item. List their count in one line; keep their ids, because Step 3 may need to name them.
- **Banners, in scope** = published in this environment. Do not require `start_frequency`.
- **Popup announcements, in scope** = level `modal`, `toast` or `popout`, published in this
  environment. Drop `silent` and `badge` and say how many were resource-center only, **except** when
  `draft_dirty` is true: the level you read is the draft's, and the live one may be a popup. Keep
  those in scope marked "level unverified".
- Empty `flow_envs` means not published in this environment; exclude it.
- Conditions come from the **draft**. Flag every item with `draft_dirty: true`, because what's live
  may differ from what you read, and publishing a fix would also ship those other edits. No MCP call
  returns the published version's conditions.

## Step 3: Decode every condition

Read every condition in full, whatever its shape, and turn each item into a short **profile** a
non-technical person can read:

- **Who:** the audience after combining start, filter and hide conditions
- **Where:** pages, or "every page"; element rules ("when a *Settings* button is on the page")
- **When:** what triggers it (on page load, after an event, after another flow, after a delay)
- **How often:** frequency, limit, gap between repeats, per user or per company
- **Started by:** auto-start, another item (name it), or both

How stored conditions are shaped:
- Conditions are a tree: `{"type": "clause", "operator": "and" | "or", "conditions": [...]}`, and
  clauses can nest. Read every branch. An `or` widens the audience; an `and` narrows it.
- Leaves use the Builder's field names, not the predicate DSL: `attribute_name`, `operator`,
  `value`, `data_type` for attributes; `event_name`, `event_*` keys and an optional
  `where_condition` for events; `segment_id` for segments; `type: "page"`, `operator: "url"` with
  `url_pattern: {includes, excludes}` for pages; `type: "element"` with a `selector` (`type:
  "manual"` plus visible `text` or `css`) and `element_state` (for example `present`) for elements.
- The Builder also offers rules on another flow or checklist, text typed into an input, any input
  being filled in, the current time (scheduling) and a wait before starting. Expect leaves for those
  too, and decode them from their keys.

Decoding reference (not exhaustive):
- Datetime attributes: `relative_gt N` = within the last N days; `relative_lt N` = more than N days
  ago. Values may be stored as strings (`"30"`).
- Events: `event_frequency_operator: eq` with `event_frequency_value: 0` (or a `not_event`) = has
  never done it; `gte` / `lte` N = at least / at most N times. A `where_condition` narrows which
  events count; an `event/flow_id` value is a flow id, so name the flow (from your `list_flows`
  result, including items that aren't in scope). `event_time_operator: relative_gt` with
  `event_relative_value` N and `event_relative_unit` = within the last N units; `relative_lt` = more
  than N units ago; `any` = at any time. Use the stored unit (seconds, minutes, hours, days).
- `event_actor`: `current_user` = this user's events; `current_group` = anyone at their company.
- Segment ids → segment names from `list_segments`.
- URL rules → "on the /billing page", or "on every page" when there's no URL rule. How patterns
  match:
  - Parts of the URL left out of a pattern match anything. A domain-only pattern means every page
    on that domain.
  - A path with no `*` matches that exact path only. `/` is the home page only, and `/app` does not
    match `/app/projects`.
  - `/app*` matches `/app` and anything starting with it (including `/applications`). `/app/*`
    matches only pages under `/app/`.
  - `:name` matches exactly one path segment or subdomain.
  - Query parameters in a pattern must all be present with those values. Extra parameters are
    ignored, and `*` matches any value.
  - A page must match at least one include and no exclude.

**When you meet something you can't decode** (an unknown type, key or operator), quote it as stored
in the profile ("rule: `<key>` `<operator>` `<value>`"), don't guess what it means, and lower the
confidence of any finding that depends on it.

If the user picked an audience, mark each item **Targets this audience** (its condition requires the
audience), **Reaches this audience** (no audience rule, but the audience saw it in the window), or
**No reach** (neither).

## Step 4: Pull reach and completion

Use `query_flow_metrics` with all in-scope ids, `env_id`, `last_n_days: 30`,
`sort_by: "unique_views"`. The audience filter is `predicates`. `subject_predicates` is dropped on
this tool and would silently count everyone.
- Once without predicates → all users: unique views, views, and `unique_completion_rate` (a
  fraction: multiply by 100 and show it as "completion rate").
- Once with the audience as `predicates` (if an audience was chosen) → audience reach.

Announcements come back with `views`, `reactions` and `comments` only: no unique users and no
completion. Report their reach as "N views" and leave completion blank.

Completion rate is the share of sessions that reached a goal step. Closing a flow does not complete
it. A one-step flow with no goal step stays near 0% even when everyone sees it and closes it. Do not
read that 0% as "nobody finished" and do not read a high rate on a one-step goal as "they did the
task".

## Step 5: Find what users actually experience

Look at the whole set, not item by item. Use all four checks (A–D); each catches things the others miss.

### A. What can collide (from the profiles)
Two items **can collide** unless their profiles prove they can't reach the same user at the same
moment: pages that can't match the same URL, audience rules that can't both be true, triggers that
exclude each other. When you can't prove it, treat them as overlapping and say why.

- **Everywhere items:** a queue item with no page rule and a broad audience overlaps almost
  everything. List these separately as "everywhere items" and say they can start on top of any
  group. Don't use them to merge other items into one giant group.
- **Flows and checklists that can start together:** two or more of the remaining flows or checklists
  that can start for the same user on the same page. Group them into **overlap groups** of two or
  more items, and show each group once. An item that overlaps with several groups goes in its
  largest group; name the others in the tracker's Notes ("also overlaps with group 3"). An item that collides with nothing (or only with everywhere items) has no
  group ("—"); never make a group of one.
- **Chains:** an item that another item starts (Step 3, "Started by") isn't a collision with its
  parent. It is a sequence. Show it as "follows <parent>" on the parent's group, not as a rival.
- **On screen together:** a banner or popup announcement that overlaps a queue item. Put it in an
  "on screen together" note on that group, not in the queue order.
- **Banners in a row:** two or more banners that can match the same user on the same page. State
  which shows first and that the next one appears once it's dismissed.
- For each group, state the real start order (unseen first, then seen longest ago, then priority,
  then created first). Only call out a priority tie when the first three keys match.
- For more than ~40 in-scope items, put the profiles in a compact table and compare them with a
  script (page patterns and audience keys), then reason about the pairs it flags. If you can't run
  code, group the items by page rule first, then compare audiences within each group.

### B. What users actually saw (from event data)
This confirms or rules out the overlaps from check A, whatever the conditions look like. It works
from real users' event timelines.
1. **Find the users who got the most.** `list_users` with `env_id`, `order_by: "last_seen_at"`,
   `order_dir: "desc"`, `limit: 5` (each row carries all of the user's attributes, so rows can be
   large) and one predicate, run once per event:
   `{"type": "event", "event_name": "flow_started", "frequency_op": "gte", "count": 3,
   "within_days": 30}`, and the same with `checklist_started` (checklists log their own event). Lower
   `count` to 2 if nobody matches.
2. **Read their timelines.** `get_user_events` (`user_id`, `env_id`, `limit: 100`) for 3–5 of them.
   A busy user's timeline can be too large to read inline; if it's saved to a file, parse it with a
   script, or if you can't run code, use `limit: 50`.
   Events come newest first. Each `flow_started` has `attributes.flow_id`, `flow_name`,
   `flow_start_reason` and `page_url`. Each `checklist_started` has `attributes.checklist_id`,
   `checklist_name` and `checklist_start_reason`. `flow_ended` has `flow_end_reason` (for example
   `user_closed`). A start reason of `start_condition` is an auto-start; other values (for example
   `userflowjs`) were started by code, a link or another item.
3. **Rebuild what each user went through:** which items auto-started, on which page, in what order,
   how many seconds or minutes apart, and how each ended. Two auto-starts minutes apart, or a popup
   while a flow was open, is overload you can show the customer. Refer to these people as User A,
   User B… with their plan or role and signup date; never show their name, email or company in
   chat or in the tracker.

Don't use `list_users` to count users who saw two specific items. Its event predicates ignore both
`flow_id` and a `where_predicates` filter on `event/flow_id`, so every count comes back as "anyone
who started any flow".

Leave out internal and test users: company email domains, emails or names that look like test or
demo accounts (for example "test" in them, or `example.com` domains), `localhost` pages, and
`page_url`s on `app.userflow.com` (Builder previews). Say how many you left out. If every match is
left out, don't lower `count` to find more: report that no real user had more than one start. Check
B then has nothing to add, which is itself a finding. Never make up numbers.

### C. Walk through typical users
Pick 2–4 typical users from the account's real segments and attributes (for example a signup from
today, a trial user, a paying customer of a year). If the segments look like test data, build the
users from the attributes the items' rules actually use. For each, walk through their first visits on the
main pages: "On /app they get X. When it closes, Y starts at once because nothing makes it wait,
while banner Z is already on screen." This catches overload that no rule predicts.

### D. Anything that looks wrong
Look for anything that doesn't make sense for its purpose. Examples only; don't stop at these:
- a condition that can never be true now (a date cutoff in the past, contradictory rules, a value no
  user has, a single named user or email)
- a value that looks mistyped or truncated next to what segments use (`enterprise-` vs `enterprise`)
- a name that contradicts its audience ("Onboarding" sent to year-old accounts)
- repeats with no gap or limit (`always`; `multiple` with no `start_limit`, no interval, or an
  interval under a day)
- popups and banners for everyone on every page
- dated or finished content (a past launch, an old promo, a closed experiment)
- test-like leftovers (test names, localhost or example pages)

For an item with 0 views, check whether anyone can match it before calling it dead: `list_users`
with its key audience rule as `predicates` (`limit: 1`), and read `total_count`. When reach
contradicts the rules (for example a popup for everyone on every page with 0 views while users were
active), report the mismatch as a finding. Don't explain it away. Reach you can't trust can't support
a Retire either, so such items go to Review.

**Idle environment.** If `list_users` with `last_seen_at` within the audit window finds no active
users, every item will show 0 views and 0 reach for the wrong reason. Say that reach is
uninformative here, send every would-be Retire to Review (except an audience of a single named
user or email), finish the audit, and offer a longer window or another environment at Checkpoint 1.

**Before calling anything dead or stale, check `first_published_at`.** An item published inside the
window has partial data: suggest Keep and a re-check, not Retire. The exception is an audience of a
single named user or email. It is dead whatever the data says, and this exception overrides every
other Retire rule, including the window.

## Step 6: Work out each item's purpose, then decide

**Work out the intent first.** For every item you'd change, ask what its author was trying to do,
using its name, labels, conditions, what starts it and what it starts. Read its steps
(`get_flow_details` with `include_steps: true`, `include_content: false`) when the purpose or a
start_flow action matters. Usually deliberate, so don't "fix" them without a reason specific to the
item:
- follow-ups that start after another flow (a chain)
- sequences and onboarding programs
- recurring surveys with a long gap between repeats
- per-company frequency, date-boxed campaigns

**Never propose a change that breaks a purpose.** The interruption guard on a follow-up delays it by
the guard's length, or stops it if the user leaves first. If a chain causes the overload, propose
lengthening the delay in its trigger rule (done in the Builder) or put it in Review. Don't add a
guard.

**Make sure the change fixes the cause.** For example, 8 views per user on a `once` flow is not
fixed by a guard. Check `restart_enabled` and the user timelines first.

Give each item one action and a **confidence**. Confidence is how sure you are that the problem is
real and that the change helps. It is not how important the item is, or whether it looks like test
content.
- **High:** the problem follows directly from settings you read on an item with no unpublished draft
  edits, or from clear data, and no plausible purpose needs it. A checklist that restarts every
  second, `multiple` with no start limit, and an audience of one named email are High.
- **Medium:** likely, but something is unverified: unpublished draft edits on the item, an undecoded
  rule, a purpose you can't rule out, or partial data (published inside the window). Partial data
  only lowers findings that rest on data (reach, dead, stale). A problem you read straight from the
  settings, like a 1-second repeat, stays High however recently the item was published.
- **Low:** a guess.

Don't lower confidence just because an item is a near-copy or has a test-like name. Judge the
setting itself. An item can have a clear setting problem and also be a copy: give the Fix for the
setting, and note the copy in Notes for the team.

Decide every item's action and confidence before Checkpoint 1, because the summary counts them.

Which confidence each action needs:
- **Fix** and **Retire** need **High**. If a Fix or Retire would be right but confidence is Medium
  or Low, use **Review** and say what would settle it.
- **Keep** can be any confidence (for example Keep / Medium for an item with partial data).
- **Review** is for items below High that would otherwise be Fix or Retire, and for decisions only
  the team can make.

Actions:
- **Fix:** Name the smallest change that improves what users see
  without breaking the purpose, and say the trade-off. Examples (illustrations, not a menu):
  - "Set interruption guard to 1 day" (`throttle_value: 1`, `throttle_unit: "day"`) on an
    independent queue item that collides with others. Say that it waits on the last flow, not on a
    checklist or banner. Put it on the items that would start *after* another flow, not on the one
    that starts first: the first one has nothing before it to wait on, so a guard there doesn't stop
    the pile-up.
  - "This tour is unseen, so it starts before the higher-priority survey the user has already seen"
    (quote the real order, not "raise priority" alone, unless priority is the key that is tied)
  - "Change frequency from always to once" (done in the Builder when the item has a page or element
    rule; see Step 8); "Set a start limit" when `multiple` has none
  - "Limit to the /reports page" (done in the Builder; see Step 8)
  - "Correct `plan` value `enterprise-` to `enterprise`"
  - For two banners on the same page for the same people: "Raise the one you want shown first"
    (`priority`). The other shows only after the first is dismissed, so if users shouldn't get both,
    narrow one banner's audience or pages, or retire it
- **Retire** (unpublish): with evidence that it is dead, stale or finished. A test-like name alone
  is not enough. It also needs negligible reach and a first publish before the window. An audience
  of a single named user or email is the exception: it is dead regardless (see Step 5).
- **Review:** a Fix or Retire below High confidence, which one of a pair of near-copies to keep
  (settings that match don't prove the content matches; let the team pick), chains that look like
  overload, and items with an unclear owner or purpose. Say what the team needs to decide.
- **Keep:** working as intended.

✋ **Checkpoint 1.** Only once the whole audit is done (see the top of this skill). Show a short
summary in chat, then wait for the user to say go on before building the tracker:
- How many items start or show on their own, split into flows and checklists that start on their own, banners, and popup
  announcements, and how many of them you checked (all of them, unless you said why not)
- How many groups of items can reach the same user at the same moment (groups of two or more), and
  the top 3 problems ranked by users affected
- One typical-user walkthrough (Step 5, check C), in three or four lines
- Counts by suggested action, with how many are High confidence
- Caveats (see below)

## Step 7: Build the decision tracker

Columns, in this order:
1. Item name, Type, Category (Targets / Reaches / No reach, if an audience was chosen)
2. How it shows (Starts on its own / Banner / Popup announcement), Auto-start rule (the plain-English profile), Frequency, Interruption guard ("none" or "1 day", never raw values like "0 minute"; "n/a" for banners and announcements), Priority, Overlap group (from Step 5; "—" when none)
3. Users reached (30d; "N views" for announcements), Audience reached (30d, if chosen), Completion rate (blank for banners and announcements)
4. First published, Last published by, Unpublished draft changes (Yes/No)
5. Suggested action, Confidence, Exact fix, Why (the evidence)
6. **Decision**, **Owner**, **Decision date**, **Applied in Userflow?** (No / Draft only / Live;
   default "No"), **Notes**
7. Item id, Builder link from **Builder links**

Sort by overlap group, then by users reached, descending. If a rule names a person's email, keep
it (the team needs it), and mention that the file contains it.

Deliver it where you agreed in "Before you start"; don't ask again:
- **Spreadsheet connector agreed:** create the sheet there. Add dropdowns on Decision (Keep / Fix /
  Retire / Review) and Applied (No / Draft only / Live) if the tool supports data validation,
  freeze the header row, and add a Summary tab with counts by suggested action and by decision. If
  any call fails (for example an admin turned the tool off), say so in one line and create the file
  below straight away.
- **No spreadsheet connector:** create a CSV (or .xlsx) file if you can create files, otherwise give
  the CSV text in chat. Say that dropdowns need to be added by hand, and give the Summary counts
  (by suggested action) in chat, since a CSV has no second tab.
- Always also show the top of the table in chat.

## Step 8: Apply the fixes (only after a yes)

For a viewer, skip Checkpoint 2 and this step: end with the list of changes for an editor to apply.

✋ **Checkpoint 2.** Ask which changes to apply. Accept "all Fix items", "all Retire items", a list,
or none, and only offer the groups that exist (if there are no Fix items, don't offer "all Fix
items"). If the user picks a Review item or a change that touches a chain, say what it could break
before going on. Say plainly which changes are draft-only (Fix: nothing changes for end users
until someone publishes) and which are live at once (Retire: unpublishing stops the item for
end users immediately). Before
writing anything, repeat the exact list of changes back and get a yes. Then:

- **Setting changes** (guard, priority, frequency, limits, gaps): for each item, call
  `get_flow_details` immediately before editing and take the **top-level** `edited_at` (not one
  from `draft`, not the one from `list_flows`). Call `update_flow` with that as
  `expected_edited_at` and only the fields that change. These edits change the **draft only**.
  Send `throttle_value` and `throttle_unit` together. Send `start_limit` as an integer of at least 1.
  Guard, priority, limit and gap changes can be sent on their own. **A change to `start_frequency`
  cannot:** an auto-starting frequency (`once`, `once_per_group`, `multiple`, `always`) must be sent
  together with `start_condition`, which means re-sending the whole existing condition. So a
  frequency change on an item whose start condition has any rule the predicate DSL can't express is
  a Builder hand-off (see the next point). Know this before Checkpoint 2, and mark those items "in
  the Builder" in the list you repeat back.
- **Condition and URL changes:** the predicate DSL covers only attribute, `event` and `not_event`
  rules (and clauses of them). It has no page, URL, element, segment, other-flow, input, scheduling
  or wait rule, and no event property filter (`where_condition`). If the item's start condition
  contains any of those, or the fix is a URL rule, don't rewrite it with `update_flow`: sending a
  new `start_condition` would drop those rules. Give the user the Builder link and the exact change
  to make there. Other condition fixes can go through `update_flow` with the predicate DSL
  (`read_resource` "predicate-dsl"); at Checkpoint 2 show the rebuilt condition next to the
  original so the user can see nothing was lost. Banner and announcement audiences live on
  `filter_condition`. The same warning applies there.
- **Publishing a fixed item** happens only if the user asks for it explicitly. Use
  `set_flow_publication` with `action: "publish"`, the chosen `env_id` and the item's top-level `edited_at`
  as `expected_edited_at`; call it without
  `confirm` first, show the impact summary it returns, and pass `confirm: true` only after the user
  approves. Warn again if the item had `draft_dirty: true` before your edit.
- **Retire** = `set_flow_publication` with `action: "unpublish"`, same consent pattern (first call
  without `confirm`, show the impact, confirm only after yes). Unpublishing does not need
  `edited_at`. Unpublishing is not deletion; the item and its analytics stay. If the item has
  unpublished draft changes, say that republishing it later would ship them.
- If a `stale_flow` error comes back, someone edited the item in the Builder. Re-read it, re-apply
  the change on top, and tell the user.

For the Fix items you changed, tell the user: "These items now have unpublished changes. They go
live when someone publishes them, and whoever publishes next will ship these changes too." Set their
**Applied in Userflow?** to "Draft only" if you can write to the tracker. For Retire items you
unpublished, tell the user they are **no longer shown to end users, as of now**, and set Applied to
"Live". For items handed to the
Builder, leave Applied as "No" and add "Handed to Builder" in Notes. Finish with a short list of what
changed and what was handed off, with Builder links.

## Caveats to always state
- Audience reach uses each user's attributes **today**, not at the time they saw the item.
- Settings were read from drafts; items with unpublished draft changes are flagged, and an
  announcement's popup level may differ from what's live.
- Completion rate counts sessions that reached a goal step. A one-step flow with no goal step shows
  about 0% just for being shown and closed. Announcements have views only.
- Flows and checklists start in this order: one the user hasn't seen, then the one seen longest
  ago, then priority, then created first. Banners and popup announcements don't wait their turn;
  they can be on screen with a flow. Only one banner
  shows per page at a time; the next appears after the first is dismissed.
- The interruption guard only looks at previous flows.
- What users actually saw comes from the event timelines of N users, or was skipped and why.

## Writing style
Plain, direct sentences. Use the customer's own item names. No jargon like "predicate", "FQN" or
"throttle" in anything the user reads; say "rule", "attribute", "audience", "interruption guard".
Don't use this skill's own step names either ("inventory", "collision analysis", "lens", "profile",
"queue", "in scope", "Checkpoint 1", "Step 5"): say what you did, for example "checked all 217 items that start or show on their own" or
"found 6 groups of items that can show to the same user at the same moment".
Every finding says what you saw, not only what you concluded.
