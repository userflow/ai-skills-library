---
name: userflow-adoption-agent-topics
description: Read what people actually asked a Userflow Adoption Agent over a time window (default last 30 days) and turn it into a shareable HTML report of plainly-named topics, split into what the agent couldn't answer, what got thumbs-down, and what came up most — every topic expandable to the real conversations behind it. Use this skill whenever a user with the Userflow MCP connected asks "what are people asking the agent", "what are the top topics in the Adoption Agent", "what is the assistant failing to answer", "where is the agent getting negative feedback", "cluster our agent conversations", "analyse Adoption Agent questions", "what are the knowledge gaps in our agent", "summarise AI assistant conversations", or wants any topic, theme, cluster, gap, or failure analysis of an Adoption Agent / AI Assistant / assistant flow. Also trigger when a picker widget from this skill sends a prompt like "Build the Adoption Agent topic report for ... over ...". Requires the Userflow MCP connector.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow Adoption Agent topic report

Turn an Adoption Agent's raw conversation log into a report a PM or support lead can act on: a set of clearly-named topics, sorted into the three questions people actually want answered — **what is the agent failing to answer, what is it getting yelled at for, and what does it get asked most** — with every topic opening up to the real conversations underneath.

The audience is anyone running an Adoption Agent, not just analysts. So topic names have to read like something a colleague would say out loud, and every number has to be traceable to conversations the reader can inspect.

## Requirements

The **Userflow MCP connector** must be connected. If it isn't, say so and stop — there is no useful fallback.

## The flow at a glance

1. **Pick the agent and window** — one picker widget; assistant flow names are heavily duplicated, so never resolve by name alone.
2. **Size the job** — one analytics call gives denominators and tells you how much to pull.
3. **Pull the conversations** — three paginated pulls (disliked, unanswered, general).
4. **Cluster it yourself** — from what users actually wrote. Do not inherit the API's topic model.
5. **Build the report** — one self-contained HTML artifact with expandable topics.
6. **Write insights** — a few paragraphs of prose after the artifact, never inside it.

Read `references/api-notes.md` before the first data call. It documents the field semantics and pagination traps that will otherwise silently corrupt the report — several of them look like working data until you check. Read `references/artifact-template.md` at step 5.

---

## Step 1 — Pick the agent and the window

Call `describe_session` for `env_id`. Default to Production; only ask if the account has several plausible environments and the user hasn't said.

Call `list_flows` with `types: "assistant"`. Expect a lot of them, mostly drafts — real accounts accumulate test copies. **Names repeat**: an account can hold three flows called "Userflow Adoption Agent" and four called "Userflow AI Assistant". Resolving by name would silently analyse an abandoned draft, so the picker exists to make the user choose a specific UUID.

Render a picker widget (Visualizer, `interactive` module): the assistant flows as selectable rows, published first, then by `edited_at` descending. Each row needs enough to disambiguate identically-named flows — state, publication count, last edited date, and the first 8 characters of the UUID. Add window chips (7 / 30 / 90 days / custom, default **30 days**) and a "Build topic report ↗" button whose `sendPrompt` carries the flow name, UUID, and window. Then end the turn.

Flows with `total_publications: 0` have almost certainly never taken traffic. Keep them selectable but visually de-emphasised, so someone who wants a draft can still pick one and get an honest empty report rather than being blocked.

## Step 2 — Size the job before pulling

Call `get_adoption_agent_analytics` with the flow UUID, `env_id`, the window, and `interval: "week"`. This is one cheap call that returns `conversation_stats` (total, liked, disliked, unanswered) and `message_stats` (total messages plus a weekly series with per-week likes and dislikes).

Use it for three things: the report's KPI row, the denominators that turn raw counts into rates, and a pull budget. Roughly, conversations ÷ 50 is the number of paginated calls a full read would take — decide from that whether you can read everything or need to sample, and tell the user which you did.

If the window has almost no traffic (say under 10 conversations), say so plainly and offer a wider window before building anything. Clustering five conversations produces five "topics" and no insight.

## Step 3 — Pull the conversations

Three pulls with `list_adoption_agent_conversations`, always passing `flow_id`, `env_id`, `start_date`, `end_date`, and `include_messages: true`:

1. `conversation_type: "disliked"` — always read all of these. There are usually very few (single or low double digits even across a busy month) and they carry the most valuable content in the dataset.
2. `conversation_type: "unanswered"` — read all, up to your budget.
3. **No `conversation_type`** — the general corpus, for the frequency ranking. This is the expensive one; paginate with `offset`.

`include_messages: true` caps `limit` at 50 regardless of what you ask for, so pagination is mandatory on anything but a quiet window. Dedupe across the three pulls by conversation `id` — a disliked conversation also appears in the general pull, and double-counting it inflates topic sizes.

If you can't read the whole corpus within budget, read the disliked and unanswered sets completely and sample the general pull, because the first two sections must be exhaustive to be trustworthy while the frequency ranking degrades gracefully. Then state the coverage in the report footer: "clustered from 480 of 630 conversations".

## Step 4 — Do your own clustering

**Cluster from the raw messages. Do not use the API's topic model as your grouping.** There is a `get_adoption_agent_top_topics` tool and it returns tempting pre-built sections, but its topic descriptions routinely describe different subject matter than the conversations filed under them, and it tends to dump most traffic into one catch-all topic that then ranks first in every category at once. A report built on it looks authoritative and says nothing. `references/api-notes.md` has the specifics.

Optionally call it once as a cross-check. If your clustering and its ranking disagree sharply, that divergence is worth one line in the insights — but your clustering is the one that ships.

**Cluster on `user_content`, not `assistant_content`.** Assistant replies are templated ("I'm sorry, but I couldn't find specific information in our knowledge base…"), so clustering on them produces groups that describe the agent's failure modes rather than the users' subject matter. What people asked is the signal.

### Naming topics so they're actually readable

This is the part that determines whether the report gets used. Name each topic as the user's intent, in the plainest words that fit — a short verb or noun phrase someone could say in a standup. Abstract nominalisations ("User Interaction and Data Filtering") are what the machine-generated version already does badly; the value you add is saying what people actually wanted.

| Instead of | Say |
|---|---|
| User Interaction and Data Filtering | Can't find Adoption Studio |
| Last Seen and Activity Fields | What "Last seen" actually means |
| Request to Complete Field | Builder field-fill requests |
| Event Tracking Configuration Queries | Setting up event tracking |
| Subscription Tier Feature Access | Hitting a paywall mid-task |

Give each topic a **one-sentence description** in the same register — what these people want and why they're stuck, not a restatement of the name. Aim for **6–12 topics**. Fewer than 6 and you've built the catch-all bucket you were trying to avoid; more than 12 and nobody reads it. Sweep genuine one-offs into a single "Other one-off questions" entry rather than padding the list — but never sweep a *disliked* conversation into it, since a single angry conversation can be the most important thing in the window.

### Frustration chains

A user escalating across turns ("where is the adoption studio?" → "Yes, tell me how to locate it" → "are you serious") is one topic entry, not seven. Count it once, but flag it — repeated escalation inside a single conversation is a stronger failure signal than seven unrelated unanswered questions, and the reader should see that.

### Internal and test traffic

Real accounts have their own team hammering the agent, and it distorts everything. Tell-tale signs: the same `user_content` verbatim dozens of times, agent-action messages rather than questions (`is_unanswered: null` with replies like "I have filled in the field"), and traffic concentrated in two or three recurring `user_id` values.

Keep these topics in the report, marked with a visible **Test** badge, and exclude them from the headline customer counts while still showing their own counts. The reason to show rather than drop them is that the reader needs to know why their message volume looks high, and mislabelling internal QA as customer demand is exactly the error the report exists to prevent. If a topic is ambiguous, leave it unbadged and mention the doubt in the insights.

## Step 5 — The three sections

Every section is a ranked stack of expandable topic cards. Read `references/artifact-template.md` for the HTML.

1. **Couldn't answer** — topics ranked by how many messages have `is_unanswered: true`. Note that this is the agent's own self-report of not finding a knowledge-base match, not a judgment of correctness; a confidently wrong answer counts as answered. Say this in the report, because readers will otherwise treat the unanswered rate as an accuracy score.
2. **Negative feedback** — topics containing messages with `rating: "dislike"`. Always surface the `feedback` free-text verbatim where it exists. It's the only place a user says in their own words what went wrong, and it lands harder than any count.
3. **Asked most often** — topics ranked by conversation count, with the test-badged ones visibly separated from customer traffic.

**A topic appearing in more than one section is expected and meaningful** — the thing people ask most is often the thing that fails most. Render it in each section it qualifies for, but keep one canonical name and description, and badge the repeat ("also #1 unanswered") so the reader understands they're seeing the same topic rather than two similar ones.

## Step 6 — Build the artifact

One self-contained HTML file in `/mnt/user-data/outputs/`, then `present_files`. Structure, styling, and the expand/collapse pattern are in `references/artifact-template.md`.

The one behaviour that matters most: **sort every conversation's messages by `inserted_at` before rendering**. The API returns them unordered, so an unsorted transcript reads as gibberish and destroys trust in the whole report.

## Step 7 — Insights, as prose, after the artifact

Two to four short paragraphs in the chat — not inside the HTML. Reach for the readings the counts don't make obvious:

- **Knowledge gaps vs product gaps.** "Can't find X" is a docs or discoverability problem; "X is only available on a higher plan" is a packaging problem hitting users mid-task. They have different owners, and separating them is the most useful thing this report does.
- **What the dislikes are really about.** Check whether the thumbs-down clusters on wrong answers or on the agent cheerfully offering to help and then failing — the second is a tone-and-capability mismatch and is fixable in the prompt.
- **Concentration.** If a large share of traffic comes from a handful of users, or one week spikes, name it and suggest what to check.
- **What to do next.** One or two concrete moves: articles to write, a paywall message to reword, a topic worth adding to the knowledge base.

Then offer the obvious follow-ups: a wider window, a different agent, or a drill into one topic.

## Known limitations — state these, don't paper over them

- `user_id` values are internal UUIDs. No current Userflow MCP tool resolves them to names or emails, so show shortened IDs and explain the gap if asked rather than guessing.
- Conversation-level and message-level counts disagree slightly (a conversation with two disliked messages counts once in `conversation_stats`, twice in `message_stats`). Pick one basis per number, label it, and don't reconcile them silently.
- "Unanswered" means the agent said it couldn't find an answer. Silent wrong answers are invisible to this report.
- Clustering is a judgment call. When a conversation could sit in two topics, put it where its opening question points and keep the verbatim text visible so a reader can disagree.
