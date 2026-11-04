# Follow-ups

Goal: every end user who asked the Adoption Agent something it couldn't answer still gets an answer
from a person. This stage finds those users, drafts a reply for each, records a follow-up task, and
sends the drafts for review. **A person sends every reply.** Never contact an end user yourself, by
email, chat, in-app message or any other tool, even if a connector could.

This stage needs the Userflow MCP (it reads Adoption Agent conversations). Without it, say so and
stop.

## When it runs
- **Default: daily** (the "daily digest"), or how often the settings say. Each run covers the time
  since the end of the last run's window (saved in the settings). First run: ask how far back to go
  (suggest the last 7 days).
- You can't start yourself on a schedule. If the user's AI tool can schedule tasks, offer to set it
  up there; otherwise suggest running it each morning.
- Don't create a second follow-up for a conversation that already has one: check the settings' open
  follow-ups (and the task tool, if connected) by conversation id.

## 1. Find who didn't get an answer
1. Use the in-app agent ids from the settings (or pick them as in `audit.md`, source A step 1).
2. `list_adoption_agent_conversations` with `flow_id`, `env_id`, the window as `start_date` and
   `end_date`, `conversation_type: "unanswered"` and `include_messages: true`. Page with `offset`
   (50 per call with messages) until `has_more` is false.
3. The filter returns whole conversations, and messages aren't always in order: sort each
   conversation's messages by `inserted_at` first. Keep messages with `is_unanswered: true`. If a
   later message in the same conversation answered the same question, it doesn't need a follow-up.
   In those same conversations, also keep account-specific requests the agent only redirected to
   support (a refund, a password reset, a charge): nobody has answered them yet either.
4. If the settings say to include disliked answers too, also read `conversation_type: "disliked"`
   and messages with negative typed `feedback` (ignore `scale_rating`). Default: unanswered only.
5. Leave out messages that aren't a question for a person: a pasted link or token on its own, a test
   message, or chatter. Count them.

## 2. Work out who asked
1. Drop internal and test users exactly as in `audit.md`, source A step 4 (ask for internal domains
   first if the settings have none). Also flag users whose email looks like a test or demo address
   (for example `test` in it, or `example.com` or any of its subdomains). Ask about all flagged
   users once, as one list (conversation ids, not emails), before drafting anything; draft only for
   the ones the user keeps.
2. Match each remaining `user_id` to the `id` in `list_users` results (page with a `last_seen_at`
   predicate as in `audit.md`) to get the user's name and email (`attributes.name`, `attributes.email`), and their company if their
   attributes show one. Use only what's needed to reply.
3. A user with no email (anonymous visitors, often `anon-` ids) can't be followed up. Count them and
   say their questions still feed the next audit.

## 3. Draft each reply
One reply per user, covering all their unanswered questions in the window.
- **Find the answer** in the team's help center (connector or web fetch, as in `audit.md` check
  3.1), the best human answer from support or a pinned team-chat thread, and recent announcements.
  Never use `search_knowledge_base` for the team's own product; it searches Userflow's docs.
- **Answer found:** a short, friendly reply in the team's tone that answers the question and links
  the article. Only link articles you opened.
- **Account-specific request** (a refund, a password reset, a charge on their account, access):
  don't answer it. Draft a reply saying who will help and how, and name the team that owns it
  (support, billing) in the task.
- **No answer found:** draft a holding reply ("we're checking and will come back to you") and mark
  the task `[CONFIRM: needs an answer from <owner>]`. Never guess an answer.
- Never repeat tokens, keys or URLs the user pasted. Security, privacy, data location, retention and
  legal claims always get a `[CONFIRM]` naming who should confirm (as in `draft.md`).
- Each question with no article behind it is also a help center gap: list it for the next audit.

## 4. Record a follow-up task
Use the task tool from the settings (any tool: Asana, Jira, Linear, Trello, Monday or another). The
first time, ask which project or list to use, and save it. Never create a ticket, conversation or
reply draft with the end user as requester or recipient: in a support tool (Zendesk, Intercom,
Freshdesk, Help Scout and the like) that can email the customer. Use an internal task or internal
note only.
- One task per user: title `Follow up: <topic> (<conversation id>)`, with no name in it (task links
  posted to a channel often show the title); in the description the user's name and email, the date asked, each question (paraphrased if it contains anything pasted),
  the conversation id, the drafted reply, open `[CONFIRM]`s and the owner if it isn't support.
- ✋ Show the list of tasks (titles and count) and create them only after a yes.
- **No task tool connected:** ask which tool the team tracks work in and suggest connecting it, so
  there's a record of who was followed up. For this run, give the follow-ups as a table (or CSV
  file) in this chat.

## 5. Review, then a person sends
Send the drafts for review as `review.md` describes, with these differences:
- The parent message reads "<N> follow-up replies are ready for review" instead.
- The message posted in the team's messaging tool never contains a user's name, email or company:
  give the topic, the task link and the conversation id. The identity stays in the task. With no
  task tool, the reviewer reads the drafts in this chat instead of a channel.
- Statuses: `Needs review` → `Approved` / `Changes requested` / `Not needed`; then `Sent` once the
  person who sent it says so (or the task is closed). Approval lets a person send the reply; it is
  never a reason for you to send it.
- Keep the statuses in the settings' open follow-ups (conversation id and status only) and in the
  task tool. At the start of each run, list follow-ups still not `Sent` after 2 days.

## Report
One line of numbers: unanswered messages in the window, non-questions left out, users, internal and
test left out, flagged as test and awaiting a decision, anonymous (no email), follow-ups drafted,
tasks created. Then, per follow-up: topic, task link (or
"in this chat"), status. No names or emails in the report itself: they belong only in the tasks, or
in the follow-up table in this chat when there's no task tool. Save the end of this run's window in
the settings.

If nobody needs a follow-up, say "No one needs a follow-up since <date>" and stop.

Questions with no article behind them go into the next audit as evidence (Adoption Agent, source A);
mention the count and offer to run the audit.
