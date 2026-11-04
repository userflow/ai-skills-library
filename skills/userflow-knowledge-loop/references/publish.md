# Stage 4: Publish

Goal: push **approved** drafts live in the team's help center, then make sure the Adoption Agent and
support can use them.

## Before publishing
1. Collect the items with Status `Approved` (from the review document, task tool, help center drafts
   or this chat). Never publish `Needs review`, `Changes requested` or `Rejected` items. If a
   draft changed after it was approved (its last edit time in the help center, file or doc is
   later than the approval time recorded in Open reviews), set it back to `Needs review`.
2. Re-check each approved draft for leftover `[CONFIRM]` or `[SCREENSHOT]` markers. Only markers the
   reviewer accepted as open in Review may remain; otherwise hold the item and set it back to
   `Needs review`. Marker text never goes live: remove accepted markers, and for copy-paste put any
   screenshot note outside the content block.
3. ✋ Show the final list (title, action, target section, new vs. update vs. retire) and get a yes for
   this exact list.

## Publishing
Use the help center connector's own tools; check what they support before starting:
- **Can publish:** create or update the article in the right section/category with the approved
  content, then set it live (or publish the existing draft). For updates, update the existing article
  rather than creating a duplicate. If an update was drafted as a separate copy, apply its content to
  the original, then archive the copy (or ask the user before removing it; never delete it unasked).
  For retirements, use the least destructive option (unpublish or archive, never delete) and add the
  redirect if the tool supports it; otherwise list the old URL and its target for the team. If the
  only option is delete, hand it off instead.
- **Can only create drafts:** create or update the drafts and tell the user to press publish in the
  help center, with links. Set the status to `Handed off`.
- **No connector, or a read-only one:** give each article as copy-paste-ready content in the help
  center's format, with the target section and, for updates, the URL of the article to replace (or
  the exact insertion point for a changed section). Set the item's status to `Handed off`; it's verified on the next run.

Do one item at a time and stop on the first error, report it, and ask how to proceed. Never retry a
publish blindly; check whether the first attempt went through.

## After publishing
1. **Verify:** open each published article (via the connector or web fetch) and confirm the content
   and URL. For `Handed off` items this happens at the start of the next run (Setup step 4 in
   `SKILL.md`).
2. **Update the status** of each verified item to `Published` with the URL and date.
3. **Adoption Agent** (if the team has an in-app one): name the new or updated articles the agent's
   knowledge sources must include (Adoption Agent → Sources in the Userflow Builder; the MCP can't
   change agent sources), and say the agent must be published again for source changes to take
   effect. Next audit will show whether the related unanswered questions dropped.
4. **Support:** suggest updating any saved replies or macros that link to retired or renamed articles.
5. **Walkthroughs:** if an article describes a short click path that many users ask about, suggest
   linking a Userflow walkthrough from it (see `userflow-create-reactive-flows`).

End with a short summary: published, held, failed, and links.
