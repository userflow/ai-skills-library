# Userflow MCP reference — condition segments

Exact tool usage for this skill. Read the live `predicate-dsl` resource via `read_resource` for the
full predicate spec; this file captures the segment-specific decisions.

## The one write tool

`create_or_update_segment` — creates/updates **condition segments only**
(`source_type: condition`). There is **no** MCP tool to create manual/list segments, import members,
create/update users or companies, or set attributes. Don't promise those.

## Subject-type scoping

`subject_type` is required on create: `"user"` or `"company"`. It constrains which attribute FQNs are
valid (same rules as the dashboard segment builder):

| Segment `subject_type` | Allowed attributes in predicates |
|------------------------|----------------------------------|
| `user` | user attributes (bare name, e.g. `email`, `last_seen_at`), company attributes (`group/…`), company-membership (`group_membership/…`) |
| `company` | company attributes only (`group/…`). **Not** user-scoped attrs or `group_membership/…` |

Resolve FQNs with `list_attribute_definitions` (use `scope: "user"`, `"group"`, `"group_membership"`,
or `"event"`). Company attributes are stored and referenced with the `group/` prefix exactly as
returned.

## Building the conditions

Predicates are a **non-empty JSON array**; top-level entries are AND-combined. For OR / grouped logic,
use a `clause` (alias `group`) object with `"operator": "and" | "or"` and a nested `"predicates"` array.

Allowed predicate types **in a persisted condition segment**: `attribute`, `event`, `not_event`, and
nested `clause`/`group`. **`type: "segment"` is rejected anywhere in the tree** — you cannot nest one
segment inside another here.

Operators by `data_type`: string → `eq, ne, contains, starts_with, ends_with`; number →
`eq, ne, gt, gte, lt, lte`; boolean → `eq, ne`; datetime → comparisons plus `within_days` /
`older_than_days` (value = positive integer days).

Nesting budget (same as the dashboard): the top-level array is the outer AND group; you get **one**
level of inner groups, then leaves. A single top-level `clause` with `operator: "or"` replaces the
implicit AND — that's how you express "OR of AND groups".

### Examples

```json
// Company segment: active subscription AND EU region
[
  { "type": "attribute", "fqn": "group/subscription_state", "op": "eq", "value": "active" },
  { "type": "attribute", "fqn": "group/region", "op": "eq", "value": "eu" }
]

// User segment: inactive 30+ days AND never completed onboarding
[
  { "type": "attribute", "fqn": "last_seen_at", "op": "older_than_days", "value": 30 },
  { "type": "not_event", "event_name": "onboarding_completed", "time_op": "any" }
]

// User segment: work email domain is one of two (OR group)
[
  {
    "type": "clause", "operator": "or",
    "predicates": [
      { "type": "attribute", "fqn": "email", "op": "ends_with", "value": "@acme.com" },
      { "type": "attribute", "fqn": "email", "op": "ends_with", "value": "@acme.io" }
    ]
  }
]
```

Mind data types — string `"true"` ≠ boolean `true`, and a mismatch silently matches no one. Always
restate the audience in plain English and confirm before creating.

## Optional match-count preview (read-only)

To sanity-check a filter before creating, run the same predicates through a read tool in the user's
environment (needs `env_id` — get it from `describe_session`; default to Production):

- User segment → `list_users(predicates: [...], env_id: <env>)`
- Company segment → `list_companies(predicates: [...], env_id: <env>)`

Report an approximate count. This is optional and non-blocking. (Note: `list_users`/`list_companies`
accept `type: "segment"` predicates for filtering, but the **segment you create** cannot — keep that
distinction clear.)

## Creating the segment

```json
{
  "subject_type": "company",
  "name": "Active EU companies",
  "predicates": [
    { "type": "attribute", "fqn": "group/subscription_state", "op": "eq", "value": "active" },
    { "type": "attribute", "fqn": "group/region", "op": "eq", "value": "eu" }
  ]
}
```

- Omit `segment_id` to create a new segment; pass it to update an existing one.
- Optional: `columns` (default table columns as FQNs), `order_by` / `order_dir` (default list sort).
- Membership is evaluated automatically and stays current — no manual refresh.
