# API notes — Adoption Agent tools

Field semantics and traps for the Userflow MCP tools this skill uses. Everything here was checked against live calls on a busy production agent (≈300 conversations / 670 messages in 30 days). Most of these traps don't throw errors. They return plausible-looking data that is quietly wrong, which is why this file exists.

Contents
1. Session and environment
2. Finding the right flow (`list_flows`)
3. Sizing (`get_adoption_agent_analytics`)
4. Pulling conversations (`list_adoption_agent_conversations`)
5. Message fields, one by one
6. What lives in the text (non-obvious content patterns)
7. The topic model (`get_adoption_agent_top_topics`) — why not to use it
8. Counting rules (which basis for which number)

---

## 1. Session and environment

- Every data tool needs `env_id`. Omitting it returns an `environment_required` error that lists environments, which wastes a round trip. Call `describe_session` first; it returns `environments[]` with `id`, `name`, `slug` (`production`, `staging`, …).
- Default to the environment whose slug is `production`. Staging agents usually have only internal test traffic.

## 2. Finding the right flow (`list_flows`)

- Pass `types: "assistant"`. Do **not** also pass `list_all_flow_types` — sending both is rejected as `conflicting_type_scope`.
- Use `order_by: "edited_at"`, `order_dir: "desc"`.
- Useful fields per flow: `id`, `name`, `state` (`published` / `draft` / `archived`), `edited_at`, `first_published_at`, `total_publications`, `last_publisher.name`.
- **Names repeat and copies pile up.** One real account has 20 assistant flows: four named exactly "Userflow AI Assistant", plus "… Copy", "test …", "CS test - …" variants. Only 4 were published.
- **`state: "draft"` does not mean "never had traffic."** A flow with `state: "draft"` and `total_publications > 0` was published and later unpublished; it can hold real historical conversations. Only `total_publications: 0` (and `first_published_at: null`) reliably means "never live".
- `get_adoption_agent_analytics` and `get_adoption_agent_top_topics` accept `flow_name`, but it's a **case-insensitive substring match**. "Userflow Adoption Agent" also matches "Userflow Adoption Agent (No Flows)" and "test Adoption Agent". Always pass `flow_id`.

## 3. Sizing (`get_adoption_agent_analytics`)

Call with `flow_id`, `env_id`, `start_date`, `end_date`, `interval: "week"`. Shape:

```json
{
  "conversation_stats": {"total": 316, "disliked": 7, "liked": 2, "unanswered": 104},
  "message_stats": {
    "messages": 672, "likes": 2, "dislikes": 8, "interval": "week", "timezone": "UTC",
    "time_data": [{"t": "2026-09-14T00:00:00Z", "messages": 110, "likes": 0, "dislikes": 1}, ...]
  }
}
```

- `conversation_stats` counts conversations: one with two disliked messages counts once in `disliked`. `message_stats` counts messages (8 dislikes vs 7 disliked conversations above).
- `conversation_stats.unanswered` = conversations with **at least one** unanswered message, not the number of unanswered messages.
- **Weekly buckets are Monday-aligned**, not aligned to your `start_date`. A window starting Tuesday 15 Sep gets a first bucket labelled Monday 14 Sep that covers only part of the week, and the last bucket is usually partial too. Don't call a short first or last week a "drop"; label partial weeks or leave them out of trend comments.
- `timezone` defaults to UTC. Pass the user's timezone only if they asked for one, and keep it consistent with the dates you send to the conversation pulls.
- Likes are rare (single digits). Don't build a "most liked" section on them.

## 4. Pulling conversations (`list_adoption_agent_conversations`)

Parameters that matter: `flow_id` (required), `env_id`, `start_date`, `end_date`, `conversation_type` (`liked` / `disliked` / `unanswered`, or omit for all), `include_messages`, `limit`, `offset`, `topic_id`.

- **Always send both dates with `include_messages: true`.** Without a date window the call stops with `assistant_messages_scope` and asks the user for confirmation. The `confirm_messages_without_dates` flag exists to release that gate *after the user has approved*. Never set it on your own.
- Use full ISO timestamps: `start_date: "2026-09-15T00:00:00Z"`, `end_date: "2026-10-15T23:59:59Z"`. A bare date as `end_date` risks cutting off the last day.
- `include_messages: true` caps `limit` at 50. Without messages the max is 200.
- Response: `{"items": [...], "total_count": 316, "has_more": true}`. Page with `offset` (0, 50, 100, …) until `has_more` is false. `total_count` in the first response is your denominator for coverage.
- **Payloads are heavy.** A page of 25 conversations with messages ran to roughly 15k tokens; long multi-turn conversations and markdown-heavy agent replies dominate. Budget accordingly: a 300-conversation month is ~6 pages of 50 and can exhaust context. Read disliked and unanswered in full, then sample the general pull (see the skill's step 3).
- **Cheap metadata pass:** the same call with `include_messages: false, limit: 200` returns conversation metadata without bodies. It's a cheap way to see the `user_id` distribution (internal-traffic concentration) across the whole window before deciding what to sample. Check the fields on the first call; don't assume.
- **Window semantics:** the date filter selects *conversations with activity in the window*, but each returned conversation carries **all** its messages, including ones before `start_date`. Observed: a conversation in a 15 Sep–15 Oct pull whose first message was 14 Sep. For counts that should match the window (unanswered messages, dislikes), filter messages by `inserted_at` yourself. Conversation-level `inserted_at` can also predate the window.
- **The three pulls overlap.** A disliked conversation also comes back in the unfiltered pull, and often in the unanswered pull. Dedupe by conversation `id` before counting anything.
- **`conversation_type: "disliked"` returns whole conversations**, not just the disliked messages. In one example a 6-message conversation had one disliked message; the other five were ordinary questions. Find the disliked message by `rating == "dislike"`, and treat the rest as context.

Conversation fields: `id`, `user_id`, `inserted_at`, `updated_at`, `last_activity_at`, `messages[]`.
- `updated_at` equals `inserted_at` in every observed record. Use `last_activity_at` for "when did this conversation end".
- `user_id` is an internal UUID. No current MCP tool resolves it to a name or email; show the first 8 characters.

## 5. Message fields, one by one

Each message is one user turn plus the agent's reply:

| Field | Values seen | Notes |
|---|---|---|
| `id` | UUID | |
| `inserted_at` | ISO timestamp | **Messages arrive unordered.** Sort by this before rendering or reading a conversation's flow. |
| `user_content` | string | What the user typed. The clustering signal. |
| `assistant_content` | string, often markdown | Templated. Don't cluster on it. Contains links, numbered lists, code fences. |
| `rating` | `"dislike"`, `"like"`, `null` | Per message. A dislike can sit on a message the agent **did** answer (`is_unanswered: false`) — confidently wrong or unhelpful answers. |
| `feedback` | free text, `""`, `null` | Only exists alongside a rating. **Empty string and null both mean "no comment"** — treat `""` as absent, don't render an empty quote. |
| `scale_rating` | `null` in every observed record | Ignore unless populated. |
| `topic_id` | UUID or `null` | From the API's topic model. Recent messages are mostly `null` (the model lags) and older ones mostly carry one catch-all id. Not usable for grouping. |
| `is_unanswered` | `true`, `false`, `null` | `true` = the agent said it couldn't find a knowledge-base match. `null` appears on agent-action messages (e.g. builder field-fill replies like "I have filled in the field"), which are neither questions nor answers. |

`is_unanswered: true` is broader than "knowledge gap". It also fires when the agent asks for clarification ("I need more context…") after vague input like "native elements", "wat to do next" or "CAN YOU explain the rest". Separate **too vague to answer** from **asked a real question, KB had nothing** when you cluster; they need different fixes (prompt/UX vs content).

## 6. What lives in the text

Patterns from real traffic worth recognising early:

- **Multiple languages.** Portuguese and German questions appear alongside English, and the agent replies in kind. Cluster by meaning across languages; keep the original text visible in transcripts and add a short English gloss in the topic description if the language isn't English.
- **Handoff requests.** "Speak to agent", "quero falar com o Rudhra" (asking for a named person). These usually get marked unanswered and sometimes disliked. They're a topic in their own right (people wanting a human), not noise.
- **Escalation chains.** Users rephrase the same unsolved problem three to six times in one conversation ("not working still", "applying for only one element but not for another"). One topic entry, flagged as a chain.
- **Non-questions.** Lists of people's names, single keywords, pasted URLs or long targeting-condition strings. Some are internal testing; some are a customer using the agent as a search box. Don't drop them blindly.
- **Customer specifics in verbatims.** Users paste their own app URLs, domains and condition lists. Fine for an internal report; mention in the footer that transcripts are verbatim if the report may be shared outside the company.
- **Plausible but wrong answers are invisible to the flags.** E.g. the agent confidently pointing to a "Dashboard" view for something that doesn't exist, with `is_unanswered: false` and no rating. Only a repeated, rephrased follow-up ("Are you sure?") hints at it. Worth an insight line when you notice it, never a count.

## 7. The topic model (`get_adoption_agent_top_topics`)

Requires topic modelling to be enabled for the account. It returns three sections (`disliked_topics`, `unanswered_topics`, `frequent_topics`), each a list of `{id, name, description, message_count, dislike_count, unanswered_count}`. On the same 30-day window as above it returned:

- One catch-all topic, "User Interaction and Data Flow", holding **488 of 672 messages**, ranked #1 in all three sections.
- A description listing subjects ("Next" buttons, resource-center triggers, step skipping) that matched almost none of the disliked conversations actually filed under it (launcher scroll lag, step duplication, admin ID, event trackers).
- Only 1–2 topics per section despite `limit: 5`.
- Counts that don't reconcile with analytics: 6 dislikes vs 8 message dislikes; 109 unanswered vs analytics' 104 unanswered conversations (different basis, unlabeled); topic counts summing to 547 of 672 messages, because many recent messages have `topic_id: null`.

So: don't group by it, don't filter by `topic_id` (it would silently drop the unassigned recent messages), and don't quote its counts. One cross-check call is fine; if it looks like the above, one insight line ("the built-in topic model files ~70% of messages under a single generic topic") is useful to the reader.

## 8. Counting rules

Pick one basis per number and label it in the UI.

| Number | Basis | Source |
|---|---|---|
| KPI: conversations, % with an unanswered message, disliked conversations | conversation | `conversation_stats` from analytics (it covers the whole window even when you sampled) |
| KPI: messages | message | `message_stats.messages` |
| "Couldn't answer" topic rank | message (`is_unanswered: true`, in window) | your pulls |
| "Negative feedback" topic rank | message (`rating: "dislike"`, in window) | your pulls |
| "Asked most often" topic rank | conversation | your pulls, deduped |

A conversation counts toward a topic once per topic, under the topic its opening question belongs to unless a later turn is clearly a separate subject. If your own totals differ from analytics (they will, slightly, because of the window semantics in §4), show analytics in the KPI row and your totals in the sections, and note it in the footer rather than forcing them to match.
