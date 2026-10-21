# Userflow MCP reference — per-segment metrics

How to pull a single content item's metrics for each segment. Read the live `predicate-dsl` resource
for the full predicate spec; this file captures the comparison-specific decisions.

## Primary tool: `query_flow_metrics`

One call per segment, scoped by that segment's predicates, on the single content id. It works for
**any** flow type (guide flow, announcement, banner, checklist, launcher, resource center, embed,
etc.), and returns totals + a time series.

```
query_flow_metrics(
  flows: ["<content-id>"],
  predicates: [ <segment predicates> ],
  include_time_series: true,
  interval: "week",        // day | week | month
  last_n_days: 90,         // or start_date + end_date (ISO 8601)
  env_id: "<env>"
)
```

Response shape (confirmed):

```json
{
  "items": [{
    "metrics": { "views": 79, "unique_views": 79, "completions": 79,
                 "unique_completions": 79, "completion_rate": 1.0, "unique_completion_rate": 1.0 },
    "flow": { "id": "...", "name": "...", "type": "flow" },
    "time_data": [ { "t": "2026-07-06T00:00:00Z", "views": 10, "completions": 10 }, ... ]
  }],
  "warnings": []
}
```

- `metrics` → the comparison-table row for that segment.
- `time_data` → the trend series for that segment (align the `t` buckets across segments for the
  charts).

## Metric set by content type (adaptive)

Works for **any** flow type. Don't hardcode two cases — **read the `metrics` keys actually returned**
for the chosen content and pick 3–4 meaningful ones. Use this as guidance for what to lead with:

| Content type | Lead with (use what's returned) |
|--------------|---------------------------------|
| **flow** (guide) | Views, Unique Views, Completions, Completion Rate |
| **announcement** | Views, Reactions, Comments |
| **banner** | Views (seen), Dismissals |
| **checklist** | Started, Completions, Completion Rate |
| **launcher** | Views (seen), Activations |
| **resource_center** | Opens / Views |
| **embed** | Views (seen), Dismissals |
| **assistant / tracker / other** | Whatever engagement metrics the response carries |

Rules of thumb:
- **Completion-type content** (guide flows, checklists) → lead with a completion **rate** plus the raw
  counts.
- **Seen/engagement-type content** (announcements, banners, launchers, embeds, resource centers) →
  lead with **views** and the type's primary engagement metric (reactions/comments, dismissals,
  activations, opens).
- If a type returns only the universal fields, fall back to **Views** and **Completions** from
  `time_data`. The `time_data` series (`{ t, views, completions }`) is available regardless of type, so
  trends always work.

**Prefer `query_flow_metrics` for every type** (it scopes cleanly by predicate). `get_flow_summary`
can under-report announcements, so don't lean on it for the headline numbers.

## Scoping (user-actor predicates)

`query_flow_metrics` predicates are **user-scoped**. That means:

- **Existing segments** referenced as `{ "type": "segment", "segment_id": "<uuid>" }` must be **user**
  segments (`list_segments` with `subject_type: "user"`). Manual, condition, "all", and integration
  user segments are all fine to reference.
- **Ad-hoc filters** use `attribute` / `event` / `not_event` / `clause` predicates. User attributes use
  the bare name (`email`, `last_seen_at`); company attributes use the `group/` prefix and are evaluated
  against each user's company (so "EU companies" → `group/region = eu`); company-membership uses
  `group_membership/`.
- You **cannot** pass a *company* segment id here. Re-express the intent as user predicates instead.

Operators by data type: string → `eq, ne, contains, starts_with, ends_with`; number →
`eq, ne, gt, gte, lt, lte`; boolean → `eq, ne`; datetime → comparisons plus `within_days` /
`older_than_days`. Mind data types (string `"true"` ≠ boolean `true`).

## Zero / thin data

A segment can legitimately return all-zero `metrics` and a flat `time_data`. Don't present that as a
finding — label it (e.g. "no eligible users / no activity in window"). Small segments produce noisy
rates; note low sample sizes so a 100% completion on 2 views isn't mistaken for a win.

## Optional: step-funnel detail (guide flows only)

If the user wants per-step drop-off per segment, additionally call
`get_flow_summary(flow_id, predicates: [<segment>], env_id)` for guide flows — it returns the step
funnel and worst drop-off. Not needed for the core table + trends, and not reliable for announcements.
