# Export: KB inventory

Goal: one table of every help article, for an inventory, a backup, or to spot stale content. Read-only.

## Collect
Use the help center connector to list all articles (page through everything). If there's no
connector, try in this order:
1. A sitemap (`<help center URL>/sitemap.xml`, or the one named in `robots.txt`), an
   `<help center URL>/llms.txt` index, or the help center's own export (CSV/JSON) if the user can
   provide one. Read it with a script if you can run code; otherwise read it in batches and say the
   inventory may be partial.
2. The help center's index and category pages, read with web fetch, following links to articles. Say
   the inventory may be partial.
Without a connector or export, "Last updated" needs one fetch per article (sample if there are many,
and say so), and web fetch may not return exact article text, so a full-content **backup** needs a
connector or the help center's own export.
Never use `search_knowledge_base`: it lists Userflow's docs, not the team's.
Large results: save to a file and process with a script rather than reading into context. If you
can't run code or create files, work in batches, give the table in chat, and say if it may be
partial.

If many articles share the exact same "last updated" timestamp, treat it as a bulk republish, not real
edits, and say the Stale flag is unreliable for them.

## Columns
Title · URL · Section/category · Status (published/draft/archived) · Last updated · Author/owner (if
available) · Word count · Has screenshots (if detectable) · Language

## Useful flags (add as columns)
- **Stale:** not updated in 12+ months (let the user change the threshold)
- **Mentions removed or renamed features:** if the user gives a list of retired names, search for them
- **Possible duplicates:** very similar titles in the same section
- **Orphans:** articles no other article links to (only if links are available)
- **Used by in-app questions:** articles matching topics from recent Adoption Agent conversations (if
  an audit ran in this session)

## Deliver
A CSV or spreadsheet (in a connected spreadsheet tool, if the user wants), plus a short summary:
total articles, by section, how many are stale, and the top 5 stale articles in areas users ask about
most. Offer to add stale items to the next audit as housekeeping (they have no user evidence, so they
aren't backlog items). If the export shows an open backlog item affects more articles than the
settings say, update that item's scope in the settings. Record the export's date and file name under
"Exports" in the settings.

If the user wants a **backup** (full content, not just the inventory), export each article's body as
Markdown files in a folder named by section, and zip it if you can create files. If you can't create
files, don't paste every article into chat: point the user to the help center's own export.
