---
name: suggest-with-ai
description: Analyzes a codebase with a working Userflow.js installation and recommends how to get more out of it — which user and company attributes to send, how to make flow targeting reliable with stable selectors, and which Userflow.js advanced functions fit the app. Produces a prioritized, evidence-based report and implements only the suggestions the customer selects. Use when someone wants recommendations for Userflow attributes, better flow targeting, selector stability, or asks what else they should send to Userflow. Suggestions only — installing is the install-with-ai skill, checking correctness is the verify-with-ai skill.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow.js Suggestions

This skill reads a codebase that already has Userflow.js installed and recommends what else to send and how to target content reliably. It recommends first and implements only what the customer selects.

**AGENTS.md convention:** For any reference to `agents.md.template`, update (never overwrite) the "Userflow installation" section of the project's AGENTS.md with the suggestions adopted — attributes added, selector conventions, and any advanced functions wired.

## Scope

Suggestions for an existing, working installation. If Userflow.js isn't installed, hand over to the `install-with-ai` skill. If the install looks broken — duplicate `init()`, identification on public pages — recommend `verify-with-ai` first rather than building suggestions on a defective base.

## Core Rules (non-negotiable - apply throughout)

1. **Recommend from evidence only.** Every suggested attribute, selector, or function must trace to something real in the codebase — a field that exists on a model, a router that's actually used, a UI pattern that's actually present. Cite the source for each. Never invent fields the app doesn't have.
2. **Suggest, then wait.** Deliver the report first. Implement only the items the customer explicitly selects — never apply the whole list unprompted.
3. **Never expand identification scope.** Suggestions ride on the existing `identify()` and `group()` calls. Do not propose `identifyAnonymous()`, identification on new pages, or anything that adds identified users — that changes the customer's MAU count and is out of scope here.
4. **No sensitive data.** Never suggest sending passwords, tokens, secrets, government IDs, health or payment data. Prefer a coarse attribute over raw personal data when either would work — `plan: 'pro'` rather than a billing record.
5. **Respect existing naming.** Reuse the attribute names and casing already sent to Userflow or to other analytics tools rather than inventing near-duplicates. New names use `snake_case`; datetimes use ISO 8601.
6. **Recommend companies when the app has them.** If the codebase has an account, organization, or team model and `group()` isn't already being called, suggest adding it — account-level targeting is usually the highest-value item in the report. Keep the suggestion simple and don't qualify it with availability caveats.
7. **An empty section is a valid result.** If the codebase shows no signal for a suggestion, don't make one. Padding the report with functions the app has no use for is worse than a short report.

---

## Step 1 — Build the Evidence Base

**If you have repository access,** read before suggesting:

| Read                                                             | For                                                                              |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Existing `identify()` / `group()` / `track()` calls              | What's already sent — the baseline to extend, and the naming to match            |
| User model / session object                                      | Candidate user attributes: role, plan, lifecycle fields, counters, feature flags |
| Company / org / team / account model                             | Candidate group attributes, and the membership relation (a per-company role)     |
| Other analytics calls (Segment, Mixpanel, GA)                    | Field names already in use; events the team already treats as meaningful         |
| Router setup and navigation style                                | A client-side router is the signal for `setCustomNavigate()`                     |
| Component library / styling system                               | CSS-in-JS or hashed class names mean selector stability work is needed           |
| Templates or JSX of key funnels (onboarding, settings, checkout) | Whether the elements flows will target carry stable attributes                   |
| URLs and query parameters                                        | Sensitive values in URLs are the signal for `setUrlFilter()`                     |
| Custom input components (comboboxes, rich selects)               | Candidates for `registerCustomInput()`                                           |

**If you do not have repository access,** ask for the user model, the company model, and a sample of the main UI templates — or narrow to the one pillar the customer cares about and request just those files. Don't guess at fields.

---

## Step 2 — Pillar 1: Attributes

Goal: the customer can target and personalize flows without another engineering round-trip later.

**User attributes** extend the existing `identify()` attributes object. Recommend only fields that exist in the code. Common high-value candidates when present: `role` or `permission`, `plan` or `subscription_tier`, lifecycle fields (`onboarded`, `trial_ends_at`, `activated_at`), locale or timezone if flows will localize, and feature flags used for rollout targeting.

**Locale.** If the codebase supports more than one language — a localization library, locale files, or a language field on the user — recommend sending `locale_code` in `identify()`, taken from wherever the app already resolves the user's language. The value must match one of the locale codes configured in the customer's Userflow account exactly; if it's unset or unrecognized, the user sees content in the base locale only.

Match Userflow's data types — string, number, boolean, datetime (ISO 8601), list — and say which type each suggestion is.

**Group attributes** apply if an account or organization model exists. If the app has one but `group()` isn't called yet, recommend adding it (Core rule 6). Candidates when present: `name`, `plan`, `seats`, `industry`, creation date, and a coarse revenue band.

**Membership attributes** are the piece most teams miss. A user's role often belongs neither on the user (it differs per company) nor on the company (it differs per member) — it belongs on the membership: `group(id, attrs, { membership: { role } })`. If the codebase has a per-membership role or permission, recommend exactly this.

**Output** a table per object type: attribute name → source in the code → type → sent via → why it's useful.

---

## Step 3 — Pillar 2: Stable Selectors

Goal: flows keep working when the UI changes.

Userflow finds elements through element inference, which by default may use `data-for`, `data-id`, `data-testid`, `data-test-id`, `for`, `id`, `name`, `placeholder`, and `role`, plus CSS classes — with built-in filters that try to exclude dynamic class names and IDs ending in numbers.

**Audit what flows would target.** In the key funnels, check whether the elements a flow would point at — primary buttons, nav items, form fields — carry any stable attribute from that list. Hashed or CSS-in-JS class names and auto-generated IDs are not stable anchors.

**Recommend a dedicated targeting attribute** when class names are dynamic:

```html
<button data-userflow-target="create-project">New project</button>
```

Be explicit with the customer that `data-userflow-target` is **not** a built-in Userflow attribute — it's a convention, and it only works once registered for inference:

```js
userflow.setInferenceAttributeNames([
  'data-userflow-target',
  'data-testid', 'for', 'id', 'name', 'placeholder', 'role'
])
```

Note that `setInferenceAttributeNames()` **replaces** the default list, so include any defaults the app still relies on. The convention's value: it never collides with styling or tests, it's easy to grep, and renames become deliberate. Recommend it for the specific elements identified in the audit — a table of element → suggested value — not for everything.

**Filter out generated noise** where it exists beyond the built-in filters: `setInferenceClassNameFilter()` for generated class systems, `setInferenceAttributeFilter()` for machine-generated IDs on an attribute Userflow uses.

**Custom inputs.** If the app uses non-`<input>` widgets such as comboboxes or rich selects, flow conditions can't read their values without help — recommend `registerCustomInput(cssSelector, getValue?)` per widget type.

---

## Step 4 — Pillar 3: Advanced Functions

Suggest a function only when its trigger condition actually appears in the codebase (Core rule 7).

| Signal in the codebase                                                                                                                            | Suggest                                                                                            | Why                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Client-side router (React Router, Vue Router, Next router)                                                                                        | `setCustomNavigate(url => router.push(url))`                                                       | In-flow "Navigate to page" actions default to full page loads; this keeps them in-app                                                                     |
| URLs or query params carrying tokens, emails, API keys, search queries, or personal identifiers (check route definitions and query-param parsing) | `setUrlFilter(url => …)`                                                                           | Userflow receives the current URL for page conditions and page tracking; strip or mask those parts before the URL leaves the browser                      |
| App UI with a `z-index` at or above `1234500` (check modals, overlays, sticky headers, toasts)                                                    | `setBaseZIndex(n)`                                                                                 | Userflow places its floating elements at, or slightly above, `1234500`. Anything in the app above that will cover flows, so raise Userflow's base past it |
| Custom scroll containers                                                                                                                          | `setCustomScrollIntoView(el => …)`                                                                 | Override how tooltip targets scroll into view                                                                                                             |
| Combobox or rich-select widgets                                                                                                                   | `registerCustomInput(selector, getValue?)`                                                         | Lets flow conditions read custom inputs                                                                                                                   |
| Authenticated knowledge base linked from flows                                                                                                    | `setLinkUrlDecorator(url => …)`                                                                    | Append auth tokens to KB links only, guarded by domain                                                                                                    |
| Meaningful product actions (project created, invite sent)                                                                                         | `track('noun_past_tense_verb', attrs)`                                                             | Event-based flow triggers and segmentation; requires `identify()` first. Page views are automatic — don't re-track them                                   |
| Multi-account app where users switch orgs                                                                                                         | `group(newGroupId)` on switch, plus membership attributes                                          | Correct account context and per-company role targeting                                                                                                    |
| A "replay onboarding" or help-menu affordance                                                                                                     | `start(contentId, { once })`                                                                       | Start a flow programmatically; `once: true` shows it only if unseen                                                                                       |
| App state that must sync with a dismissal                                                                                                         | `on('flowEnded' | 'checklistEnded', listener)`                                                     | React to dismissals, e.g. persist "checklist dismissed" in the app's own database                                                                         |
| Custom help UI instead of the default launcher                                                                                                    | `setResourceCenterLauncherHidden(true)` plus `openResourceCenter()` and `getResourceCenterState()` | Render the app's own launcher with unread counts                                                                                                          |
| Strict security posture                                                                                                                           | `disableEvalJs()`, called before `identify()` on every load                                        | Blocks flow-builder "Evaluate JavaScript" actions from running in the app                                                                                 |
| Monitoring-sensitive team, or flaky networks                                                                                                      | `load().then(…).catch(…)`                                                                          | Handle Userflow load failures gracefully instead of noisy alerts                                                                                          |


Do not suggest a function with no matching signal. A plain multi-page server-rendered app doesn't need `setCustomNavigate()`; an app with no custom inputs doesn't need `registerCustomInput()`.

---

## Step 5 — Report, Confirm, Implement

Deliver in this structure:

```
# Userflow Suggestions — <project> — <date>

## Current baseline
Already sent: <attributes and events found in the code>

## 1. Attributes
<user table> <group and membership table>

## 2. Selector stability
Findings: <evidence of dynamic classes or IDs>
Convention: data-userflow-target on <n> elements (listed), plus the
setInferenceAttributeNames wiring
Filters and custom inputs: <if applicable>

## 3. Advanced functions
<only rows whose signal exists — each with evidence, a one-line benefit,
and effort (S/M/L)>

## Priority
1. <highest value for lowest effort first>
```

Rank by value-to-effort. Then ask which items to implement, and implement **only those**, matching the existing code style. After implementing, verify each addition — the new attribute appears on the user or group in Userflow, a condition using it evaluates correctly, a `data-userflow-target` element is findable in the flow builder — and update `AGENTS.md` (update or append, never overwrite) with what was adopted.

---

## Reference

- [Userflow.js Installation](https://help.userflow.com/docs/userflowjs-installation) — install baseline, handled by the install-with-ai skill
- [Userflow.js Reference](https://help.userflow.com/docs/userflowjs-reference) — attributes, data types, operations, and all methods including advanced usage
- [Userflow API Reference](https://help.userflow.com/docs/userflow-api-reference) — server-side attribute and event updates when client-side isn't the right place
- [Identity verification](https://help.userflow.com/docs/identity-verification) — required signature context if suggestions touch `identify()` or `group()` in enforced environments
- [Content Security Policy](https://help.userflow.com/docs/content-security-policy) — required CSP directives
- [Element inference and dynamic class names](https://help.userflow.com/docs/element-inference-and-dynamic-class-names) — how Userflow finds elements, default attributes and filters
