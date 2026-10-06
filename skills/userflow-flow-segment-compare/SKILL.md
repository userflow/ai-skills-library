---
name: userflow-flow-segment-compare
description: Compare how a single piece of Userflow content performs across several audience segments, rendered as a dashboard — a key-metrics comparison table plus trend charts. Works for ANY Userflow flow type (guide flows, announcements, banners, checklists, launchers, resource centers, embeds), not just flows and announcements. Content is chosen from a searchable dropdown; the "segments" are whatever the user wants to compare — existing account segments, ad-hoc filters built just for this analysis, or a mix — and ad-hoc ones are never saved to the account. Use whenever a user with the Userflow MCP connected wants to "compare a flow/announcement/banner across segments", "how does [content] perform for [group A] vs [group B]", "break down [content] by audience/user type", or any per-audience performance breakdown of one piece of content. Different from userflow-flow-compare (two flows head-to-head) — here it's ONE piece of content across MANY audiences. Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow Content × Segment Compare

Take **one** piece of Userflow content — any flow type — and show how it performs across **several
audiences**, ending in a dashboard: a **comparison table** of key metrics and **trend charts** of
those metrics, one line per segment. Conversational and step-by-step — **pause at each ✋ checkpoint**.

Hold onto three things:
- **Any content type.** Guide flows, announcements, banners, checklists, launchers, resource centers,
  assistants, trackers, embeds — all are "flows" with a `type` in Userflow. The metrics adapt to the
  type (see `references/mcp-metrics.md`).
- **"Segment" is loose.** A real account segment, or an ad-hoc filter the user describes just for this
  comparison. **Never create ad-hoc segments on the account** — they're query-time predicates only.
- **Read-only.** This skill only reads analytics; it writes nothing to Userflow.

## Before you start

1. Confirm the **Userflow MCP** is connected. If not, say so and stop.
2. Resolve the **environment** via `describe_session` (default to **Production** for analytics unless
   told otherwise); pass its `env_id` on every analytics call.

---

## Phase 1 — Pick the content (searchable dropdown)

Don't make the user type an exact name. Fetch the content and let them **pick from a searchable
dropdown**.

1. Call `list_flows` broadly — `list_all_flow_types: true`, `state: "published"` (published content is
   what has analytics), ordered by `edited_at` desc. Each item carries `name`, `type`, and `id`.
2. Render a **searchable dropdown picker** as an interactive widget (same pattern as the
   `userflow-flow-compare` picker): a search box plus a filterable list of items, each showing the
   **name** and a **type badge** (Flow / Announcement / Banner / Checklist / …). On selection, the
   widget sends a prompt back to continue (e.g. "Analyze '<name>' [<id>] across segments"). If an
   interactive widget can't render, fall back to a concise text list grouped by type for the user to
   pick from.
3. **Capture the content type** from the chosen item — it decides the metric set. Confirm the resolved
   name + type back to the user.

---

## Phase 2 — Which segments to compare?

Now ask what audiences to compare (aim for 2–5 for a readable dashboard). For **each** one, it's
either:

- **An existing account segment** — call `list_segments` (`subject_type: "user"`) and let the user
  pick (a searchable/multi-select picker works well here too, or a simple list). Reference it as a
  `{ "type": "segment", "segment_id": "<uuid>" }` predicate.
- **An ad-hoc filter** — the user describes it in plain language; you translate it into
  attribute/event predicates. **Resolve real FQNs / event names first** (`list_attribute_definitions`,
  `list_event_definitions`) — never invent them.

A mix of existing + ad-hoc is fine. Collect them all before moving on.

**One real constraint:** these analytics predicates are **user-scoped**, so existing segments you
reference must be **user** segments. A company-level idea (e.g. "EU companies") is still fine — express
it as a user predicate on a company attribute (`group/region = eu`); just don't pass a *company*
segment id. See `references/mcp-metrics.md` → *Scoping*.

---

## Phase 3 — Review the segments (before pulling any data)

✋ Show the assembled comparison set as a **readable card** (not JSON):

- The **content** being analyzed (name + type)
- Each **segment**: its label, and either "existing segment" or the ad-hoc conditions in plain English
  (Field · Operator · Value)
- The **time window** and **interval** (propose a default: **last 90 days, weekly**; offer day/week/
  month and a different range)

Ask: "Compare these against **[content]** over **[window]**? I can add, drop, or edit any segment."
Remind them ad-hoc segments won't be saved to the account. Iterate until they're happy.

---

## Phase 4 — Pull the metrics

For **each** segment, call `query_flow_metrics` on the single content id, scoped by that segment's
predicates, with the time series on:

```
query_flow_metrics(
  flows: ["<content-id>"],
  predicates: [ <that segment's predicates> ],
  include_time_series: true,
  interval: "<day|week|month>",
  last_n_days: <n>,          // or start_date/end_date
  env_id: "<env>"
)
```

It returns the segment's `metrics` and a `time_data` array for trends, and works across content types.
**Read the metric keys actually returned and adapt** — completion-type content (guide flows,
checklists) leads with a completion rate; seen/engagement-type content (announcements, banners,
launchers, embeds, resource centers) leads with views and its primary engagement metric. See
`references/mcp-metrics.md` for the per-type guidance and zero-data handling. Collect one result per
segment.

---

## Phase 5 — Build the dashboard

Produce a **self-contained HTML dashboard** (a file artifact). Before writing HTML, read
**`userflow-brand-visuals`** and **`frontend-design`** so it's on-brand. Follow
`references/dashboard-spec.md`. At minimum:

1. **Header** — content name, type, time window, and the segments compared.
2. **Comparison table** — one row per segment, columns = the key metrics for this content type (chosen
   from what `query_flow_metrics` returned). Make the best/worst per column easy to spot.
3. **Trend charts** — for each key metric, one multi-series line chart with **one line per segment**
   over the shared time buckets.

Flag any low-sample or zero-data segment so a flat line isn't misread. Save to
`/mnt/user-data/outputs/` and present it, then offer to iterate (add/drop a segment, change window or
metrics).

---

## Guardrails

- **Never create segments on the account.** Ad-hoc filters are query-time predicates only — say so
  when reviewing them.
- **Never invent** attribute FQNs / event names / values — look them up and echo audiences back.
- **Match metrics to content type** — adapt to the returned metric keys; don't show completion rate for
  a banner or reactions for a guide flow.
- **Don't mislead on thin data.** Flag low-sample or zero-data segments.
- **Read-only** — never publishes or writes anything.
- Keep it light; the dashboard is the deliverable, not a lecture.
