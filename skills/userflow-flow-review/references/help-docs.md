# Help center pages

Checks in `checks.md` and rows in `cannot-verify.md` name a page by its key (`doc: flow-not-starting`). Use this table to turn the key into a link. When a URL changes, change it here only.

| Key | Page | Use it for |
|---|---|---|
| flow-not-starting | https://help.userflow.com/docs/flow-not-starting | Not starting, wrong page or time, works in preview but not live, edits not live, disappears after a click |
| flow-targeting | https://help.userflow.com/docs/flow-targeting-and-audience-rules | Audience and conditions: attributes, segments, companies, dates, AND/OR |
| debugger | https://help.userflow.com/docs/using-the-debugger-for-auto-start-conditions | Seeing which auto-start condition fails for a real user; priority between flows |
| dismiss-snooze-restart | https://help.userflow.com/docs/understanding-flow-dismiss-snooze-and-restart | Once per user, repeats, snooze, restart, what counts as complete |
| element-not-found | https://help.userflow.com/docs/element-not-found | Tooltip element not found; dynamic text and class names |
| tooltip-target-behavior | https://help.userflow.com/docs/missing-tooltip-target-behavior | Theme setting for a missing element: tolerance and what happens next |
| step-timeouts | https://help.userflow.com/docs/flow-step-timeouts | Elements that load slowly or appear after a page change |
| hidden-steps | https://help.userflow.com/docs/hidden-steps | Hidden steps that can leave users stuck; triggers for the wrong path as well as the right one |
| enhanced-javascript | https://help.userflow.com/docs/using-enhanced-javascript | Evaluate JavaScript actions; quoting attribute placeholders |
| disconnected-steps | https://help.userflow.com/docs/disconnected-steps | Steps that can't be reached from the first step |
| install-check | https://help.userflow.com/docs/userflowjs-installation-check | Userflow.js installed, initialized, user identified |
| chrome-extension | https://help.userflow.com/docs/chrome-extension-not-working | Preview or element picker not working in the builder |

## How to use these pages

- In the report, end each finding that has a `doc` key with "Read more: <link>". Link each page once per flow, on the first finding that uses it.
- Reading the page is optional. If you can read web pages and the user asks how to fix something step by step, read that one page (add `.md` to the URL for a plain-text version) and follow it. If you can't, give the link. Never read pages you don't need.
- The pages are written for people using the builder and their own app. They don't say how to spot a problem from flow data — that is what `checks.md` is for. Don't replace a check's result with what a page says.
