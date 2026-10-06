---
name: userflow-flow-compare
description: Compare two Userflow flows of the same type side by side in an interactive dashboard — views, completions, completion rate, step-funnel drop-off, missing element errors, trends, and improvement insights. Use this skill whenever the user with the Userflow MCP connected asks to "compare flows", "compare these two flows/announcements/checklists", "which flow performs better", "flow A vs flow B", "benchmark my onboarding flows", or wants any head-to-head performance comparison of Userflow content. Also trigger when a picker widget from this skill sends a prompt like "Compare these two ... flows over ... Build the comparison dashboard". Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow flow compare

Compare two flows of the same type over a chosen date range, producing an inline comparison dashboard with metrics, funnels, trends, and insights.

The interaction has two phases, usually across two turns:
1. **Picker phase** — fetch all flows, render an interactive picker (type → two searchable flow dropdowns → date range → Compare button).
2. **Dashboard phase** — triggered by the picker's `sendPrompt` (or by a user who names both flows directly), pull analytics and render the comparison dashboard plus written insights.

If the user already named two flows and a range in their message, skip the picker and go straight to the dashboard phase (resolve names via `list_flows` with `flow_name` and verify both are the same type; if types differ, say so and re-render the picker pre-scoped so they can fix one or both).

## Setup (both phases)

1. Load Userflow tools via `tool_search` if not already loaded: `list_flows`, `describe_session`, `query_flow_metrics`, `query_usage_metrics`, `get_flow_details`.
2. Call `describe_session` once to get `env_id`. Default to the Production environment; only ask the user if there are multiple non-obvious environments.

## Phase 1 — picker

1. Call `list_flows` with `list_all_flow_types: true`, `state: "published"`, `order_by: "edited_at"`, `order_dir: "desc"`. Keep `id`, `name`, `type`, and `first_published_at` for each flow (store `first_published_at` — you need it later for window-clipping warnings).
2. **Exclude** `tracker` (event trackers, no session funnel) and `assistant` (Adoption Agent has its own analytics) from the comparable set. Comparable types: `flow`, `checklist`, `announcement`, `launcher`, `banner`, `resource_center`.
3. Render the picker widget with the Visualizer (call `visualize:read_me` with the `interactive` module first). Follow the picker template in `references/dashboard-templates.md`. Key behavior:
   - Flow type dropdown first, with per-type published counts. Changing type clears both selections.
   - Two searchable dropdowns (text input + filtered list) scoped to the selected type — this makes a type mismatch impossible by design. A flow selected in one dropdown is hidden from the other.
   - Date range chips: Last day, Last 1 week, Last 15 days, Last 1 month, Last quarter, Last 6 months, Last year. Default: Last 1 month.
   - Compare button disabled until both flows are chosen; on click it calls `sendPrompt("Compare these two <type> flows over <range>: Flow 1 = \"<name>\" (id <uuid>), Flow 2 = \"<name>\" (id <uuid>). Build the comparison dashboard.")`.
4. End the turn after rendering — the selection arrives as the next user message.

## Phase 2 — data pull

Map the range to `last_n_days`: day→1, 1 week→7, 15 days→15, 1 month→30, quarter→90, 6 months→180, year→365. Pick `interval`: `day` when ≤31 days, `week` when ≤180, `month` otherwise.

Make exactly these calls:

1. `query_flow_metrics` with `flows: [id1, id2]`, `env_id`, `last_n_days`, `include_time_series: true`, `interval`, and `include_steps: true` (steps only return for guide flows; harmless otherwise). **On a 408 timeout, retry once with identical parameters** — retries routinely succeed. If the retry also fails, tell the user the analytics endpoint is slow right now and offer a narrower range.
2. For funnel-bearing types only (`flow`, `checklist` — skip for announcements/banners/launchers/resource centers): `query_usage_metrics` with `event_name: "tooltip_target_missing"`, `group_by: ["event/flow_id"]`, same `last_n_days`, `limit: 100`. A flow absent from the grouped results has **zero** missing element errors — report 0, don't call again. Note this metric is flow-level, not step-level.
3. **Do not call `get_flow_analytics` or `get_flow_summary`.** Both are timeout-prone (observed 300s timeouts) and add nothing: worst drop-off is computable directly from the step funnel.

## Phase 2 — dashboard

Call `visualize:read_me` with the `chart` module, then render **one** widget. Two layouts, chosen by flow type (full templates in `references/dashboard-templates.md`):

**Guide flows / checklists** — legend, metric cards (views vs, unique viewers vs, completion rate vs, missing element errors vs), step funnel for each flow that has views (horizontal bars, per-step counts, step-over-step drop % in red when ≥50%, worst-drop bar highlighted red), daily/weekly views line chart for both flows, follow-up `sendPrompt` buttons (view sessions, try a different range).

**Announcements** — legend, metric cards (views vs, reactions vs, comments vs, engagement per 100 views vs — computed as (reactions+comments)/views×100, 1 decimal), views trend chart, follow-up buttons. No funnel, no completion rate, no missing-element card.

Chart conventions: Cove series colors (#2a78d6 for flow 1, #eb6834 for flow 2, dashed line for flow 2 so color isn't the only cue), custom HTML legend above the chart, `role="img"` + `aria-label` on canvases, sr-only summary heading first, round every displayed number. Trim leading all-zero periods from long trend charts and say so in the chart label.

## Insights (written prose after the widget, never inside it)

Always give 2–4 insights. Derive them from these patterns, validated in dry runs:

- **Worst drop-off step**: report both the largest absolute view loss and the largest percentage drop between consecutive steps — they're often different steps and imply different fixes.
- **Goal placement artifact**: if completion rate is 0% but mid-funnel retention is strong, check whether the goal step sits after the real point of value; suggest moving the goal or strengthening the transition into the goal step, rather than assuming the whole flow fails.
- **Dormant flow**: a published flow with zero views isn't an error — look at its first step name and start conditions for chaining clues (e.g., a flow whose first step is "Navigate back to main" likely depends on another flow completing). Say what would revive it.
- **Flatline to zero**: a healthy series that drops to exactly zero and stays there mid-window signals an unpublish, expiry, or feed removal — not organic decay. Offer a `get_flow_details` follow-up button to check publication history.
- **Window clipping**: compare the chosen window against each flow's `first_published_at`. If the window starts after a flow's launch, warn that the launch spike is excluded and the comparison may mislead (a "no launch spike" conclusion from a clipped window is an artifact). Suggest a range that covers both launches.
- **Reach vs resonance**: for announcements, contrast total views against engagement per 100 views — broad targeting often wins reach while losing rate; say which goal (awareness vs activation) each pattern serves.
- **Element health**: zero `tooltip_target_missing` errors means drop-off is behavioral, not technical breakage — say so explicitly, it changes what the user should fix.

## Edge cases

- Both flows zero views: render the dashboard anyway (all zeros), lead insights with the dormancy analysis, and suggest a longer range.
- User provides a Userflow URL instead of a name: extract the UUID from the path and match against `list_flows` output.
- User's two flows are different types: name the mismatch plainly, then re-render the picker with both selections cleared so they can change one or both.
- More than ~250 flows in the account: cap each dropdown's visible list at 30 matches and rely on search.
