# What can't be verified over MCP — ask or flag

The `doc` column is a key in `help-docs.md`; give that link with the question so the user can check it themselves.

| # | What | Why it matters | What the skill should say / ask | doc |
|---|---|---|---|---|
| 1 | Userflow.js installed on that site with THIS environment's token | Wrong token = content from another env, or none | "Open the page, run `userflow` in the console; does the token on that site belong to <env>? Does your user appear under Users in <env>?" | install-check |
| 2 | `userflow.identify()` called, with a stable, defined id, before the flow should show | No user = nothing starts; `undefined` id merges everyone | "Is identify called on this page with a real user id?" | install-check |
| 3 | `userflow.group()` called | CHK-07/08 | "Does your app call userflow.group(companyId)?" | flow-targeting |
| 4 | Attributes sent at identify time, not later / not null | Rules run on what is known then | "Are <attrs> passed in identify(), with real values?" | flow-targeting |
| 5 | The element exists, is visible, unique, and the same in every environment | All selector checks | "On the live page, does <selector> match exactly one visible element?" Suggest the builder's element test. | element-not-found |
| 6 | Element inside an iframe / shadow DOM; Userflow.js loaded in both parent and iframe | Never found; duplicate flows | "Is this part of the app inside an iframe?" | element-not-found |
| 7 | Theme "missing tooltip target" behavior and tolerance (`list_themes` returns id, name, archived only) | Decides whether a missing element silently ends the flow | "In the theme → Tooltip, what is the missing-element behavior and wait time? 'Dismiss' makes failures invisible; consider 'speech bubble' and 5–10 s." | tooltip-target-behavior |
| 8 | Translations / enabled locales vs the user's locale | Flow invisible for other languages | "Do your users have a locale set? Is this flow enabled for it?" |  |
| 9 | Target platform (web vs React Native) | Other platform never sees it; CHK-17 | "Is this a web or mobile flow?" |  |
| 10 | Published version content | Only the draft is readable | State it (CHK-02). |  |
| 11 | The checklist task, launcher or resource center item that starts this flow, and whether it is published and shown to the right users | Their content isn't readable over MCP; a manual-start flow with nothing live in front of it gets zero views (CHK-19, CHK-48) | "What should start this flow? Is that checklist / launcher / resource center published in <env> and pointing at this flow?" | flow-not-starting |
| 12 | Host-page overlays, z-index, CSS, CSP | Tooltip hidden or unclickable | "Does anything in your app sit on top of the tooltip? Do the browser console or the builder's element picker show Content Security Policy errors, and does your policy allow Userflow's script, connection and frame sources?" |  |
| 13 | SPA routing, URL filters (`setUrlFilter()`), custom navigate | Page rules see a different URL | "Does your app rewrite URLs for Userflow, use `#` routes, or navigate without a full page load? Does Userflow.js hear about those page changes?" | flow-targeting |
| 14 | One user's state: seen before, snoozed, another flow currently active, leftover preview session | Explains "not for me" | "Check the user's Sessions tab and the debugger; close any open preview with the X. Is another flow, possibly stuck on a hidden step, still active for this user and blocking this one?" | debugger |
| 15 | Manual starts of this flow from other places | They use up "once per user" (CHK-20) | Ask. | dismiss-snooze-restart |
| 16 | A flow started from a link (`?userflow=`) | The parameter is lost if a redirect or reload removes it, or if it sits after a `#` | "After the page loads, is the `?userflow=` parameter still in the address, before any `#`?" | flow-not-starting |
| 17 | The flow runs inside a mobile app or web-view wrapper | Some wrappers ignore button actions such as navigate, snooze or open link | "Does this run inside a mobile app or web view? Do its buttons work there?" |  |
| 18 | Embedded videos or media | Blocked if the media isn't embeddable or the site's frame rules don't allow it | "Is the video public and embeddable, and does your site's frame policy allow its host?" |  |
| 19 | Whether the app sends a device or screen-size attribute | CHK-65 depends on it | "Does your app send a device-type attribute you can use in start and hide rules?" | flow-targeting |
