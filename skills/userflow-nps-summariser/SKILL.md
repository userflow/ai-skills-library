---
name: userflow-nps-summariser
description: Summarise the positive and negative comments from a Userflow NPS survey over a chosen time frame, with expandable user lists showing each respondent's comment and score. Use this skill whenever the user with the Userflow MCP connected asks to "summarise NPS", "summarise NPS feedback/comments", "what are people saying in our NPS", "NPS comment summary", "group NPS feedback", or anything about reading, digesting, or theming NPS survey responses. Also trigger when a widget from this skill sends a prompt like "Summarise NPS feedback for ... over ...". Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow NPS summariser

Summarise what respondents wrote in an NPS survey — positive and negative comment themes with expandable per-user lists (comment + score). The output is deliberately comment-only: no NPS score card, no promoter/passive/detractor split, no trend chart.

Interaction, usually across three turns:
1. **Link** — ask for the NPS flow's Userflow link, extract the flow ID, verify it's genuinely an NPS survey.
2. **Time frame** — render a time-frame chip widget; the choice arrives via `sendPrompt`.
3. **Summary** — pull raw responses, join and classify, render the comment summary widget plus written insights.

If the user's first message already contains a link (or flow name) and a time frame, collapse the phases: verify, then go straight to the summary.

## Setup

1. Load Userflow tools via `tool_search` if needed: `list_flows`, `describe_session`, `list_flow_survey_questions`, `list_survey_responses`.
2. Call `describe_session` once for `env_id`. Default to Production; ask only if multiple non-obvious environments exist.

## Phase 1 — link and verification

Userflow has **no `nps` flow type** — the `types` filter silently ignores the value and returns everything. NPS surveys are regular flows containing an NPS question block, and flow names lie in both directions (a flow named "Trial Prompt: NPS Survey" may contain zero questions; a survey may lack an NPS block). So never trust names; always verify.

1. Ask the user to paste the flow's link from the Userflow app (e.g. `https://app.userflow.com/app/<slug>/flows/<uuid>/builder`). Extract the UUID from the path. If they give a name instead, resolve it via `list_flows` with `flow_name` and confirm the match.
2. Call `list_flow_survey_questions` with the flow ID. Verify a question with `type: "nps"` exists. Capture:
   - the NPS question's `cvid` and `name`
   - every text-type question (`text`, `multiline_text`) — these are the comment sources; note their names (they reveal the flow's branching, e.g. separate "Passive feedback" and "Detractor feedback" questions)
   - whether any feedback question exists for promoters — many flows don't have one, which matters for the summary
3. If no `nps` question is found, tell the user plainly what the flow actually contains (its question types, or that it has none) and ask for a different link. Do not proceed on a name match alone.

## Phase 2 — time frame

Render a small widget (Visualizer, `interactive` module): a confirmation pill showing the verified flow name, chips for Last 1 week / 15 days / 1 month / quarter / 6 months / year (default: quarter), and a "Summarise NPS feedback ↗" button whose `sendPrompt` includes the flow name, ID, and chosen range. End the turn.

## Phase 3 — data pull and joining

Map the range to a start date. **Both survey tools require full ISO 8601 datetimes** — bare dates like `2026-04-21` are rejected. Use `2026-04-21T00:00:00Z` / `2026-07-20T23:59:59Z` forms.

1. Call `list_survey_responses` with `flow_id`, `env_id`, `start_date`, `end_date`, `limit: 500`. Do **not** call `get_nps_breakdown` — the score summary is out of scope by design.
2. The result is one row per question per session. Join rows by `session_id`:
   - the row whose `question_cvid` matches the NPS question gives the score (`number_answer`, arrives as a string — parse it)
   - any text-question row in the same session gives the comment (`text_answer`)
   - empty-string text answers mean the user skipped the box — treat as no comment
3. If 500 rows come back, warn that the export may be truncated and offer a narrower range.

## Phase 3 — classification and summary

Classify each **non-empty comment** by its sentiment, not by the score bucket. An 8-scorer complaining about pricing belongs in Negative; a 7-scorer praising the product belongs in Positive. Genuinely mixed comments go where their dominant substance points, with the full comment visible so the tension shows. Keep each row's score badge so readers can see sentiment and score diverge.

Render one widget (Visualizer; no chart module needed):

1. sr-only summary heading with comment counts and the main themes.
2. Context line: flow name · range · "N comments from M responses".
3. Two `<details open>` accordions — **Positive** (`#348452` heading) and **Negative** (`#e34948` heading). Each contains:
   - a short thematic summary paragraph grouping comments into named themes with counts (e.g. "Pricing & AI limits (3): …") — bold theme labels, plain prose
   - the user list: rows of score badge (colored by score: ≥9 green `#348452`, 7–8 amber `#d97917`, ≤6 red `#e34948`), shortened user ID in monospace (first 8 chars + ellipsis), date, and the comment lightly paraphrased for length but preserving specifics
4. Follow-up `sendPrompt` buttons (labels end in ` ↗`), e.g. draft a promoter feedback question, re-run over a longer range.

Full widget template in `references/widget-templates.md`.

Then write 2–3 insights as prose after the widget (never inside it), drawing on:
- **Theme clustering**: name the dominant complaint clusters and which is a product problem vs a commercial one — they imply different owners and fixes.
- **The promoter blind spot**: if the flow has no promoter feedback question, say the positive column will stay near-empty by design and suggest adding a question — 40%+ of respondents may be scoring 9–10 with no way to say why.
- **Timing clusters**: if several negative comments land in a short window, suggest checking what shipped or changed then.
- **Specific, actionable bug reports** buried in comments (e.g. save behavior, preview rendering) deserve explicit mention — they're free QA.

## Known limitations (state honestly, don't work around)

- `list_survey_responses` returns internal user UUIDs only. No current Userflow MCP tool resolves internal UUIDs to names or emails (`check_user_activity` and `list_users` search external IDs/names/emails only; `get_user_events` confirms existence but returns no identity). Display shortened IDs and, if the user asks who someone is, explain the limitation rather than guessing.
- Comment classification is a judgment call on sentiment; when a comment is truly ambiguous, place it in Negative (complaints are costlier to miss) and keep the verbatim substance visible.

## Edge cases

- Zero comments in the window: still render the widget with both sections empty, state the response count, and lead insights with the flow's feedback-question structure (that's usually why).
- All comments one polarity: render both sections anyway — an empty Positive section paired with the promoter-blind-spot insight is itself the finding.
- Flow published but with responses predating the window: suggest a wider range in the insights when comment volume is thin (under ~5).
