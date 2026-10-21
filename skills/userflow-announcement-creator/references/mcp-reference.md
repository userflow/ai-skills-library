# Userflow MCP reference — announcements

Exact tool calls and JSON shapes for this skill. The running session also has the live Userflow
resources — read `flow-draft-dsl` and `predicate-dsl` via `read_resource` if you need the full
spec. This file captures the specific decisions this skill makes.

## Environment

Most Userflow tools take an optional `env_id`. Resolve it once via `describe_session` and reuse it.
If the user only has one environment, you can often omit `env_id` and the authenticated env is used
— but passing it explicitly avoids ambiguity when multiple environments exist.

## Notification level mapping

The announcement's prominence is the `level` field on `draft.announcement`:

| User-facing term | `level` value | Behavior |
|------------------|---------------|----------|
| Silent | `silent` | No unread badge; only seen when the user opens the Resource Center |
| Badge (default) | `badge` | Unread counter on the Resource Center launcher |
| Boosted → Pop-out | `popout` | Speech bubble from the launcher; moderate attention |
| Boosted → Modal | `modal` | Center-screen overlay, dims background; highest attention |
| Boosted → Notification | `toast` | Slides in from a corner; brief, low-friction |

Optional level-specific fields (only set if the user asks): `toast_auto_dismiss` (seconds),
`toast_width` (200–600), `modal_width` (100–1000).

## Content: rich2 (never HTML)

`draft.announcement.content` (and `more_content`) must be a **rich2** document. Do **not** pass an
HTML string like `"<p>…</p>"`.

```json
{
  "type": "rich2",
  "children": [
    { "type": "heading2", "children": [{ "text": "New dashboard filters" }] },
    { "type": "paragraph", "children": [{ "text": "You can now filter by region and plan." }] }
  ]
}
```

Block types: `paragraph`, `heading1`–`heading3`, `quote`, `ordered-list`, `unordered-list`,
`list-item`, `link`, `button-group`, `button`. Inline marks: `bold`, `italic`, `underline`, `code`,
etc. (`image`/`video` blocks exist but image handling is out of scope for this skill.)

For long copy, you can split with `more_enabled: true` + `more_button_text` + `more_content`.

## Creating the announcement

```json
{
  "name": "New dashboard filters",
  "type": "announcement",
  "env_id": "<env-uuid>",
  "draft": {
    "announcement": {
      "title": "New dashboard filters",
      "level": "modal",
      "content": {
        "type": "rich2",
        "children": [
          { "type": "paragraph", "children": [{ "text": "Filter dashboards by region and plan." }] }
        ]
      }
    }
  },
  "filter_condition": {
    "predicates": [
      { "type": "attribute", "fqn": "group/subscription_state", "op": "eq", "value": "active" }
    ]
  }
}
```

- Omit `filter_condition` entirely for an "everyone" audience.
- `create_flow` **never publishes** — it saves a draft and returns a Builder URL. Surface that URL
  to the user.
- Optional CTA buttons go under `draft.announcement.buttons` (max 10), e.g.
  `{ "text": "Open dashboard", "appearance": "primary", "actions": [{ "type": "navigate", "url": "/dashboards", "navigate_target": "same_tab" }] }`.

## Targeting (`filter_condition`)

Predicates are a non-empty JSON array; root entries are AND-combined. Use a `clause` object with
`"operator": "or"` for OR logic.

**Always resolve real identifiers first:**
- `list_attribute_definitions` → valid attribute FQNs and their `data_type`. Company attributes use
  the `group/` prefix (e.g. `group/plan`); company-membership uses `group_membership/`.
- `list_event_definitions` → valid `event_name` values.
- `list_segments` (`subject_type: user`) → existing segment IDs for `{ "type": "segment", "segment_id": "…" }`.

Operators by data type: string → `eq, ne, contains, starts_with, ends_with`; number →
`eq, ne, gt, gte, lt, lte`; boolean → `eq, ne`; datetime → comparisons plus `within_days` /
`older_than_days` (value = positive integer days).

A friendly label the user gives you ("paid", "active", "enterprise") almost never maps 1:1 to a
stored value. Resolve it: e.g. "active customers" is usually the company attribute
`group/subscription_state = active` (not a made-up `group/plan`); "enterprise" is usually a specific
`group/plan_id` value you may need to discover via `list_companies`. Look up the real FQN and value,
then echo the interpreted audience back before finalizing.

Common patterns:

```json
// Active (subscribed) customers — company attribute, evaluated per user's company
[{ "type": "attribute", "fqn": "group/subscription_state", "op": "eq", "value": "active" }]

// Inactive users (no session in 30 days)
[{ "type": "attribute", "fqn": "last_seen_at", "op": "older_than_days", "value": 30 }]

// Haven't completed a specific flow, ever
[{ "type": "not_event", "event_name": "flow_completed", "time_op": "any" }]

// EU region OR US region (OR group)
[{
  "type": "clause", "operator": "or",
  "predicates": [
    { "type": "attribute", "fqn": "group/region", "op": "eq", "value": "eu" },
    { "type": "attribute", "fqn": "group/region", "op": "eq", "value": "us" }
  ]
}]
```

Mind data types — string `"true"` ≠ boolean `true`, and that mismatch silently matches no one.
Always echo the interpreted audience back to the user in plain English before finalizing.

## Resource Center readiness check (informational)

```
list_flows(types: "resource_center", state: "published", env_id: <env>)
```

If this returns nothing, no published Resource Center exists — announcements (even Modal/Toast) won't
surface. This is informational only; mention it once and let the user proceed.

## Publishing (two-step confirm)

`set_flow_publication` requires an explicit confirm handshake:

1. First call — **omit** `confirm` (or `false`). You get a `confirmation_required` payload
   describing what will change.
2. Second call — `confirm: true` to actually publish.

```json
// step 1
{ "action": "publish", "flow_id": "<flow-uuid>", "env_id": "<env-uuid>" }
// step 2
{ "action": "publish", "flow_id": "<flow-uuid>", "env_id": "<env-uuid>", "confirm": true }
```

Only do step 2 after the user has said yes to publishing. Use `action: "unpublish"` (same handshake)
to take it back down.
