# Stage 2: Draft

Goal: ready-to-review drafts. The audit calls this stage for the top 3 to 5 Create and Update items
and shows the drafts in its report; run it again for any other backlog item the user picks. Never
publish from this stage.

## Before writing
1. **Learn the house style.** Read the 2–3 example articles from the settings (or 2–3 recent articles
   in the same product area). Note: title pattern (task-based "How to…" or noun-based), intro length,
   use of numbered steps, how UI labels are formatted (bold, quotes), callouts/notes, screenshots,
   tone (you/we), and how related articles are linked.
2. **Gather the facts.** For each item, collect the evidence from the audit, the best human support
   answer, the release note or announcement, and the current article (for updates). If a fact can't
   be confirmed from these, don't invent it: write `[CONFIRM: …]` inline for the reviewer. If the
   human support answer and the docs disagree, don't pick one: keep both versions in the notes and
   mark the claim `[CONFIRM]`. An answer from a team-chat thread marked for the KB is a colleague's
   answer: use it as the starting point, but mark every step, name or limit that you couldn't
   confirm from the product, an announcement or the current article `[CONFIRM]`, and keep internal
   tool names, customer names, private links and tokens out of the draft.
3. **Check the scope is current.** If a later export or check changed an item's scope (for example
   more affected articles than the backlog says), update the backlog entry first, then draft for the
   full scope, or say what the draft leaves out and why.

## Writing rules
- One task or question per article. Title in the user's words (what they searched or asked).
- Lead with the answer in the first two sentences, then the steps.
- Numbered steps, one action each, UI labels exactly as they appear in the product.
- Mention plan, role or permission requirements near the top when they apply.
- Add a short "Troubleshooting" or "Common questions" section only when the evidence shows repeat
  follow-ups.
- Link related articles that exist; never link to pages you haven't confirmed.
- Screenshots: you can't capture them. Insert `[SCREENSHOT: what it should show]` placeholders.
- No prices, plan limits or roadmap promises unless the source states them; mark `[CONFIRM]` if
  unsure.
- Claims about security, privacy, data location, retention or legal terms always get a `[CONFIRM]`,
  even when a colleague stated them clearly. Name in the open questions who should confirm them (the
  owner of that topic, not only the docs reviewer).

## For updates
Show a **change summary** first (what's added, removed, corrected, and why, with the evidence), then
the full updated article. For a long article you may give only the changed sections, each with its
exact insertion point (after which heading or paragraph). Keep everything that's still correct; don't
rewrite for style alone.

## For retirements
Explain why (feature removed, duplicate, superseded) and where the article should redirect.

## For "Covered but not found"
No draft. Give the specific fixes instead, from "Adoption Agent fixes" in `audit.md` (for example
a title in the users' words, the missing phrasings, or adding the article to the agent's sources and
publishing the agent).

## Output
Per item:
- **Item:** title, action (Create/Update/Retire), priority
- **Change summary** (updates) or **purpose** (new)
- **Draft** in the help center's format (Markdown by default; HTML if the tool needs it)
- **Open questions** (`[CONFIRM]` list) and **screenshot placeholders**
- **Evidence** links

Where to put drafts, in order of preference:
1. As **drafts** in the help center tool, if the user agrees and the tool has a real unpublished
   state the public can't see. For an Update, only if the tool keeps an unpublished revision of the
   live article. Never create drafts under a public parent page, and never change a live article
   before Stage 4.
2. In the team's doc tool (one doc per draft or one doc for the batch), if connected and agreed.
3. In chat and as downloadable Markdown files.

Set each draft's status to `Needs review` in the settings' Open reviews, then move to Stage 3
(Review).
