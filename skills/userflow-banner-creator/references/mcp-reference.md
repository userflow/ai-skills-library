# Userflow MCP reference — banners

Exact tool usage for this skill. Read the live `flow-draft-dsl` and `predicate-dsl` resources via
`read_resource` for the full spec; this file captures the banner-specific decisions.

## Environment

`create_flow` creates the banner **draft at the account level** — it does not take an `env_id`.
Environment matters only for:
- the live-banner priority check → `list_flows(types: "banner", state: "published", env_id: <env>)`
- publishing → `set_flow_publication(..., env_id: <env>)`

Resolve the env once with `describe_session`.

## Placement mapping (always ask)

`draft.banner.embed_mode`:

| User picks | `embed_mode` | Needs a selector? |
|------------|--------------|-------------------|
| Top of page | `body_first` | No — fully MCP |
| Bottom of page | `body_last` | No — fully MCP |
| Anchor to a specific element | `element_first` / `element_last` / `element_before` / `element_after` | **Yes → finish in Builder** |

For element-anchored placement, **don't set `embed_selector` from the MCP** — the skill hands off to
the Builder. Create the draft with copy/behavior and let the user position it there. (If you ever did
set it, `embed_selector` must be a manual selector `{ "type": "manual", "css": "…" }` or
`{ "type": "manual", "text": "Visible label" }` — but the chosen behavior here is Builder hand-off.)

## Behavior fields (`draft.banner`)

| Field | Meaning | Default |
|-------|---------|---------|
| `sticky` | Stick to top/bottom of viewport while scrolling | false |
| `overlay` | Float over app content (true) vs. push content down (false) | false |
| `animate` | Subtle animation on appear | true |
| `content_layout` | `start`, `center`, or `space_between` | center |
| `max_content_width`, `max_width` | integers ≥ 100 | — |
| `border_radius`, `z_index` | integers ≥ 0 | — |
| `margin_top/right/bottom/left` | integers | — |

"Allow users to dismiss" maps to the common `close_disabled` field (dismiss allowed = `close_disabled`
false, the default). Without a dismiss affordance, add a button with a dismiss action.

## Content: rich2 (never HTML)

`draft.banner.content` is a **rich2** document, not an HTML string.

```json
{ "type": "rich2", "children": [
  { "type": "paragraph", "children": [{ "text": "Scheduled maintenance this Saturday, 02:00–04:00 UTC." }] }
]}
```

## Buttons

`draft.banner.buttons` — full-replacement list, max 10. Each: `text`, `appearance`
(`primary` / `secondary` / `default`), and `actions`.

Common actions:
- Navigate → `{ "type": "navigate", "url": "/status", "navigate_target": "same_tab" }` (or `new_tab`)
- Dismiss the banner → `{ "type": "close_flow" }`
- Start a flow → `{ "type": "start_flow", "flow_id": "<uuid>" }`
- Track an event → `{ "type": "track_button_event" }`
- Set an attribute → `{ "type": "set_attribute", ... }`

```json
{ "text": "See status page", "appearance": "primary",
  "actions": [{ "type": "navigate", "url": "/status", "navigate_target": "new_tab" }] }
```

## Targeting (`filter_condition`)

Same predicate DSL as segments/announcements. Predicates are a non-empty array, AND-combined at the
root; use a `clause` with `"operator": "or"` for OR logic. **Resolve real identifiers first**
(`list_attribute_definitions`, `list_event_definitions`, `list_segments`) — never invent them. Company
attributes use the `group/` prefix. Mind data types (string `"true"` ≠ boolean `true`). Echo the
audience back in plain English before creating.

```json
{ "predicates": [
  { "type": "attribute", "fqn": "group/subscription_state", "op": "eq", "value": "active" }
]}
```

## Priority (only when other live banners exist)

Only one banner shows per user at a time; the highest-priority eligible banner wins. If
`list_flows(types: "banner", state: "published")` returns any, ask whether this banner should take
precedence and set top-level `priority` (1–5). Confirm the resulting order is right in the Builder.
Skip entirely when no other banners are live.

## Creating the banner

```json
{
  "name": "Weekend maintenance",
  "type": "banner",
  "priority": 3,
  "draft": {
    "banner": {
      "embed_mode": "body_first",
      "sticky": true,
      "overlay": false,
      "content_layout": "center",
      "content": {
        "type": "rich2",
        "children": [
          { "type": "paragraph", "children": [{ "text": "Scheduled maintenance Saturday, 02:00–04:00 UTC." }] }
        ]
      },
      "buttons": [
        { "text": "Status page", "appearance": "primary",
          "actions": [{ "type": "navigate", "url": "/status", "navigate_target": "new_tab" }] }
      ]
    }
  },
  "filter_condition": {
    "predicates": [
      { "type": "attribute", "fqn": "group/subscription_state", "op": "eq", "value": "active" }
    ]
  }
}
```

- Omit `filter_condition` for "everyone"; omit `priority` when it didn't come up.
- Returns a **Builder URL** — surface it. `create_flow` never publishes.

## Publishing (two-step confirm)

`set_flow_publication` needs an explicit handshake:

```json
// step 1 (review)
{ "action": "publish", "flow_id": "<flow-uuid>", "env_id": "<env-uuid>" }
// step 2 (apply) — only after the user says yes
{ "action": "publish", "flow_id": "<flow-uuid>", "env_id": "<env-uuid>", "confirm": true }
```

Use `action: "unpublish"` (same handshake) to take it down.
