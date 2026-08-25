---
name: verify-with-ai
description: Inspects an existing Userflow.js installation and reports whether it is correct — no duplicate init(), no leftover placeholders, token matches the environment, identify() only on the authenticated path, no identify()/identifyAnonymous() double-identification, isIdentified() false on public pages (the MAU check), and correct usage of any advanced functions already in use. Produces a severity-ranked report and applies fixes only after the customer confirms. Use when someone wants to verify, audit, review, or debug an existing Userflow install, or asks why Userflow content isn't showing or why their MAU count is high. Verification only — fresh installation is the install-with-ai skill.
metadata:
  author: userflow
  version: "1.0"
---

# Userflow.js Verification

This skill inspects an existing Userflow.js installation and reports whether it is correct. A broken install rarely throws an error — it silently identifies the wrong users (inflating the customer's Monthly Active User count and bill), shows content in the wrong environment, or shows nothing at all. Verification catches those defects before they cost money.

**AGENTS.md convention:** For any reference to `agents.md.template`, update (never overwrite) the "Userflow installation" section of the project's AGENTS.md with the verification date, a summary of findings, and any fixes applied.

## Scope

Verification of an existing install only. This skill **reads first and reports** — it changes code only after the customer confirms a specific fix. If Userflow.js is not present in the codebase, say so and hand over to the `install-with-ai` skill. Recommending new attributes or advanced functions beyond what correctness requires is out of scope.

## Core Rules (non-negotiable — apply throughout)

1. **Read-only until confirmed.** Inspect and report first. Never modify code, move calls, or clean up the install before the customer approves that specific fix. Never apply all fixes as one batch without itemized confirmation.
2. **Every finding needs evidence.** Cite the file and line, or quote the offending code. No finding without a location, and no speculation about code you haven't read.
3. **MAU is the headline risk.** Any path where an unauthenticated visitor can be identified is Critical, regardless of whether content otherwise "works."
4. **Client-side only — requires a browser.** Userflow requires a browser to initialize; it is not built for server-side rendering. *Importing* the package in shared code is fine, but `init()`, `identify()`, and `reset()` being *called* during server rendering is a defect. In React Server Components / Next.js App Router, calls must come from a Client Component marked `"use client"`.
5. **Don't expand scope.** Verify what exists. Never introduce `group()`, `track()`, identity verification, or any function the install doesn't already use — at most, flag them as recommendations.
6. **If you can't verify it, say so.** Some checks need a running app or the Userflow dashboard. Mark those "Needs runtime check" with exact instructions — never report them as passed.
7. **The user ID is the customer's choice.** Userflow accepts any stable, unique identifier. A database ID is recommended because changing the identifier creates a *new* Userflow user — but email is allowed. A changeable ID is an advisory finding, not a defect.

---

## Step 1 — Locate the Install

**If you have repository access,** find every Userflow touchpoint before judging anything:

| Search for | Why |
|---|---|
| `userflow` in `package.json` / lockfile | npm install present? Which version? |
| `import userflow` / `require('userflow.js')` | Every module that touches Userflow |
| `userflow.init(` | All init call sites — there must be exactly one execution path |
| `userflow.identify()` and `userflow.identifyAnonymous()` | All identification call sites and the conditions guarding them |
| `userflow.reset()` | Sign-out wiring |
| `.group()` / `.track()` / `.start()` / `.setCustomNavigate()` / `.updateUser()` | Advanced usage to verify |
| Script tags referencing Userflow (templates, `index.html`, tag managers) | Script-tag installs, and **mixed npm + snippet installs** |
| The token passed to `init()` and where it comes from (`.env`, config, hardcoded) | Environment-token checks |

Build a map: install method → init site(s) → identify site(s) and their guards → reset site → advanced calls. That map is the evidence base for every finding.

**If you do not have repository access,** don't guess. Ask the customer to share the files where `init`/`identify`/`reset` are called plus their env config, or walk them through the Runtime Checks in Step 3 — those need no code access.

---

## Step 2 — Static Checklist

Evaluate each item against the code map. Record **Pass / Fix / Flag / Needs runtime check**, with file:line evidence.

### A. Initialization

- **A1 — Exactly one `init()` execution path.** Two modules both initializing, npm *and* script-tag snippet both present, or an init inside a re-rendering component → **Fix, High**.
- **A2 — `init()` runs before other calls.** Any Userflow call reachable before `init()` → **Fix, High**. (The npm package and official snippet queue early calls, so this is about ordering logic, not race timing.)
- **A3 — Client-side only.** `init()`/`identify()`/`reset()` *called* in server-executed code — a Server Component without `"use client"`, an SSR lifecycle, or server template logic that executes rather than emits the call → **Fix, High**. Server templates that *emit* the script for the browser to run are correct.

### B. Token & Environment

- **B1 — Real token, not a placeholder.** `<USERFLOW_TOKEN>`, `'YOUR_TOKEN'`, or an empty string → **Fix, Critical** (nothing works).
- **B2 — Token matches the environment.** Each build must use the token belonging to that Userflow environment. A production token in staging, or one token shared across all builds, mixes users and content across environments → **Fix, Critical**. You cannot see the Userflow dashboard, so pair this with runtime check R4 and ask the customer to compare against **Settings → Environments**.
- **B3 — Token not hardcoded.** A literal token committed in source rather than injected via env config → **Fix, Medium**. It works, but rotating or adding environments breaks it.

### C. Identification (the MAU section)

- **C1 — `identify()` only on the authenticated path.** Every call site must be reachable only after sign-in/sign-up or with an existing session. `identify()` on a public, marketing, or login page, or unconditionally at app boot → **Fix, Critical** (MAU overage).
- **C2 — No double identification.** `identify()` and `identifyAnonymous()` must never both be reachable on the same page load. The classic defect is `identifyAnonymous()` added as an else-branch to make content show — that identifies *every visitor* → **Fix, Critical**. If a user is never identified, content simply doesn't show and the Debugger reports "not identified"; that is expected, not a bug to patch with `identifyAnonymous()`.
- **C3 — `identifyAnonymous()` is intentional if present.** Where it exists deliberately for signed-out content, confirm the customer knowingly accepted the MAU impact. If they can't confirm → **Flag, Critical** until they do.
- **C4 — Real user values.** No literal `USER_ID` / `USER_EMAIL` / `USER_SIGNED_UP_AT` placeholders → **Fix, Critical**. A changeable ID such as email is **Flag, Low** (Core rule 7), not a defect.
- **C5 — Datetimes in ISO 8601.** Malformed `signed_up_at` breaks date-based targeting → **Fix, Medium**.
- **C6 — Re-render guard correct.** If `isIdentified()` guards `identify()`, confirm it can't block a *different* user: on account switch without reload the code must `reset()` then `identify()` → **Fix, High** if it can skip a new identity. Absence of the guard is **Flag, Low** — redundant identifies are wasteful, not harmful.

### D. Lifecycle

- **D1 — `reset()` on sign-out.** Missing → **Fix, High**: the next user on a shared device inherits the previous user's state. For server-redirect logouts (JSP, PHP, Rails, Django), `reset()` should fire from the logout control before navigation, or at the top of the post-logout landing page.
- **D2 — `reset()` not misused.** Firing on every route change or render, wiping identity constantly → **Fix, Medium**.

### E. Advanced Functions (verify only what exists — Core rule 5)

- **E1 — `group()`**: called only for signed-in users after `identify()`, with a real group ID, and called again when the active account switches → misuse is **Fix, Medium**.
- **E2 — `track()`**: only fires when the user is identified, and isn't re-implementing page views (tracked automatically) → **Fix, Low–Medium**.
- **E3 — Identity verification (`signature`)**: if present, the signature must be computed on the backend and passed as the third argument. The Secret Key or signing logic in frontend code is **Fix, Critical** (security). If absent entirely, **Flag, Low** — recommended hardening, implement only if the customer asks.
- **E4 — Other methods** (`setCustomNavigate`, `start`, `updateUser`, `updateGroup`, `endAll`): sane usage per the Userflow.js Reference. `start()` with hardcoded content IDs that may not exist in the target environment is **Flag, Low**.

### F. Delivery

- **F1 — CSP compatibility.** If the app enforces a Content Security Policy, Userflow's domains must be allowed or nothing loads. Check the app's CSP against the [Content Security Policy doc](https://help.userflow.com/docs/content-security-policy) rather than listing domains from memory → missing directives are **Fix, High**.
- **F2 — Script-tag installs use the official snippet.** A hand-written or modified loader stub → **Fix, Medium**.

---

## Step 3 — Runtime Checks

Static reading cannot prove behavior. Have the customer confirm these in a browser, against the environment whose token is configured:

- **R1 — Public page, signed out:** `userflow.isIdentified()` returns **`false`** and the Network tab shows no identify request. **This is the MAU check — the single most important result.**
- **R2 — After sign-in:** `isIdentified()` returns `true`; the test user appears in Userflow with the expected attributes (the installation check confirms the script is detected).
- **R3 — After sign-out:** `isIdentified()` returns `false` again.
- **R4 — Environment match:** the test user appears in the *intended* environment. Appearing elsewhere confirms a B2 token cross-wire.
- **R5 — Console and Network clean:** no Userflow errors (CSP violations show here — see F1); the identify request fires once per load, not repeatedly on route changes (repeat-fire points at C6).
- **R6 — If content doesn't show** for an identified user: confirm R2 passed, the token matches the environment being viewed, and check the flow's own targeting conditions. A correct install with non-matching flow conditions is not an install defect. Do **not** "fix" missing content by adding `identifyAnonymous()` (C2).

---

## Step 4 — Report

Use this structure so results are consistent across runs:

```
# Userflow Install Verification — <project> — <date>

## Summary
Install method: <npm | script tag | mixed (defect)>   Framework: <detected>
Result: <PASS | N Critical / N High / N Medium / N Low>

## Findings
[C2][Critical][Fix] identifyAnonymous() reachable as a fallback on every load
  Evidence: src/auth/session.ts:41 — `else { userflow.identifyAnonymous() }`
  Impact: identifies every visitor → MAU overage.
  Proposed fix: remove the else-branch; unidentified users seeing no content is expected.

[B3][Medium][Fix] Token hardcoded
  Evidence: src/main.tsx:12 — `userflow.init('ct_live_…')`
  Proposed fix: move to env config; one token per environment.

[E3][Low][Flag] Identity verification not enforced
  Recommendation only — implement if the customer wants it.

## Needs runtime check
R1 public-page isIdentified() === false; R4 environment match.

## Verdict
<Correct install | Correct after listed fixes | Structurally broken — recommend
reinstall via the install-with-ai skill>
```

Order findings Critical → High → Medium → Low. Every Fix needs evidence, impact, and the proposed change. **Apply fixes only after the customer confirms each one** (Core rule 1).

If the install is tangled enough that patching is riskier than redoing it — multiple conflicting inits, mixed install methods, identification scattered across many files — say so plainly and recommend a clean reinstall via `install-with-ai` instead of heroic patching.

After applying confirmed fixes, re-run the relevant checks to confirm they landed, then update the **Userflow installation** section of `AGENTS.md` (update or append — never overwrite the file or unrelated sections).

---

## Severity Definitions

| Severity | Meaning | Examples |
|---|---|---|
| **Critical** | Costs money, corrupts data, or breaks security | Public/anonymous identification (C1–C3), cross-environment token (B2), placeholder token or values (B1, C4), Secret Key in frontend (E3) |
| **High** | Install malfunctions for real users | Duplicate init (A1), server-side calls (A3), missing reset (D1), guard skipping a new user (C6), CSP blocking load (F1) |
| **Medium** | Works today, breaks later | Hardcoded token (B3), malformed dates (C5), hand-written loader (F2), reset misuse (D2) |
| **Low** | Advisory | Changeable user ID (C4), identity verification absent (E3), missing `isIdentified()` guard (C6) |

---

## Reference

- [Userflow.js Installation](https://help.userflow.com/docs/userflowjs-installation) — install methods, placeholders, environments
- [Userflow.js Reference](https://help.userflow.com/docs/userflowjs-reference) — `init`, `identify`, `isIdentified`, `reset`, `identifyAnonymous`, `group`, `updateGroup`, `track`, `start`, `endAll`, `updateUser`, `setCustomNavigate`
- [Userflow API Reference](https://help.userflow.com/docs/userflow-api-reference) — server-side user/group registration
- [Identity verification](https://help.userflow.com/docs/identity-verification) — HMAC-SHA256 `signature`, computed on the backend
- [Content Security Policy](https://help.userflow.com/docs/content-security-policy) — required CSP directives
- [Element inference and dynamic class names](https://help.userflow.com/docs/element-inference-and-dynamic-class-names) — when flows target elements unreliably
- [Using Userflow in Angular and Shell (Micro-Frontend) Applications](https://help.userflow.com/docs/using-userflow-in-angular-and-shell-micro-frontend-applications) — multi-app placement