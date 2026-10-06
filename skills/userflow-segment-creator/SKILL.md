---
name: userflow-segment-creator
description: Create a condition (filter-based) segment in Userflow through a guided, conversational flow — pick user vs. company, describe the audience in plain language, translate it into real attribute/event predicates (looked up, never invented), show the conditions in a simple inline card for confirmation, name it, and create it via the Userflow MCP. Use this whenever a user with the Userflow MCP connected wants to "create a segment", "build an audience", "make a user/company segment", "segment users who…", "define a group of users/companies by conditions", or filter their audience by attributes or behavior. Requires the Userflow MCP connector. Note — the MCP only creates condition segments; manual/list (CSV-uploaded) segments are not supported and must be imported from the Userflow dashboard.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow Segment Creator

Guide the user from a plain-language audience description to a live **condition segment** in Userflow.
This is a **conversational, step-by-step** skill: move through the phases in order and **pause at each
✋ checkpoint**. Never create the segment until the user has seen the conditions and said yes.

## Scope (read first)

The Userflow MCP's `create_or_update_segment` creates **condition (filter) segments only** — segments
defined by attribute/event rules that evaluate membership automatically. It **cannot** create
**manual/list segments** (a fixed set of users uploaded from a file); there is no MCP tool to import
members or set attributes. If the user wants a manual/CSV-based segment, say so plainly and point them
to the Userflow dashboard's CSV import (or the REST Identify API) — then offer to help with a condition
segment instead. Don't try to fake it with a giant list of OR'd equals; that hits the nesting budget
and isn't what they want.

## Before you start

Confirm the **Userflow MCP** is connected (its tools are available). If not, tell the user this skill
needs the Userflow connector and stop. Segments are account-level, so no environment needs to be
chosen to create one (an optional match-count preview later is per-environment — handle that then).

---

## Phase 1 — User or company segment?

Ask up front, because it decides which attributes are even valid:

> "Is this a **user** segment or a **company** segment?"

This sets `subject_type` (`"user"` or `"company"`) and constrains predicates — see
`references/mcp-reference.md` → *Subject-type scoping*. In short: a **company** segment can only use
company attributes (`group/…`); a **user** segment can use user attributes, company attributes, and
company-membership attributes.

---

## Phase 2 — Describe the conditions

Ask the user to describe the audience in plain language:

> "Describe who should be in it — e.g. 'companies on an active subscription in the EU', or 'users who
> haven't completed onboarding and were last seen over 30 days ago'."

Then translate it into predicates. **Resolve real identifiers first — never invent them:**

- `list_attribute_definitions` (scope matching the subject type) → exact attribute FQNs and their
  `data_type`. Company attributes use the `group/` prefix.
- `list_event_definitions` → valid `event_name` values, if the description involves behavior.
- Build the predicate array per `references/mcp-reference.md` → *Building the conditions*.

Two things that silently break segments, so get them right:
- **Data types.** String `"true"` ≠ boolean `true`; a number stored as text won't match a numeric
  comparison. Match the attribute's real `data_type`.
- **No nested segment references.** `create_or_update_segment` rejects `type: "segment"` predicates
  anywhere in the tree. If the user says "everyone in segment X plus …", you can't nest X — expand the
  intent into attribute/event rules, or tell them that part can't be combined this way.

If the description is ambiguous ("active" = subscribed, or recently seen?), ask one short clarifying
question rather than guessing.

---

## Phase 3 — Show the conditions and confirm

✋ Render the conditions as a **simple, human-readable card** so the user can eyeball them before
anything is created. Use `visualize:show_widget` for a compact card if available; otherwise a clean
text table is fine. The card should show:

- **Subject type** (User segment / Company segment)
- A **plain-English restatement** ("Companies with an active subscription AND region = EU")
- The **conditions in readable form** — one row per rule as **Field · Operator · Value**, using the
  attribute's friendly **display name** (e.g. "Subscription State", "Page Viewed"), a plain operator
  ("is", "is not", "fewer than", "more than", "in the last 30 days"), and the actual value — grouped
  by AND / OR. For event rules, spell out the count, window, and actor in words (e.g. "fewer than 10
  times, across all team members, in the last 30 days").

**Do not show raw predicate JSON to the user.** The JSON is what you send to the tool, not what the
user reviews — a table of Field / Operator / Value is far easier to sanity-check and is what catches
wrong data types or values. Keep the JSON to yourself.

Then ask:

> "Does this match who you have in mind? I can adjust any rule."

Iterate until they're happy. Small edits are cheap — re-render the card each time.

**Optional match preview.** Offering a rough count helps them trust the filter. If they want it, run a
read-only `list_users` (or `list_companies`) with the same predicates in their chosen environment
(default Production) and report the approximate number of matches. Keep it optional and non-blocking —
skip it if they'd rather just proceed.

---

## Phase 4 — Name it

Once the conditions are confirmed:

> "What should I name this segment?"

Suggest a descriptive default from the conditions if they're unsure (e.g. "Active EU companies").

---

## Phase 5 — Confirm and create

✋ One final check before writing:

> "Ready for me to create the **[User/Company] segment '[name]'** with these conditions?"

On yes, call `create_or_update_segment` with `subject_type`, `name`, and `predicates` (omit
`segment_id` to create new). See `references/mcp-reference.md` → *Creating the segment*.

Report back the created segment (name + id) and that it's now live in their segment list, evaluating
membership automatically. Because it's condition-based, membership updates on its own as users/companies
change — no manual upkeep.

---

## Guardrails

- **Never invent** attribute FQNs, event names, or values — look them up, and echo the audience back in
  plain English before creating.
- **Respect subject-type scoping** — don't put user-scoped attributes on a company segment.
- **No nested segment predicates** — attribute / event / not_event / clauses only.
- **Condition segments only** — if they need a manual/list segment, point them to the dashboard importer
  rather than forcing it.
- **Don't skip the confirmation card.** A segment with a subtly wrong data type matches the wrong people
  (or no one); the eyeball step is the whole point.
- Keep it conversational — you're walking a teammate through it, not making them fill in a form.
