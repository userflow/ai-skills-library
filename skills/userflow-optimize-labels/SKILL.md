---
name: userflow-optimize-labels
description: Organize a Userflow account with labels so the team can see what is live, who it is for and what it is meant to do. Builds a simple label taxonomy if there isn't one, finds published flows, checklists, launchers, banners, announcements, resource centers and Adoption Agents that are unlabeled or only partly labeled, proposes labels for each, applies them after approval, and returns a bird's-eye overview of everything deployed to end users. Use this whenever someone with the Userflow MCP connected says their account is "messy", "disorganized", "we can't find anything", "too many flows to maintain", asks to "label our flows", "tag our content", "set up a naming convention or taxonomy", "audit labels", "clean up labels", or wants an overview of "what is live" in Userflow. Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow label audit and taxonomy

Accounts grow to dozens or hundreds of items. Without labels nobody can answer "what are we showing
new users?" or "what touches the billing page?", and maintenance turns into guesswork. This skill
gives every published item a small, consistent set of labels and then shows the account at a glance.

Labels in Userflow are shared across flows, charts and dashboards, **label changes go live
immediately** (they aren't part of the draft/publish cycle), and the MCP **can't delete a label**.
Neither label tool asks for confirmation, so this skill always shows its plan and waits for a yes
before creating or applying anything, and creates a label only once an item that uses it is approved.

## Before you start

1. **Userflow MCP.** If its tools aren't available, stop and point the user to
   https://help.userflow.com/docs/mcp.
2. **Account and environment.** Call `describe_session`, tell the user which company you're connected
   to and their role, and pick the environment: suggest the one named like Production, and if
   several names look like production, list them and let the user pick. Labels must be applied by an
   editor or above. A viewer gets Parts A–C as a read-only report plus the Part E overview: skip both
   approvals and Part D, and say an editor must apply the plan.
3. **Does a taxonomy exist?** Call `list_labels` and look for a pattern (for example names that share
   prefixes like `Feature:`, `Stage:`, `Team:`). Match prefixes and label names ignoring case
   everywhere: `feature: reports` has the `Feature:` prefix and is the same label as `Feature: Reports`.
   Show an existing label in its existing spelling, and rename only if the user asks. Also ask once whether the team keeps label rules in a
   doc or sheet. If they share one and a connector for the tool it lives in is available (Google
   Drive, OneDrive, Notion, Confluence…), name it and ask before reading with it; otherwise ask them
   to paste or export it (CSV is fine). Then run Part B steps 1–4 (one `list_flows` call, reused
   everywhere) and decide from the in-scope live items:
   - A taxonomy doc, or prefixed labels with enough values to cover those items → go to Part C.
   - No taxonomy, only a few ad hoc labels, or prefixes with too few values to cover them → Part A
     first, keeping the existing prefixes and labels.

## Part A: Propose a taxonomy (only if there isn't one)

Keep it small. Three dimensions cover almost every team:

| Dimension | Question it answers | Rule | Examples |
|---|---|---|---|
| `Feature:` | Which part of the product does this help with? | Exactly one primary; a second only if it truly drives two | `Feature: Reports`, `Feature: Integrations` |
| `Stage:` | Where in the customer journey does it sit? | Exactly one | `Stage: Onboarding`, `Stage: Adoption`, `Stage: Trial conversion`, `Stage: Retention` |
| `Audience:` | Is it restricted to one plan, role or segment? | Only when targeting restricts it | `Audience: Admins`, `Audience: Enterprise` |

Steps:
1. Propose the **Stage** values from the four examples above, adjusted to how the customer talks
   about their journey.
2. Propose **Feature** values from the customer's product areas. Start from the in-scope live items
   Part B steps 1–4 left (reuse those responses) and any existing labels; read targeting with
   `get_flow_details` only for items whose name doesn't settle it. Propose only as many features as
   the live content supports (usually 4–15), then ask the user to correct the list.
3. Propose **Audience** values only from audiences their targeting actually uses (plans, roles,
   segments found in start or filter conditions).
4. Reuse existing labels wherever one already means the same thing. Note labels that look
   operational (for example "Experiment", "Q3 campaign", "production"); keep them, but outside the
   taxonomy.

✋ **Checkpoint A.** Show the proposed taxonomy as a short table with one-line definitions, marking
which labels already exist and which would be new. This approves the **taxonomy only**: don't create
any label yet. New labels are created in Part D, and only those that approved items use. Offer to save
the taxonomy as a document the team can keep (in a connected docs tool after asking, or as a file).
Tell the user once here that a label, once created, can't be deleted through the MCP (only in the
Userflow dashboard), so approve names you're happy to keep.

## Part B: Find the gaps

1. `list_flows` with `list_all_flow_types: true` and `state: "published"`. Parse large results with a
   script; if you can't run code, keep only each item's id, name, type and labels. Drop `tracker` types, and apply the set-aside rule in step 4 before live-checking. Everything else is in scope, including Adoption Agents
   (`assistant`). `list_flows` isn't scoped to an environment: before calling an item live, confirm
   with `get_flow_details` (`env_id`, `history_limit: 1`, `include_steps: false`) that its
   `flow_envs` entry has a `published_version_id`. Keep that response: Part C reads targeting from
   it and does not call again. Items not live in this environment are skipped and counted as
   "published elsewhere" in the overview. For more than ~40 items, split the ids into batches (use parallel
   sub-agents if your environment supports them) and have each batch return one compact JSON line
   per item, including whether it is live and the targeting fields Part C needs. Without sub-agents,
   go item by item and keep only that one-line record for each, never the raw responses.
2. `list_flows` returns label **names** without ids. Map names to ids with `list_labels`.
3. **Targets** = items with no labels, plus items missing a required dimension (no `Feature:` or no
   `Stage:` label). For partly labeled items you only **add** the missing dimension; never remove
   labels in this part.
4. **Set aside, don't label:** items whose name has a whole word that marks it as scratch or a
   duplicate: `test`, `testing`, `copy`, `copy of`, or `(copy)` (any case). Match those words on
   their own (treat `_`, `-`, brackets and parentheses as word breaks, so `test_onboarding` and
   `[UF Testing]` match). A name that merely
   contains the letters, such as "Latest", "Contest" or "Copywriting", stays in scope. If more than
   ~20% of the non-tracker items match, or the product's own vocabulary uses these words (a testing
   tool, say), ask once before setting them aside, then continue. Items that look like demos for
   prospects (named after another company) also go on the needs-a-decision list. Also set aside items targeted at a single named user or email,
   and items whose purpose can't be told from name and targeting. Put them on a
   **needs-a-decision** list with the reason.

## Part C: Decide labels for each target

Each target already has one `get_flow_details` call from the live check in Part B; read its targeting
from that same response rather than calling again. Say in the report which items were decided from
the name alone (targeting wasn't needed). Work in this order, and record which method decided each
label:
1. **Team rules.** If the taxonomy doc lists a recommendation for the item, use it.
2. **Precedent.** Match already-labeled items in the same series (for example other steps of the
   same onboarding program). A similar name alone isn't precedent: check the content or targeting
   agrees.
3. **Name and targeting.** From the Part B response, read `draft.start_condition` (URL rules for
   flows and checklists are `type: "page"` conditions inside it), `draft.filter_condition` when
   present, and
   `draft.url_pattern` (launchers). These are draft values; if the chosen environment's `flow_envs`
   entry has `draft_dirty: true`, note that the live targeting may differ. Pick:
   - **Feature:** what the content drives.
   - **Stage:** from its audience: new users → Onboarding, trial users → Trial conversion, paying
     users → Adoption, renewal or churn-risk audiences → Retention. Items available to everyone with no restricting audience (Adoption Agents,
     resource centers, untargeted checklists, launchers and announcements) → Adoption, unless their content is
     clearly onboarding. Content started by another flow takes that flow's Stage, and usually its
     Feature: you can spot it as a `start_condition` event condition (for example `flow_step_seen` or
     `flow_completed`) whose `where_condition` has an `event/flow_id` pointing at another flow, or as
     the target of a `start_flow` button action you saw in another item's steps.
   - **Audience:** only when the targeting restricts it to a plan, role or segment. Other filters
     (an email domain, say) get no Audience label; note them.
4. If two Features fit about equally, or none fits, leave the Feature off and put the item on the
   needs-a-decision list. An item can still get its Stage label; record the missing Feature.

Never apply a label the approved taxonomy doesn't contain. If the right label is missing from the
taxonomy, note it and offer to go back to Part A.

✋ **Checkpoint B.** Present the plan grouped by label pattern, not one row per item (unless fewer
than 10), for example: "14 items → Feature: Reports + Stage: Adoption". List which **new labels** the
plan would create (only those the plan uses). Show the needs-a-decision list separately. Say plainly
that labels go live immediately (they aren't part of draft and publish) and that new labels can't be
deleted through the MCP. Ask the user to approve all, approve some, or edit. After edits, show the changed groups and the new-label list
again and wait for a yes.

## Part D: Apply

1. **Create each new label right before the first batch that uses it**, and only labels approved items
   use: `create_or_update_label` with the name. If a created label ends up on 0 items (a batch failed
   or the user stopped), say so and name it for deletion in the dashboard. A successful create nests the id at `label.id`. Names are unique ignoring case. If one
   already exists, the call fails with `duplicate_name` and the id is `existing_label.id` — not
   `label.id`, and not a top-level `label_id`. Use `existing_label.id` and do not create another.
   Don't rename existing labels unless the user asked for it; a rename shows everywhere the label is used.
2. `apply_labels` with `target_type: "flow"` for every item type (launchers, checklists, banners,
   announcements, resource centers and Adoption Agents are all flows here).
- **Batching:** max 50 items and max **50 label ids in total** per call. Items per call = 50 ÷ labels
  per item, rounded down (2 labels → 25 items, 3 labels → 16). Batch by Checkpoint B group.
- The call is atomic: on `label_not_found` or `target_not_found` nothing is written. Remove or fix the
  bad id and resend; re-sending is safe.
- Report from the result rows (`target_id` plus `added_label_ids` changed, `unchanged_label_ids` were
  already there), mapped back to item names. Don't describe what you sent; describe what the rows say.

## Part E: Verify and give the overview

1. Re-run `list_flows` (published, all types) and confirm every approved item now has its labels.
   List items that still lack a Feature or a Stage, and why.
2. Give the **bird's-eye overview**: a matrix of live items by Feature × Stage (counts; set-aside
   items weren't live-checked, so count them separately), plus:
   - Features with no live content at all (possible gaps)
   - Stages with a lot of content that shows on its own (possible overload). For flows and checklists,
     that means `draft.start_frequency` other than `never` and a `start_condition`. Also count published
     banners (they show from `filter_condition`, even when frequency is `never`) and announcements whose
     `draft.announcement.level` is `modal`, `toast` or `popout`. Suggest the `userflow-optimize-autostart`
     skill if it's installed. That skill has the rules for what shares a slot and what shows at the same time.
   - The needs-a-decision list with reasons
   If you can create visual artifacts, render the matrix as a simple dashboard; otherwise a table in
   chat is enough. Offer a CSV: write a file if you can create files, otherwise give the CSV text.
3. Optional hygiene notes (report only, change nothing): labels used on 0 items, near-duplicate label
   names, labels outside the taxonomy. Before calling a label unused, check flows in every state
   (`list_flows` with the `label` filter and no `state`, plus `state: "archived"`) and dashboards
   (`list_dashboards`, `label_names`). `list_charts` doesn't return labels, so say chart use can't be
   checked here and should be confirmed in the dashboard. Deleting a label is done in the Userflow dashboard; the MCP can't
   delete labels.

## Ongoing use

Suggest running Part B–E monthly or after a big launch. New items created by other Userflow skills
(for example reactive flows or adoption nudges) should get labels from the same taxonomy.

## Writing style
Plain language. Say "label", "rule", "audience". Keep tables short and grouped.
