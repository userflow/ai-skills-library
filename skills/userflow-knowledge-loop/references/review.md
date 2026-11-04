# Stage 3: Review

Goal: a clear approval decision on every draft before anything is published. This replaces an
internal "staging" step and works in any tool.

## Set up the review
Drafts made by the audit are already in its report, each under its evidence: don't draft them again.
Keep the full drafts where the reviewer can read them:
- the help center's own draft state (if drafts were created there), or
- a review document or task per draft in the team's doc/task tool (reuse the item's backlog task if
  there is one), or
- the audit report itself, or this chat if the person you're talking to confirms they are the named
  reviewer.

Each entry shows: title, action, priority, change summary, the draft (or its link), open `[CONFIRM]`
questions, screenshot placeholders, and a **Status** field:
`Needs review` → `Approved` / `Changes requested` / `Rejected`; after Stage 4, `Approved` →
`Published`, or `Handed off` (pasted by the team, verified next run).

## Send the approval request
Send it to the place the settings name under "where approval requests go". This works the same in
any messaging tool (Slack, Microsoft Teams, Google Chat, Discord or another): only the connector
changes. If the settings say "this chat", ask the reviewer here and skip the rest of this section.

**The tool is connected:**
1. Use the saved channel, group or thread. If posting fails because it doesn't exist or you can't
   post there, say so and ask for another place; never pick one yourself.
2. Write the message:
   - one parent message for the run: "<N> help center drafts are ready for review", the run date,
     and a link to the report or review doc if there is one, plus the approval signal from the
     settings (for example "react with ✅ to approve, or reply with changes")
   - one reply in that message's thread per draft: title, action (Create/Update), priority, one line
     on why it's needed, how many `[CONFIRM]` questions are open, and a link to the full draft.
     With no link, put the draft text in the thread, split across several messages if it's long
   - mention the reviewer only if the settings say so
   - no customer names, emails, company names or pasted URLs (ground rules in `SKILL.md`);
     conversation ids and thread links are fine
   Tools without threads: one message per draft, each starting with the run date and title.
3. ✋ Show the exact messages and the place, and post only after a yes. Ask this every run: posting
   is visible to others.
4. Save each message's link in the settings' Open reviews so the decision can be read back.

**The tool isn't connected:** say which connector would let you post and read approvals, and
suggest connecting it. For this run, give the messages above as text to paste, and ask the reviewer
to confirm their decision in this chat.

The same steps send Follow-ups for review (`follow-ups.md`), with the differences it lists.

## Reading the decision back
When the review happened in a connected tool, read the reviewer's response with that tool's
connector (each draft's reply thread: replies or reactions; the task's state; the doc's comments).
A reaction or reply on one draft's message decides that draft only; one on the parent message
decides only what it clearly says ("all approved" approves every draft listed in that run). Count it only
when it matches the approval signal in the settings and comes from the named reviewer's own account
in that tool; a signal from anyone else is not approval. Count only signals given after the draft's
latest revision: after changes, post a fresh review request. The review tool holds the decision;
copy it into the settings' Open reviews with who, when and where.
If the connector can't read that kind of signal, say so and ask the reviewer to confirm here.

## Reviewer checklist (include it with the drafts)
- Facts match the product today (steps, labels, plans, permissions)
- Every `[CONFIRM]` answered or removed
- Screenshots added or placeholders accepted
- Title matches how users ask the question
- Links work

## Handling feedback
- **Changes requested:** apply the edits, keep a short change note, set back to `Needs review`.
- **Rejected:** record the reason; if the underlying signal is still real, note it in the backlog
  history for the next audit.
- **Approved:** only a reviewer named in the settings can approve, with the approval signal saved in
  the settings; "publish" or "go ahead" on its own doesn't count. Record who approved, when and
  where. Before recording it, check every `[CONFIRM]` is
  answered; if some remain, ask the reviewer to answer them or explicitly accept them as open, and
  note which. Only approved drafts move to Stage 4.

## Keeping track between runs
Keep the status list in the place the team chose (doc, task tool, or the settings file's
"open reviews" section). At the start of the next run, read it so approved items can be published and
pending ones aren't drafted twice.
