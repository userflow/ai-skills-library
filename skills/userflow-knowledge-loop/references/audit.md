# Stage 1: Audit

Goal: a short, prioritized backlog of articles to **create**, **update** or **retire**, each backed by
evidence.

**Ask for the time window before pulling anything** (skip the question only if the user already
said it, or the saved settings have a window):

> "How far back should I look? Default is the last 7 days, which suits a weekly review. You can pick
> 14 days, 30 days, or any custom range."

On a first run (no backlog history in the settings), ask this instead:

> "This is the first run, so I suggest the last 30 days: there's no earlier backlog yet, and a longer
> window shows which topics keep coming back. OK, or would you prefer 7 or 14 days?"

- **Default: 7 days**, if the user has no preference.
- **First run:** 30 days unless the user prefers a shorter window.
- Long windows (60+ days) on busy accounts mean a lot of conversations: say the run will take longer
  and may sample the answered (non-frustrated) conversations.
- Save the ongoing window in the settings so the next run doesn't ask again. The first-run 30 days is
  a one-off: save 7 days, or the window the user picks for regular runs.
- Compute explicit start and end dates from today and state them in the report.

**Re-runs.** If the backlog history shows an audit already ran with the same sources and the same
window (no new export, no newly connected tool, no new day's data), don't repeat it: it would only
reproduce the same backlog and double-count topics as recurring. Say so, show what's still open, and
offer new sources or the next draft. If the user explicitly asks for a re-run, run the whole audit
again and write a new report file (`knowledge-loop-audit-YYYY-MM-DD.md`; add `-2` to the name if
one exists for the date). Don't append
to or edit an earlier report, and write each result once. Replace that date's backlog history entry
rather than adding a second one.

## Contents
1. Sources
2. Turning signals into topics
3. Checks before an item goes on the backlog
4. Priority
5. Output and delivery

## 1. Sources

Run every source that's available; skip the rest and say which were skipped.

### A. Userflow Adoption Agent (in-product questions)
The best signal for gaps that never became tickets: users asked while stuck inside the product.
1. **Pick the agents.** If the settings list in-app agent ids, use those. Otherwise `list_flows` with
   `types: "assistant"`, `state: "published"`. Use ids, not names. `list_flows` isn't scoped to an
   environment and doesn't say where an agent is placed, so for each agent get
   `get_adoption_agent_analytics` (`flow_id`, `env_id`, window, `interval: "month"`) and skip agents
   with 0 conversations. For the rest, check each is live in the chosen environment
   (`get_flow_details` with `env_id`: its `flow_envs` entry has a `published_version_id`). Show them
   (name and conversation count) and ask once which run inside the product; skip website/prospect
   agents. Save the chosen ids in the settings.
   With many agents, make these per-agent calls in parallel. On later runs, check the saved ids are
   still published and mention any new in-app agents. If every agent had 0 conversations in the
   window, or agents are only published in another environment, say so once and continue.
   **If no in-app agent is published**, check `list_flows` with `types: "assistant"` and no state
   filter, then tell the user once (never repeat it in the same run) and continue with the other
   sources. Never create or publish an agent, and never assume which plans include it.
   - **None exists:** "I didn't find an Adoption Agent in your account. If your plan includes it,
     publishing one inside your product would let me also use the questions users ask while they're
     stuck. Here's how to set it up: <help article>. For now, I'll continue with your other sources."
   - **Exists but unpublished:** "Your Adoption Agent '<name>' isn't published yet, so there are no
     in-app questions to read. Once it's live, the next run can use them: <Builder link>. Continuing
     with your other sources." (An existing agent means the plan includes it; don't add "if your plan
     includes it".)
   - **Published only on a website:** "Your Adoption Agent only runs on your website, so I can't see
     questions from inside your product. Adding it in-app would give the next run that signal."
   For `<help article>`, call `search_knowledge_base` with `q: "set up Adoption Agent"` (Userflow's
   own docs, the right source here) and link the top setup article; otherwise point to
   https://help.userflow.com. Never guess an article URL. Builder link: the primary environment is
   `https://userflow.com/app/<company slug>/flows/<agent id>/builder`. Every other environment is
   `https://userflow.com/app/<company slug>@<env slug>/flows/<agent id>/builder`. `describe_session`
   does not mark which environment is primary. Use the plain form for the environment the user treats
   as production, or when there is only one environment. Use the `@<env slug>` form when they picked
   a second environment.
2. `get_adoption_agent_analytics` (`flow_id`, `env_id`, window) for totals, if not already fetched.
3. `list_adoption_agent_conversations` with `include_messages: true` and the window:
   - `conversation_type: "unanswered"` → **Unanswered**: the agent found nothing to answer from
   - `conversation_type: "disliked"` → **Disliked**: it answered, the user said it was wrong or
     unhelpful (read `feedback` when present). That filter counts only thumbs ratings. A user can
     also leave typed `feedback` with `rating` empty ("bad", "not what I expected"), so when you
     read unfiltered conversations, also treat a message with negative `feedback` text as Disliked.
     Ignore `scale_rating`, which can be 1 for positive and negative text alike.
   - unfiltered (if volume allows) → look for **Struggle**: the user asked the same thing at least
     twice (a rephrase or re-ask) in one conversation, or the same user asked it again in a later
     conversation
   Page with `offset` (limit caps at 50 with messages). Dedupe by conversation id. Messages aren't
   always in order: sort by `inserted_at` before looking for re-asks.
4. **Drop internal users.** If the settings have no internal email domains, ask for them now (see
   `SKILL.md`), before reading any conversation; never leave this for a later run.
   A conversation's `user_id` matches the `id` field in `list_users`
   results (not `external_id`), and it can't be searched with `q`. So: `list_users` with `q` = each
   internal domain (`limit: 100`, page with `offset`), keep users whose `attributes.email` ends with the domain (name and
   email are under `attributes`, not top-level fields, and many users have no email),
   collect their `id`s, and drop conversations whose `user_id` is in that set.
   To see who the remaining askers are, page `list_users` (`limit: 100`) with predicate
   `[{"type": "attribute", "fqn": "last_seen_at", "op": "after_date", "value": "<window start>"}]`
   and match `id` to the conversations' `user_id`s. Stop paging once every `user_id` is matched, or
   after 10 pages on a large account, and report the rest as unresolved (`get_user_events` with a `user_id` also shows
   where they were: `page_url` is inside each event's `attributes`, for example a `localhost`
   `attributes.page_url`). Report how many conversations came from users with
   no email and from users that look like test accounts ("test" in the name or email, localhost
   pages), and ask whether to drop them. Count conversations per agent after this step.
5. Read what users asked (`user_content`), not what the agent answered.

### B. Support conversations
Use the connected support tool's search for the window (or the export). Drop conversations from
internal email domains and obvious test accounts first. Look for:
- conversations a human had to answer that a bot couldn't (bot escalations)
- low-rated answers
- the same question across several customers
- a support reply containing steps that no article contains ("human answers beat docs")
Read full threads only for the shortlist.

### C. Support AI bot performance (if available)
If the support tool exposes AI-bot data (resolution state, escalations, ratings, "no source found"),
treat escalations and low ratings like Adoption Agent Disliked, and "no source" like Unanswered.

### D. Product changes
- **Userflow announcements:** two `list_flows` calls with `types: "announcement"`:
  `first_published_after` = window start (new ones), and `edited_after` = window start (older ones
  republished in the window), both with `include_publications: true`. `list_flows` isn't scoped to
  an environment, and the second call also returns drafts and announcements that were only edited:
  in both results keep only those with a `publications` entry whose
  `env_id` is the chosen environment and whose `inserted_at` is on or after the window start. Each
  announced feature or change may need a new article or updated screenshots and steps. Read the text with
  `get_flow_details` (`env_id`, `include_content: true`): it's in `draft.announcement` (`title`,
  `content`, `more_content`); `content` and `more_content` are rich-text trees, so collect their
  `text` values. That's the draft; if `flow_envs[0].draft_dirty` is true, say the live
  text may differ. If the content doesn't come back, work from its name and ask the user for the
  release note.
- **Release notes / changelog:** ask for the link or doc if they keep one; read it with the docs
  connector or web fetch.
- **Upcoming changes:** ask if anything ships in the next two weeks that needs docs ready.

### E. Help center search (if the tool exposes it)
Searches with no results and searches where users bounced are direct gap signals. Use them only if
the help center connector or an export provides them. Otherwise skip.

### F. Team-chat threads marked for the KB (if team chat is connected)
Colleagues often answer a question in chat that no article covers. A team marks such a thread by
replying with its KB marker (the settings' marker, for example `kbpin`) once the question has an
answer. That is a person saying "this belongs in the help center".
1. **Find them.** Search the connected chat tool for messages that are the marker, posted inside the
   window. Public channels only, unless the settings include private ones. Match messages that
   consist of the marker; a message that merely discusses it is not a pin. A marker message says
   which thread it belongs to (in Slack its permalink carries the parent thread id): open that
   thread from its first message. Read only these threads, never whole channels. Dedupe by thread.
2. **Read each thread whole.** The **question** is what an end user would have asked, restated in
   their words: usually the first message, but when that is a bot post, a feedback note or a status
   update, take it from the replies. The replies before the marker are the **answer** (the people
   who answered, and any correction made along the way). A marker with no substantive answer before
   it (no reply, or only chatter), or one that isn't inside a thread, is an **unresolved pinned
   thread**: list it under "also seen" with its link and don't draft from it.
   Also read the replies **after** the marker. A later "this is already documented", "that was a bug
   and it's fixed" or "that's wrong" changes the outcome: feed it into checks 3.1 and 3.2 and don't
   draft a fixed bug into an article.
3. **Treat the answer as a colleague's answer, not a verified fact.** It can be informal, partial or
   out of date. Use it as the "best human answer" and the draft's starting point, and check it
   against the product, the announcements and the existing article (section 3).
4. **Keep what's internal internal.** Paraphrase the question and answer, cite the thread link, and
   leave out names, customer names, internal tool names, private links and tokens.
5. **How it counts.** A pinned thread is evidence on its own and may become a backlog item even when
   only one person asked: the team already judged it worth documenting. It is team knowledge, not
   end-user demand, so it doesn't add to a topic's distinct end users. When end users asked the same
   thing (sources A to C), join them into one topic. If a pinned topic is already fully covered by a
   live article and has no end-user signal, it is not a backlog item: list it under "also seen" as
   "pinned, already documented".

## 2. Turning signals into topics

- Group signals by what users were trying to do, in their words.
- Map each topic to an existing article (search the help center by keywords and by the product area)
  or to "new article needed".
- Per topic keep: distinct users/companies, sources, evidence ids (including pinned-thread links),
  and the best human answer if any.

## 3. Checks before an item goes on the backlog

1. **Already covered?** Search the team's help center for the topic with 2–3 different phrasings,
   using the first method available:
   - the help center connector's search, or, if it only returns every article at once, that list saved
     to a file and searched with a script (if you can't run scripts, search it in batches in context)
   - with no connector: an index of the help center (try `<help center URL>/sitemap.xml`, the
     sitemap named in `robots.txt`, `<help center URL>/llms.txt`, or the category and index pages),
     read with web fetch, then the likely articles. Web fetch may return summaries rather than the
     exact article text; that's enough to judge coverage
   - otherwise, list the topics and ask the user to check them
   Never use `search_knowledge_base` for this; it searches Userflow's docs, not the team's. Say
   which method you used. An index or a fetch summary can't prove an article is absent: word it as
   "not found in the index", not "missing". When the agent answered, also open the links it cited:
   a link that is dead or points at an unrelated article is evidence the real article is missing
   or hard to find. If an article fully answers it, the problem is findability or the agent's
   sources, not content: record it as **"Covered but not found"** with the article link and the
   specific fixes from "Adoption Agent fixes" in section 5 that apply to it.
2. **Already fixed?** If the settings' backlog history or the open reviews show an article was
   updated for this topic recently, check whether the signal dropped after the fix date. If it
   didn't, escalate it to a **full rewrite** instead of another small edit.
3. **Recurring?** If a topic appeared in all 3 audits in the backlog history with new evidence ids each
   time, flag it as recurring
   and suggest a section-level review rather than one more patch.
4. **Fragment?** Several small items on the same article become one update item.
5. **Not a docs problem?** Bugs go to engineering; one-off account issues (a refund, a password
   reset, a billing question about one account) go to support, and the user who asked still needs a
   personal reply (Follow-ups, `follow-ups.md`); questions that are really a short in-app click path
   may be better as a walkthrough (`userflow-create-reactive-flows`).

## 4. Priority

- **P1:** a recent product change with no or wrong docs; or 5+ distinct users with frustration
  signals (unanswered, disliked, escalated, low-rated)
- **P2:** 3–4 distinct users asking the same thing (no frustration signal needed: a question many
  users ask is a gap even when each got an answer); or an article that contradicts current human
  answers
- **P3:** everything else with evidence. A pinned team-chat thread alone is P3, unless it reports a
  recent product change with no or wrong docs (P1) or its answer contradicts a live article (P2).
  It also moves up when end users asked the same thing (sources A to C) and that reaches P2 or P1 on
  its own.

Within a priority, order by distinct users, then by signal (unanswered, then disliked, then
struggle), then by number of conversations. Do the sort explicitly before presenting: two items
with 2 users must rank above two items with 1 user in the same priority. Cap the backlog at about 10 items per run so it gets
done; list the rest as "also seen".

**Thin evidence.** If every item is P3, all the evidence comes from fewer than 3 users, or no topic
has 3 or more distinct users with a frustration signal, say so plainly at the top of the report
rather than presenting the list as the worst gaps. Offer a longer window, more agents or sources,
or the Export stale check.

## 5. Output and delivery

One entry per item:

- **Article:** existing title + link, or "New article: <working title>"
- **Action:** Create / Update / Retire / Covered but not found
- **What's wrong or missing:** one or two sentences
- **Evidence:** source + ids (Adoption Agent conversation id + the user's question, paraphrased;
  never quote tokens, keys or URLs that users pasted; support
  conversation id; team-chat thread link; announcement name; search term + count)
- **Best known answer:** the human reply's substance, if any
- **Priority:** P1/P2/P3

Start with one line of numbers (conversations read per source, pinned threads read, internal
removed, topics found), then the backlog, then **Drafts for approval**, then "also seen" and skipped
sources.

### Drafts for approval
The report must not stop at what is wrong. After the backlog is sorted, write the drafts for the
**top 3 to 5 draftable Create and Update items**, in priority order, following `draft.md` (house
style, `[CONFIRM]` and `[SCREENSHOT]` markers, a change summary for updates). Show each draft in the
report directly under its evidence, with its **Status** (`Needs review`), so the reviewer reads the
gap and the proposed fix together. The cap keeps the report readable; the rest of the backlog stays
listed and is drafted when the user asks.
- **Draftable** means there is a verified or pinned source for the facts and the topic isn't
  unresolved or waiting on an owner's decision. Skip an item that isn't draftable, take the next one
  that is, and list each skipped item with its reason (for example "no source for the steps", "needs
  the legal owner"). Never guess to fill the cap.
- **Retire** and **Covered but not found** items get a recommendation, not a draft (see `draft.md`).
- Evidence links (conversation ids, team-chat thread links) stay in the report and the review. They
  never go into the article text.
- End the section with the reviewer checklist from `review.md` once, not per draft.
- **What the reviewer's answer does:** *approve* → `Approved`, under the Stage 3 rules (a named
  reviewer, every `[CONFIRM]` answered or accepted). *Edit* → apply the edits, set `Changes
  requested`, then back to `Needs review`. *Skip* → the draft stays `Needs review` and is listed as
  skipped for this run; the item stays in the backlog. Use `Rejected` only when the reviewer says
  the item is not wanted.
- Set each shown draft to `Needs review` in the settings' Open reviews and hand over to Stage 3.
  Showing a draft is not approval: nothing is published until a named reviewer approves it.

Cite conversation ids, never customer emails or names. Findings with no user signal behind them
(for example an outdated product name spotted in the help center index) are not backlog items: list
them under "also seen / housekeeping" and say they have no user evidence.

### Recommendations and next steps
Every recommendation, including the closing "next steps", names what it applies to (the article,
flow, agent or topic, with its evidence ids) and the exact change. A generic step such as "improve
Adoption Agent retrieval" or "review the docs" is not allowed: replace it with the specific fixes
below, or leave it out.

**Adoption Agent fixes.** When the agent answered badly or not at all although an article covers the
topic, say which of these apply, for which article, and why:
- **Not a source:** the article isn't in the agent's knowledge sources. Add it (Adoption Agent →
  Sources in the Userflow Builder).
- **Users' words missing:** users ask with words the article doesn't use. Quote the phrasings
  (paraphrased) and suggest adding them to the title, the first paragraph or a heading.
- **Answer buried:** the answer sits deep inside a long article. Suggest a section with its own
  heading that answers that one question, or a separate short article.
- **Wrong or dead link cited:** the agent linked an unrelated or broken page. Name the link it gave
  and the right article; fix the link where it comes from (often another article that links to the
  wrong page).
- **A flow should be offered:** for a walkthrough the agent should recommend, write the text for its
  **Flow purpose** field (Adoption Agent → Sources → Flows → the flow): one or two sentences in the
  users' words on what it helps with. The agent relies heavily on that field. The MCP can't set it,
  so give it to paste.
- **Changes not live yet:** sources and settings changed in the Builder take effect only after the
  agent is published again. Say so whenever a fix touches the agent.

Delivery, in order of preference:
1. As a document or task list in the team's doc/task tool (ask before creating; one task per item if
   it's a task tool).
2. Posted to their team messaging tool, only after the user confirms the channel and the exact
   message. The drafts' approval request follows `review.md`.
3. In chat, plus a downloadable file (`knowledge-loop-audit-YYYY-MM-DD.md`) if you can create files.

Add this audit (date, window, sources, and each item's title, action and evidence ids) to the
settings' backlog history, keeping the last 3.
End by sending the drafts for approval as `review.md` describes (in the team's messaging tool when
the settings name one), and ask whether to draft any of the remaining backlog items, including any
that were skipped as not draftable. If any end users got no answer in the window, say how many
and offer Follow-ups.
