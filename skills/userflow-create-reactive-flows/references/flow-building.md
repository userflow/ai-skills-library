# Building a walkthrough draft with create_flow

Read this before the first `create_flow` call. For the full schema, `read_resource` with
`flow-draft-dsl` is authoritative.

## Contents
1. Settings
2. Step layout
3. Moving between steps
4. Element targeting (selectors)
5. Example payload
6. Checking the draft

## 1. Settings

```json
{
  "name": "Reactive | Reports: export a report to CSV",
  "type": "flow",
  "app_url": "<the product's app URL>",
  "theme_id": "<theme id>",
  "priority": 3,
  "draft": {
    "restart_enabled": true,
    "close_disabled": false,
    "resource_center_public_name": "How to export a report to CSV",
    "steps": [ ... ]
  }
}
```

- `restart_enabled`, `close_disabled` and `steps` live **inside** `draft` only; put them at the
  top level and they are silently dropped. `draft.url_pattern` is also accepted there, but only a
  launcher uses it to decide which page it appears on. It does not limit a flow. A flow's page
  limit is a `{"type": "page", "operator": "url", "url_pattern": {...}}` condition inside
  `start_condition`. These walkthroughs don't auto-start, so leave that unset.
- `priority` (1–5) only orders flows that auto-start; 3 is a neutral default.
- Don't send the same setting both at the top level and inside `draft` (`conflicting_draft_fields`).
- No `start_frequency` and no `start_condition`: the default `never` means the flow starts only by
  link, Adoption Agent recommendation, launcher, resource center or API.
- `resource_center_public_name` is what end users see in the resource center and Adoption Agent.
  Check it saved; if the field is rejected, remove it and tell the user to set the public title in
  the Builder before publishing.
- Name pattern: `<prefix> | <Feature>: <task in lower case>`. Ask the user once what prefix they
  want (default "Reactive").

## 2. Step layout

1. **Intro** – `modal`. `heading2` with the task name, one sentence on what the flow does, and
   anything to have ready (a file, a name). If the task needs a plan or role, say so here ("You'll
   need admin access"). Primary button "Let's go" → `go_to_step` step 2.
2. **One tooltip per click** – `tooltip` pointed at the element being clicked. Short copy:
   "Click **Export** to …" (bold the UI label). Set `tooltip_placement` (`below`, `above`, `left`,
   `right`; never `top`/`bottom`) so it doesn't cover the element.
3. **Choices or typing with no single button** – `bubble` with the instruction and a primary "Next"
   button → `go_to_step`.
4. **Done** – `modal`, `is_goal: true`. `heading2` saying what's done, one line on what to do with it,
   and the most common gotcha from support threads. Primary button "Finish" → `close_flow`.

Every step needs a fresh UUID as `cross_version_id`, and every step after the first must be reachable
from an earlier step. Content is `rich2` with `paragraph` and `heading2` blocks (never `p`, never
`heading3`); bold UI labels with the `bold` mark.

## 3. Moving between steps

- **User clicks the tooltip's own target:** put `"actions": [{"type": "go_to_step", "step_cvid": "<next>"}]`
  on the step. It fires when the target is clicked. No buttons needed.
- **Tooltip points at one thing but the user moves on by clicking another** (type a name, then click
  Create): point the tooltip at the input and add a trigger. Trigger conditions are **Builder**
  conditions, not the predicate DSL. An element condition needs `type`, `data_type`,
  `element_state` and a manual `selector`:

```json
"triggers": [{
  "condition": {"type": "element", "data_type": "string", "element_state": "click",
                "selector": {"type": "manual", "css": "<create button selector>"}},
  "actions": [{"type": "go_to_step", "step_cvid": "<next>"}]
}]
```

## 4. Element targeting (selectors)

The MCP can't click through the product, record elements or take screenshots. It can only target
with a **manual** selector: `css`, visible `text`, or both. In order of preference:

1. **Borrow from a related published flow.** `get_flow_details` with `include_steps: true` on a flow
   that touches the same screens. Its tooltip steps carry `auto` selectors with an `auto_data` JSON
   string. Inside, find a `cssSelectors` entry in a group with `"cardinality": 1` (it matches exactly
   one element). From `notextGroups`, reuse that CSS alone as `{"type": "manual", "css": "..."}`.
   From `textGroups`, the CSS is unique only together with the text, so always send both `css` and
   the step's visible `text`.
2. **Visible text** for a button or menu item whose label is unique on the screen:
   `{"type": "manual", "text": "Export"}`.
3. **Otherwise a bubble step** with the instruction and a "Next" button. List it for the user to
   point in the Builder.

Never invent a class name or test id. Never send `type: "auto"`, `auto_data` or screenshot fields;
they're rejected. Keep track of which method each step used, because the hand-off checklist depends
on it.

## 5. Example payload (shortened)

```json
{
  "name": "Reactive | Reports: export a report to CSV",
  "type": "flow",
  "app_url": "https://app.example.com",
  "theme_id": "<theme id>",
  "draft": {
    "restart_enabled": true,
    "close_disabled": false,
    "resource_center_public_name": "How to export a report to CSV",
    "steps": [
      {
        "cross_version_id": "6f1c1e2a-1d7b-4b0e-9d36-2f6f0b0d1a01",
        "name": "Intro",
        "appearance": "modal",
        "content": {"type": "rich2", "children": [
          {"type": "heading2", "children": [{"text": "Export a report to CSV"}]},
          {"type": "paragraph", "children": [{"text": "We'll walk you through it. It takes under a minute."}]}
        ]},
        "buttons": [{"text": "Let's go", "appearance": "primary",
          "actions": [{"type": "go_to_step", "step_cvid": "6f1c1e2a-1d7b-4b0e-9d36-2f6f0b0d1a02"}]}]
      },
      {
        "cross_version_id": "6f1c1e2a-1d7b-4b0e-9d36-2f6f0b0d1a02",
        "name": "Open Reports",
        "appearance": "tooltip",
        "tooltip_placement": "right",
        "selector": {"type": "manual", "text": "Reports"},
        "content": {"type": "rich2", "children": [
          {"type": "paragraph", "children": [{"text": "Click "}, {"text": "Reports", "bold": true}, {"text": " in the sidebar."}]}
        ]},
        "actions": [{"type": "go_to_step", "step_cvid": "6f1c1e2a-1d7b-4b0e-9d36-2f6f0b0d1a03"}]
      },
      {
        "cross_version_id": "6f1c1e2a-1d7b-4b0e-9d36-2f6f0b0d1a03",
        "name": "Done",
        "appearance": "modal",
        "is_goal": true,
        "content": {"type": "rich2", "children": [
          {"type": "heading2", "children": [{"text": "Your CSV is downloading"}]},
          {"type": "paragraph", "children": [{"text": "Large reports can take a minute to arrive."}]}
        ]},
        "buttons": [{"text": "Finish", "appearance": "primary", "actions": [{"type": "close_flow"}]}]
      }
    ]
  }
}
```

## 6. Checking the draft

Call `get_flow_details` with `env_id`, `include_steps: true`, `include_content: false` and confirm:
- every step, selector, action and trigger saved as sent (a single trigger condition reads back
  wrapped in an `and` clause, and selectors gain `precision`; both are expected)
- every step after the first is reachable, and the Done step is the goal
- the public title is set (or flagged for the Builder)

`create_flow` returns `builder_url`; give it to the user. If a save fails, read the error, fix the
draft and retry once. Common errors: `p` instead of `paragraph`, a button with a `type` instead of
`actions`, a `go_to_step` pointing at a step you didn't send, `bottom`/`top` as tooltip placement.
