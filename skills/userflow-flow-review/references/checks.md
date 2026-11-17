# Flow review checks

Each check: severity (blocker > high > medium > low), certainty (definite = the signal is fully visible over MCP; likely = one input such as install or user data isn't visible; risk = heuristic, phrase as a question), how to detect it from tool output, why it breaks, how to tell the user, the fix, and when NOT to flag it.

`doc` names a help-center page by its key in `help-docs.md`; checks without one have no matching page.

Abbreviation: `GFD` = the `get_flow_details` response. `walk(c)` = visit condition `c`, then each of `c.conditions[]`, then `c.where_condition`, recursively.

How a page rule is stored: every `page` node has the operator "url" and a `url_pattern {includes, excludes}`; there is no separate negation flag. "Current page matches X" is `includes: [X]`. "Current page does not match X" is `includes: []` with `excludes: [X]`, which matches every page except X. A pattern listed in both means "matches the includes but not the excludes". Both lists empty never matches.

## Contents
- A. Start / targeting — CHK-01..24
- B. Preview — CHK-25
- C. Tooltip / element — CHK-27..32
- D. Progression / hidden steps — CHK-33..42
- E. Competition between flows — CHK-43
- F. Custom code — CHK-50
- G. Live data — CHK-48, 49, 66
- H. More configuration patterns — CHK-51..65

Every check here applies to flows (tours). Numbers skip the checks that only apply to other content types (checklists, banners, launchers, announcements, resource centers); those belong in their own review skills. Keep the numbers stable: SKILL.md refers to them.


### A. Start / targeting

### CHK-01 Not published in the environment being checked
- severity: blocker   certainty: definite
- applies_to: flow
- detect: `GFD.flow_envs` is `[]` for the reviewed `env_id` (equivalently `version_info.published_version_id == null`). If other envs exist, call `get_flow_details` once per other `env_id` and name the envs where it IS published. For many unpublished flows, `list_flows` `state` answers this without per-env calls: "draft" means published in no environment right now (it may have been live before), "published" means published in at least one. If `version_info.first_published_at` is set but it's published nowhere, say it was live once and has been unpublished — ask whether that was intentional.
- why: auto-start, visible-content and manual-start queries all require a `flow_envs` row for the current env. Preview skips this check, so preview works anyway.
- tell_the_user: "This isn't published in <env>, so nobody there can see it. Preview works because preview ignores publishing. It is published in: <list or 'nowhere'>."
- fix: Publish to the environment whose Userflow.js token your site loads.
- false_positive_guard: user said they are still building, asked "before I publish", or only asked about preview → downgrade to a note under "Before you publish", and don't count it as a blocker in a summary table.
- doc: flow-not-starting

### CHK-02 Live version differs from the draft that was reviewed
- severity: medium   certainty: definite
- applies_to: flow
- detect: `flow_envs[0].draft_dirty == true`, or `version_info.published_version_id != version_info.latest_draft_version_id` with `flow_envs` non-empty. If the two disagree (`draft_dirty` is false but the version ids differ), trust the version ids, report the unpublished changes, and mention the mismatch in one line so the user can check which is right.
- why: users get the published version; only the draft is serialized. Sessions keep the version they started on until restarted.
- tell_the_user: "There are unpublished changes. Everything below describes the draft; live users still get the older version until you publish."
- fix: Publish, or tell me to treat findings as "after publish".
- false_positive_guard: none; always state it, once.
- doc: flow-not-starting

### CHK-03 Auto-start is on but the start rule is empty
- severity: blocker   certainty: definite
- applies_to: flow
- detect: `draft.start_frequency` in {once, once_per_group, multiple, always} AND `draft.start_condition.type == "clause"` AND `draft.start_condition.conditions` is `[]`/absent.
- why: an empty top-level rule is never true. The builder refuses to save one, but flows created through the MCP or API can carry it.
- tell_the_user: "Auto-start is switched on, but the start rule has no conditions, so it never matches anyone."
- fix: Add at least one condition (e.g. a page rule), or set start to manual.
- false_positive_guard: do NOT apply to `hidden_condition` — an empty one is normal and harmless.
- doc: debugger

### CHK-05 Date window already over (or not started)
- severity: blocker   certainty: definite
- applies_to: flow
- detect: any `walk` node with `type == "time"`: `value2` parses and is <= now → expired; `value` parses and is > now → not started. Blocker only if the node sits in `start_condition`/`filter_condition` on an all-AND path; inside an `or`, or in `hidden_condition`, downgrade to medium.
- why: false before `value`, false at/after `value2`.
- tell_the_user: "This has a date rule that ended on <date>, so it can no longer show." / "...starts on <date>".
- fix: Update or remove the date rule.
- false_positive_guard: dates that can't be read are ignored — don't flag.
- doc: flow-targeting

### CHK-07 "Constrain to current company" is on
- severity: high   certainty: likely
- applies_to: flow
- detect: `draft.scope_by_group == true`. Then `list_companies {limit:1}`: `total_count == 0` → raise to blocker/definite.
- why: auto-start skips the flow when there is no current company; manual start raises "Can't start flow constrained by current group…" — this applies in preview too.
- tell_the_user: "This only runs for users who have a current company. If your app doesn't call userflow.group(), it never starts — in preview either."
- fix: Turn the setting off, or call `userflow.group(companyId)` after identify(). Nothing is shown to the user either way, so it just looks like the flow isn't starting; the same applies to a flow that another flow starts (CHK-39).
- false_positive_guard: companies exist in the env AND the user confirms group is called → note only.
- doc: flow-targeting

### CHK-08 Targeting depends on company data
- severity: high   certainty: likely
- applies_to: flow
- detect: any `walk` node in start/filter/hidden with `attribute_name` starting `group/` or `group_membership/`; or `event_actor` in {current_group, current_user_current_group}; or `type == "segment"` whose `segment_id` resolves (list_segments) to `subject_type == "company"`. `list_companies total_count == 0` → blocker/definite.
- why: with no current membership these conditions return false.
- tell_the_user: "This rule uses company data. For users with no current company it is always false."
- fix: Call `userflow.group()`, or use a user-level attribute.
- false_positive_guard: node only inside `hidden_condition` → low (flow just never hides).
- doc: flow-targeting

### CHK-09 Rule uses an attribute that doesn't exist or has a different type
- severity: high   certainty: likely
- applies_to: flow
- detect: for each `type == "attribute"` node: no definition from `list_attribute_definitions` with matching bare name AND scope (prefix none=user, `group/`, `group_membership/`) → "unknown attribute"; definition `data_type` != node `data_type` → "type mismatch", in either direction: a rule comparing text (`"true"`, `"5"`) against a boolean or number definition, or comparing true/false or a number against a string definition. The definition's type is set by what the app sends, and either choice is valid, so the rule must match the definition, not the other way round. Also flag near-miss names (case/underscore differences) against the returned list. Text comparisons are exact and case-sensitive, so an "is" rule on a value the app might send with extra spaces or different case is a question to ask.
- why: conditions read the stored value by exact name; a never-sent attribute is null, so positive comparisons never match.
- tell_the_user: "The rule checks `<name>`, which isn't an attribute in this workspace (closest: `<x>`)."
- fix: Use the exact attribute name from Settings → Attributes and compare it as the type shown there (e.g. "is true" for a boolean, the text `true` for a string); make sure the app sends it in identify(). Don't tell the user to change what their app sends unless they want to.
- false_positive_guard: negative operators (not equal / is empty) on an unknown attribute are always TRUE, not false — word accordingly. Existence of a definition does not prove users have a value.
- doc: flow-targeting

### CHK-10 Rule uses an event that isn't tracked
- severity: high   certainty: likely
- applies_to: flow
- detect: `type == "event"` node in start/filter/hidden whose `event_name` is missing from `list_event_definitions {names}` → unknown. Optional volume: `query_usage_metrics {event_name, measurement:"unique_events", last_n_days: 30}` == 0 → "defined but not received in this env".
- why: event conditions count rows by exact name in this env; zero rows makes ">= 1" false forever.
- tell_the_user: "The start rule waits for event `<name>`, which this environment has never received."
- fix: Match the exact event name the app sends via userflow.track(), in this environment.
- false_positive_guard: "has not done event" style (`event_frequency_operator` eq/lte 0) is always true when untracked. Event nodes in triggers/buttons belong to CHK-34.
- doc: flow-targeting

### CHK-11 Rule uses a segment that is missing, archived or possibly the wrong one
- severity: high   certainty: likely
- applies_to: flow
- detect: `type == "segment"` node: (a) `segment_id` absent or not in `list_segments` → definite false; (b) `is_archived == true` → risk; (c) another segment with a near-identical name exists → low note "confirm it's the right one"; (d) `source_type` is manual/integration → note membership is per environment.
- why: a missing segment is always false; manual segment membership is stored per environment.
- tell_the_user: "The rule points at segment '<name>', which <no longer exists / is archived / has a near-twin '<other>'>."
- fix: Re-select the intended segment.
- false_positive_guard: "is NOT in segment" on a missing segment is still false in the code path (nil → false) — keep as finding.
- doc: flow-targeting

### CHK-12 Depends on another flow that is gone or can never be "completed"
- severity: high   certainty: definite
- applies_to: flow
- detect: `type == "flow"` node: (a) `flow_id` absent → always false; (b) `flow_state == "completed"` and target `GFD.draft.steps[]` has no `is_goal == true` → never true; (c) target `flow_envs == []` in this env → never true for live users.
- why: a missing flow is always false; "completed" is only recorded when a user reaches a goal step.
- tell_the_user: "This waits for '<other flow>' to be completed, but that flow has no goal step, so nobody ever counts as completing it."
- fix: Mark the other flow's final step as a goal, or use "has seen".
- false_positive_guard: (b) reviews the target's draft; if the target has unpublished changes say "check the live version".
- doc: flow-targeting

### CHK-13 Page rule cannot match, or is unlikely to
- severity: high   certainty: risk
- applies_to: flow
- detect: for each `type == "page"` node with `url_pattern`, per `includes` string: (a) `includes == [] && excludes == []` → DEFINITE false, blocker on an AND path; (b) contains scheme/hostname → "only matches that domain" (compare with other envs); (c) path with no `*` and no trailing variant → exact path only (`/dashboard` ≠ `/dashboard/`, ≠ `/dashboard/settings`; a `?query` or `#` part on the address is still allowed when the pattern has none); (d) uppercase letters → case-sensitive; (e) a locale-looking segment (`/en/`, `/nl-NL/`) hard-coded; (f) two page nodes under AND with different paths → impossible; (g) a pattern with no scheme whose first part (before any `/`, `?` or `#`) has no `.`, `*` or `:` and isn't `localhost` (e.g. `dashboard`, `dashboard/settings`) → Userflow reads that word as a domain name, so it only matches a site whose address is literally that word: in practice never. DEFINITE, blocker on an AND path. The builder and the MCP both save the pattern as typed (no `/` is added), and the builder shows a warning only when a path follows the word, not for a bare word. Don't flag a real domain without a scheme (`app.example.com/dashboard`); (h) a literal id or slug that changes per record (`/projects/48213`) → use `:param` or `*`; (i) a full address with a query string (`?tab=2`), which varies per visit (query parameters in a pattern must all be present, in any order); (j) an app that routes with `#` keeps the same path on every screen, so a pattern without the `#` part matches all of them — add the `#…` part to target one screen; (k) `*` in the path matches any characters including `/`, but not the `?query` or `#` part, so `/projects*` covers `/projects/12/settings`; (l) `:param` matches exactly one path segment with any value (including `_`) and can't be tied to a user attribute, so `/app/:slug/flows` matches `/app/_/flows` and `/app/acme/flows` but not `/app/flows`; (m) a domain inside the pattern pins it to that domain.
- why: a page rule has to match the whole address, case-sensitively; an empty pattern never matches.
- tell_the_user: "The page rule `/dashboard` only matches exactly that address — not `/dashboard/` or pages under it."
- fix: Use path-only patterns with wildcards (`/dashboard*`, `/projects/*`, `/:lang/pricing`).
- false_positive_guard: exact paths are often intended — phrase as a question unless (a), (f) or (g). Don't flag a `:param` segment for matching a placeholder value such as `_` in a real address; it matches any single segment.
- doc: flow-not-starting

### CHK-14 Starts on a page or element but nothing hides it elsewhere
- severity: high   certainty: definite
- applies_to: flow
- detect: `draft.start_condition` contains a `page` or an `element` node. Check the hide rule (`draft.hidden_condition`) against it:
  - (a) start rule has a `page` node and the hide rule has no `page` node written as "does not match" the same page(s) (`includes: []`, the start pages in `excludes`) → finding. A hide rule written as plain "matches" (the pages in `includes`) does not count; that is CHK-23(e).
  - (b) start rule has an `element` node with `element_state` present and the hide rule has no `element` node "not present" on the SAME selector → finding. If the hide rule's selector differs from the start selector, say so.
  - Severity high when any step is `appearance == "tooltip"` (the tooltip loses its target on other pages); medium otherwise.
- why: the start rule is only checked when the flow starts; once it is running, only the "temporarily hide" rule is re-checked. The flow therefore follows the user to every page, and tooltips then lose their target. This is the most common cause of a high "element not found" rate on a single tooltip.
- tell_the_user: "The page rule only decides where it starts. Once started it stays on screen on every page until closed; tooltip steps will report 'element not found' there." / "It starts when <element> is on the page, but nothing hides it when that element is gone."
- fix: Add a "Temporarily hide flow if" rule: Current page does not match <same page or pattern as the start rule>, or Element is not present <same element as the start rule or the tooltip target>.
- false_positive_guard: flows that deliberately walk across pages — then the hide rule must cover every page of the tour (CHK-23). A flow started from a button, launcher or link that should follow the user. A modal or bubble that is fine anywhere → low. A negated page hide rule that already covers the pages without the element.
- doc: flow-not-starting

### CHK-16 Page pattern stored on the flow itself has no effect
- severity: low   certainty: definite
- applies_to: flow
- detect: `draft.url_pattern` present with non-empty includes/excludes on the flow.
- why: only launchers read a page pattern stored on the flow itself; for a flow it is ignored, so use a page condition in the start rule instead.
- tell_the_user: "A page pattern is saved on this flow but isn't used; it will show regardless of page."
- fix: Put the page rule in the start rule (and a hide rule, CHK-14).
- false_positive_guard: none.
- doc: flow-not-starting

### CHK-17 "Current screen" rule (mobile-only)
- severity: high   certainty: likely
- applies_to: flow
- detect: any `walk` node `type == "screen"` in start/filter/hidden. (In triggers/buttons → CHK-34.)
- why: it matches against the React Native screen name; an empty one never matches. The MCP doesn't show the target platform.
- tell_the_user: "This uses a mobile 'screen' rule. On a website it is always false."
- fix: Use a page rule for web flows.
- false_positive_guard: user confirms it is a React Native flow.
- doc: flow-targeting

### CHK-18 Starts when an element is present or clicked
- severity: medium   certainty: risk
- applies_to: flow
- detect: `draft.start_condition` (or filter/hidden) contains `type` in {element, input_value, filled_in_input}. Raise to high if it is the only condition (no page node alongside) or its `selector` trips CHK-28.
- why: element conditions are reported by the browser; until reported the result is "unknown" and treated as not-true. The flow can also start on an earlier page where the selector matches and then persist (CHK-14).
- tell_the_user: "Starting depends on finding an element. If that element is dynamic, slow to appear, inside an iframe, or also exists on other pages, it will start at the wrong time or not at all."
- fix: Combine with a page rule and a hide rule (CHK-14); use a stable manual selector; add a short wait.
- false_positive_guard: stable selector (id / data-attribute) AND a page node on the same AND path → low. A tooltip meant only for users who have a certain element is correctly started this way: don't blame the element rule, check CHK-14 instead.
- Also: if the start rule is an element `click` (or an event) with the default frequency, say that auto-start fires once per user and not again on later clicks. For "start every time the user clicks", use a hidden launcher on the element, `userflow.start()` from code, or an unlimited frequency with a gap.
- doc: debugger

### CHK-19 Manual start only, with no visible way to start it
- severity: medium   certainty: risk
- applies_to: flow
- detect: `draft.start_frequency` absent or "never" AND no other reviewed flow has an action with `other_flow_id == this id`. Launcher / checklist / resource-center links are not readable, so always phrase as a question.
- why: `never` flows are excluded from auto-start. A trigger on a hidden first step is not a start rule, and a link or button that points at an unpublished flow never starts it.
- tell_the_user: "This never starts by itself. How should users start it — a launcher, checklist, resource center, link or userflow.start()? (I can't see those.)"
- fix: Turn on auto-start with a rule, or wire up a launcher / checklist task.
- false_positive_guard: user already named the entry point; or the flow is published and `query_flow_metrics` shows sessions in the last 30 days — something is starting it, so no finding. Published with zero sessions in the window is a fact, not a guess: put it under "Should fix" and say nothing is starting it (CHK-48); only the cause stays a question.
- doc: flow-not-starting

### CHK-20 "Once per user" / start limit is used up by any earlier start
- severity: low   certainty: definite
- applies_to: flow
- detect: `draft.start_frequency` in {once, once_per_group, multiple}. Report as context whenever the complaint is "doesn't show for me / for some users / can't re-test".
- why: the per-user count includes every non-preview session however it started; `once` blocks at count > 0, `multiple` at `start_limit`. Republishing does not reset it.
- tell_the_user: "Anyone who has already seen this once — including via a link or a launcher — won't get it automatically again. That includes your own test user."
- fix: To retest, delete the session on the user's page or use a fresh test user; switch to "multiple times" if repeats are wanted.
- false_positive_guard: informational; don't present as a defect.
- doc: dismiss-snooze-restart

### CHK-21 Repeats with no spacing — reopens right after closing
- severity: high   certainty: likely
- applies_to: flow
- detect: `draft.start_frequency` in {always, multiple} AND (`start_interval_value` absent or 0, or `start_interval_unit` absent) AND (`throttle_value` absent or 0, or `throttle_unit` absent) AND NOT (`only_start_if_not_completed == true` AND some step `is_goal == true`).
- why: ending a flow immediately re-runs the start check; `always` has no cap and an empty interval or throttle allows an instant restart. If the start rule still matches, it starts again.
- tell_the_user: "It's set to start every time with no minimum gap, so if its start rule is still true when a user closes it, it comes straight back — and because only one flow runs at a time, it can keep other flows from showing."
- fix: Set "at least X apart" (e.g. 1 day), or use once per user.
- false_positive_guard: start rule is a one-shot signal (element `click`, event within last minute) → downgrade to low. The builder legitimately allows interval 0.
- doc: dismiss-snooze-restart

### CHK-22 "Only if not completed" can't take effect
- severity: medium   certainty: definite
- applies_to: flow
- detect: `draft.only_start_if_not_completed == true` AND (`start_frequency` not in {multiple, always} OR no step has `is_goal == true`).
- why: the check is gated on multiple/always and reads `completed`, which needs a goal step.
- tell_the_user: "'Only if not completed' is on, but <this frequency ignores it / no step is marked as the goal>, so it has no effect."
- fix: Mark the final step as goal; use it with multiple/always.
- Also: "only if not completed" with the goal on a step that a "remind me later" or dismiss button leads to, or on the last step → a user who reaches it never sees the flow again. Don't mark a "later" step as the goal.
- false_positive_guard: none.
- doc: dismiss-snooze-restart

### CHK-23 "Temporarily hide" rule overlaps where the flow should run
- severity: high   certainty: likely (blocker and definite for (a), (b) and (e) when the hide rule is true wherever the start rule is: the flow can never show)
- applies_to: flow
- detect: `draft.hidden_condition` non-empty AND any of: (a) it is structurally the same as `start_condition`; (b) it has a `page` node whose `includes` equal the start rule's `includes` (not negated; a negated page node has `includes: []` and the pages in `excludes`); (c) it has an `element` node (`element_state` not_present / present) while the flow has a `navigate` action or tooltip steps with different selectors (the element disappears mid-flow); (d) a `wait_time` on it (ignored); (e) a `page` node that is NOT negated and equals the page where the flow should show (it hides the flow exactly where it should appear); (f) several unrelated conditions joined with AND where the intent is "hide if any is true" (AND only hides when all are true; use OR); (g) an `element` present node on an element that is on the page all the time (hides the flow permanently).
- why: auto-start requires the hide rule to be false, and a running flow is hidden whenever it becomes true — the whole flow, on every step.
- tell_the_user: "The hide rule is true on the page where this should run, so it never appears." / "The hide rule depends on an element that disappears after step N, so the rest of the flow vanishes."
- fix: Make the hide rule true only where the flow must not show; cover every page the tour visits.
- false_positive_guard: negated page rule ("does not match" the start page: `includes: []`, start page in `excludes`) is the recommended pattern — don't flag. An `element` "not present" node on the SAME selector as the start rule or the tooltip target is also the recommended pattern (CHK-14) — don't flag (c) for it. AND is right when the conditions describe one situation (page AND device).
- doc: flow-not-starting

### CHK-24 "Wait N seconds" placed where it is ignored
- severity: low   certainty: definite
- applies_to: flow
- detect: `wait_time` present on `filter_condition`, `hidden_condition`, or on a nested (non-root) node of `start_condition`.
- why: the wait is applied only to the top-level `start_condition`.
- tell_the_user: "The delay is set on a rule that doesn't support it, so there is no delay."
- fix: Put the wait on the top-level start rule, or use a hidden first step with a time trigger.
- false_positive_guard: `wait_time` on trigger conditions is supported client-side.
- doc: debugger

### B. Preview

### CHK-25 Preview does not test the start rules
- severity: low   certainty: definite
- applies_to: flow
- detect: `start_frequency` is auto AND (`flow_envs == []` OR user reports "works in preview"). Emit once per review: in "Can't check from here" for one flow, or in "Across these flows" for several.
- why: preview starts the draft directly, skipping publish, start rule, frequency and platform checks.
- tell_the_user: "Preview force-starts the flow. It tells you nothing about whether real users will get it."
- also say: preview ignores start rules and frequency but does evaluate hide rules (a hide rule that matches your own test email makes the flow vanish), a leftover preview tab or session can start flows or show "tooltip missing" messages, and a test user has none of the real attributes. A preview session stays active until it is closed.
- fix: Publish to a test environment and use the debugger's "Check auto-start" as a real user.
- false_positive_guard: informational.
- doc: flow-not-starting

### C. Tooltip / element

### CHK-27 Tooltip step whose element was never picked or can never match
- severity: blocker   certainty: definite
- applies_to: flow
- detect: step `appearance == "tooltip"` AND one of: `selector` absent; `selector.type == "auto"` with no `auto_data`; `selector.type == "manual"` with `text` longer than 250 chars; `selector.type == "manual"` with neither `css` nor `text`. Same test on `beacons[].selector` (medium).
- why: an automatic selector without its stored data is treated as missing right away; text over 250 characters never matches.
- tell_the_user: "Step N is a tooltip but no element was selected, so it reports 'element not found' for everyone."
- fix: Select the element in the builder, or change the step to a modal / speech bubble.
- false_positive_guard: none.
- doc: element-not-found

### CHK-28 Fragile element selector
- severity: medium   certainty: risk
- applies_to: flow
- detect: for every selector (steps, beacons, element conditions): (a) `type == "auto"` → "automatic selector; can't judge, breaks when page text/structure changes"; (b) `css` contains hashed/generated classes (`css-[a-z0-9]{5,}`, `sc-…`, `jss\d+`, `_[a-z0-9]{5,}`), `:nth-child`/`:nth-of-type`, more than 4 combinators, or an id with 4+ digits; (c) `text` contains digits, `@`, currency, or is > 40 chars (dynamic content); (d) `offset` set (position-dependent); (e) `near_selector` set (two elements must exist); (f) `minor_version` absent or < 2 on a manual selector (searches the main page only, not iframes or shadow DOM). The MCP returns `minor_version` whenever it is set, so absent means unset, which Userflow.js treats as 1. Selectors created through the MCP often lack it; (g) `text` set, no `css`, and the text is one or two common words ("Publish", "Save", "Next") → may attach to another element with the same text; (h) `text` set, `exclude_text` not true (the builder's "Dynamic text" box is off) and no `css` → the visible text is the only handle, so it breaks when wording changes, differs per user or language, or the page is translated; ask whether the text is dynamic and, if so, tell them to tick Dynamic text or switch to a stable id or data attribute. The box only exists when the selector has text.
- why: text must equal the element's whole text; only visible elements count; out-of-range `offset` finds nothing; old manual selectors skip iframes/shadow roots.
- tell_the_user: "Step N finds its element by <reason>, which tends to break when the page changes or differs per user."
- fix: Use a manual selector on a stable id or data attribute; turn on Dynamic text for changing text; avoid "nth match". If a tooltip suddenly stopped after an app release, re-pick the element.
- false_positive_guard: `css` is a plain `#id`, `[data-*]`, `[aria-label]` or single semantic class with no text → no finding. Cap at 5 findings per flow, then summarize.
- doc: element-not-found

### CHK-29 Tooltip appears right after a page change with nothing waiting for it
- severity: medium   certainty: risk
- applies_to: flow
- detect: step S (`tooltip`) is the `step_cvid` target of an action list that also contains `navigate`, OR of a trigger whose condition is element `click` on an element that loads a new page; AND the path into S has no intermediate hidden step / no trigger with `element present` on the destination. A trigger with only a `page` condition doesn't count as waiting: the page can match before the element has loaded. Also: consecutive tooltip steps whose selectors differ with only a button `go_to_step` between them after a `navigate`.
- Also: S's target only exists after an interaction the user still has to make (open a record, select an item, open a menu) and S is reached from a Next button that only has `go_to_step` — nothing waits for that interaction; or a button only has `go_to_step` but the next step's element is on another page (add `navigate` before it, or an element-present trigger on the destination).
- why: a tooltip renders nothing until its target exists and is declared missing after the theme's tolerance (5 seconds on a new theme, 3 on some older themes, 10 at most); slow pages / SPAs exceed it. A tooltip can't open a closed menu for the user.
- tell_the_user: "Step N points at something on the next screen. If that screen loads slowly, the step gives up before the element appears (after 5 seconds on a new theme)."
- fix: Insert a hidden step that waits for "element is present" (or page matches) before the tooltip; raise the theme's missing-element tolerance; for a closed menu, make the previous step wait for the click on the opener.
- false_positive_guard: destination step is modal/bubble → no finding. S reached from the previous tooltip's own click (its `actions`), where that click opens a menu, dropdown or panel on the same page → no finding: the menu appears well within the tolerance. Raise it only if the click loads a new page or data. An element that navigates by itself when clicked doesn't need a navigate action; use an element-present trigger on the destination instead. A hidden element-present step in the middle of a flow, before a late-loading tooltip, is the recommended fix, not a finding (CHK-35 applies only to a hidden first step).
- doc: step-timeouts

### CHK-30 Live data: users are hitting "element not found"
- severity: high   certainty: definite
- applies_to: flow (published)
- detect: step 6 `query_usage_metrics` on `tooltip_target_missing` returns count > 0 for this flow. Compare per step: each step's count against that step's views from the `query_flow_metrics` step funnel; use the flow's total views only when the step funnel is missing, and say so. Ratio >= 20% → high; 5–20% → medium; lower → low. Name the worst steps with both numbers ("7 of 63 views").
- why: each missing target is reported once per step and written as a `tooltip_target_missing` event; with theme behavior "end" the flow is then ended.
- tell_the_user: "In the last 30 days, <n> of <m> sessions couldn't find the element on step '<name>'."
- fix: CHK-14 hide rule, CHK-28 selector, CHK-29 wait step — whichever applies to that step.
- false_positive_guard: no sessions in window → skip silently. Preview sessions also report missing targets, so if the count is very small say it may be test traffic.
- doc: tooltip-target-behavior

### CHK-31 Element is blocked but the step waits for a click on it
- severity: high   certainty: likely
- applies_to: flow
- detect: step `appearance == "tooltip"` AND `tooltip_target_blocked == true` AND (step `actions` non-empty OR a trigger with element `element_state == "click"`) AND no button with a `go_to_step`/`close_flow` action.
- why: with blocking on, the backdrop keeps pointer events and swallows mousedown, so the click that should advance never reaches the element.
- tell_the_user: "Step N asks the user to click the highlighted element, but the element is set to be blocked from clicks."
- fix: Turn off "block target clicks", or add a Next button. Make sure the highlighted element is the exact element users click, not a container around it.
- false_positive_guard: `backdrop_mode` absent → downgrade to risk.

### CHK-32 Click rule uses "nth match" / "near element", which clicks ignore
- severity: low   certainty: definite
- applies_to: flow
- detect: element condition with `element_state` in {click, mousedown, not_click} whose `selector` has `offset` or `near_selector`.
- why: click matching ignores both and accepts any element (or ancestor) matching css/text.
- tell_the_user: "This reacts to a click on any element matching the selector, not just the Nth one."
- fix: Give the element a unique selector.
- false_positive_guard: none.
- doc: element-not-found

### D. Progression / hidden steps

### CHK-33 Hidden step with no trigger
- severity: blocker   certainty: definite
- applies_to: flow
- detect: step `appearance == "hidden"` AND (a) `triggers == []`, or every trigger has `actions == []`; or (b) the step is the last on its path (or the flow's only step) and none of its triggers has `close_flow`, a `go_to_step` to a visible step, or `start_flow` — a trigger whose actions are only `navigate` or an attribute update still leaves the user parked on the step. Blocker for (a), and for (b) when the flow is a single hidden step.
- why: hidden steps render nothing and move only via triggers. The builder requires one, but flows created through the MCP or API may lack it. The session stays active and invisible, and an active flow blocks every other auto-start.
- tell_the_user: "Step N is hidden and has nothing that moves it on or ends the flow. Users get stuck there without seeing anything, and no other flow can start for them."
- fix: On the hidden step add a trigger (always, or after a short wait) with the action "Dismiss flow"; for a hand-off use "Start flow"; or go to the next step.
- false_positive_guard: none. (Because unreachable steps are rejected on save, this step is always a terminal step.)
- doc: hidden-steps

### CHK-34 Step trigger or button rule of a kind that never fires in the browser
- severity: blocker   certainty: definite
- applies_to: flow
- detect: any `walk` node with `type` in {event, segment, flow, screen, checklist_task_clicked} inside `steps[].triggers[].condition`, `buttons[].hidden_condition`, `buttons[].disabled_condition`, `beacons[].hidden_condition`. Blocker when on an AND path of the only exit of a hidden step; otherwise high. A clause that is `or` with another satisfiable branch → medium.
- why: these slots are evaluated in the user's browser; event, segment, screen and checklist conditions are always false there, and flow conditions never resolve. They can still be saved, including through the MCP or API.
- tell_the_user: "Step N waits for <an event / segment / another flow>. Steps can't react to those, so it never moves on."
- fix: Have the app set a user attribute and trigger on that, or use a page / element trigger.
- false_positive_guard: same types in start/filter/hidden conditions are fine (they are checked before the flow starts).
- doc: hidden-steps

### CHK-35 Hidden step that waits only on the page or an element, with no fallback
- severity: medium   certainty: risk
- applies_to: flow
- detect: `appearance == "hidden"` AND every trigger condition is element/page/input based AND no trigger has a `time`/`always_true` fallback or a `close_flow` branch. Raise to high when it is the FIRST step of an auto-start flow (users "start" it invisibly and it holds the slot).
- why: if the element/page never appears the session waits forever, invisibly, blocking other auto-starts and boosted announcements.
- tell_the_user: "Step N silently waits for <condition>. If that never happens the user is stuck in an invisible flow and gets nothing else."
- Also (attribute branches): a hidden step whose triggers are all attribute conditions with "is" on exact values (roles, time zones, plans) and no catch-all → a value outside the list matches no branch and the user is stuck; typos and look-alike characters (a hyphen vs a dash) are a variant. Add a final trigger that is always true and leads to a fallback step or Dismiss flow.
- fix: Add a second trigger: after N seconds → dismiss flow; tighten the start rule so the flow only starts where the element exists. For a FIRST hidden step that waits for an element, move "Element is present" into the start rule (with a page rule) and make the first step visible.
- false_positive_guard: flow has a `hidden_condition` that hides it off-page → medium stays, wording softer. Triggers that together cover every state (one waits for X present / true, another for X not present / false) always have one that fires → no finding. A trigger of a type from CHK-34 belongs to CHK-34, not here.
- doc: hidden-steps

### CHK-36 Dead-end step
- severity: blocker   certainty: definite
- applies_to: flow
- detect: visible step (modal/bubble/tooltip) where: no button has a non-empty `actions`; `triggers == []`; no question has `actions`; and (not tooltip or step `actions == []`). If `draft.close_disabled == true` → blocker (user is trapped). If close is allowed and the step is not a goal → medium ("only exit is the X; counts as abandoned"). Also flow-level: `close_disabled == true` AND no action of type `close_flow`/`snooze`/`start_flow` anywhere AND the terminal steps have no buttons → blocker.
- Also with `close_disabled == true`: the LAST visible step must have a `close_flow` action, and every other step a forward action.
- why: steps advance only via button/trigger/question/target-click actions; "Prevent users from closing" removes the X and disables Escape and backdrop close, which is usually why a bubble or modal has no X.
- tell_the_user: "Step N has no button or trigger that leaves it, and closing is disabled — users cannot get out."
- fix: Add a button with "Dismiss flow" (or go to step); turn off "prevent closing", then republish. The theme can also hide the X or ignore backdrop clicks; that isn't readable here.
- false_positive_guard: final goal step with close allowed (a thank-you step) → no finding. With close allowed, any action counts as an exit: `go_to_step`, `close_flow`, `snooze`, `start_flow`, `navigate`. With `close_disabled == true`, a `navigate` alone is not an exit: the flow stays on the step (a new tab leaves it open behind; the same tab shows it again on the next page, CHK-42).

### CHK-37 Button or action that does nothing
- severity: high   certainty: definite
- applies_to: flow
- detect: (a) button with `actions == []`; (b) action `type == "snooze"` with `time_value` 0/absent or `time_unit` absent; (c) `type == "navigate"` with no `url`; (d) `type == "start_flow"` with no `other_flow_id`; (e) `type == "go_to_step"` whose `step_cvid` is not a `cross_version_id` in this draft. High if it is the step's only exit, else medium.
- why: a button with no actions does nothing; snooze needs both a time and a unit; a navigate with no address or a start-flow with no target does nothing.
- tell_the_user: "The '<text>' button on step N has no action, so clicking it does nothing."
- fix: Give the button an action.
- false_positive_guard: survey steps advance through `questions[].actions`, not buttons — a question step with no buttons is fine.

### CHK-38 Trigger is already true when the step appears — step gets skipped
- severity: medium   certainty: risk
- applies_to: flow
- detect: on a visible step, a trigger whose actions include `go_to_step`/`close_flow`/`start_flow` and whose condition is: (a) `page` matching the same pattern as the flow's start rule; (b) element `present` using the SAME selector as this step's tooltip target or the previous step's; (c) `input_value` "is empty"; (d) element `not_present`; (e) `always_true` with no `wait_time`. Also two triggers on one step with element-present conditions on similar selectors ("always lands on the same branch"). Also a Back button: a button that goes back to an earlier step whose own forward trigger is already true on the current page (e.g. "page matches /settings*" while the user is still there) — the earlier step fires at once and bounces the user forward again, so Back seems to do nothing.
- why: triggers mount with the step and fire the first time the condition is true, including immediately.
- tell_the_user: "Step N has a trigger that is probably already true when the step opens, so users jump past it without seeing it (on a single-step flow, the flow ends the moment it starts)."
- fix: Trigger on something that changes (a click, a different page, an element unique to the next state).
- false_positive_guard: hidden branching steps are meant to fire immediately — only flag visible steps. Skip (b) and (d) when every path into the step already required that element state (an earlier trigger checked it), since firing at once is then the intended branch.
- doc: flow-not-starting

### CHK-39 "Start another flow" action problems
- severity: high   certainty: definite
- applies_to: flow
- detect: each action `type == "start_flow"` with `other_flow_id` → target `GFD`: (a) `flow_envs == []` in this env → nothing starts (definite, high); (b) target `draft.scope_by_group == true` → CHK-07 applies to the hand-off; (c) target has non-empty `hidden_condition` → may start hidden (high, likely; when the hide rule depends on attributes or the page, ask whether it is true where this button is clicked); (d) `other_flow_step_cvid` not among target `steps[].cross_version_id` → silently starts at step 1, or set to a later step → users skip the intro ; (e) always add the note: the current flow ends when this fires, and the target's start rule is NOT checked; (f) the flow that started it is replaced, so a way back needs its own start button; (g) the target's start rule is "flow completed" and it has no page hide rule → it appears on the page where the first one ended. A link or button that points at an unpublished flow starts nothing.
- why: starting another flow ends the current one first; a target that isn't published then doesn't start; an unknown step falls back to the first step.
- tell_the_user: "The '<text>' button starts '<other flow>', which isn't published here — the click closes this flow and nothing opens."
- fix: Publish the target in the same environment; or drop the action and let the second flow auto-start on "has seen <first flow>".
- false_positive_guard: preview starts the target's draft, so this passes in preview.

### CHK-40 No goal step — the flow never counts as completed
- severity: medium   certainty: definite
- applies_to: flow
- detect: no step has `is_goal == true`. This includes a single-step flow whose button only starts another flow. Also: (a) a flow with one visible step and the goal on step 1 counts as completed on view, so to count a click add a hidden second step as the goal — raise (a) only when something depends on "completed" (another flow's `flow` condition, `only_start_if_not_completed`, a checklist task, or the user asked about completion) or the step's button does more than dismiss (starts a flow, navigates, runs code); medium when something depends on it, otherwise low; for a plain "Got it" step it is not a finding; (b) the goal is a tooltip step, which counts even if its target never showed; (c) a step after the goal can complete a checklist task early; a dismissed flow is not completed. Separately, if the goal step has visible steps after it on the main path, add a low note: "completion counts at step N; the steps after it aren't counted — intended?". Raise to high if `only_start_if_not_completed == true`, or another reviewed flow has a `flow` condition `completed` on this one (CHK-12, CHK-22).
- why: `completed_at` is set only when the session lands on a step with `is_goal`. The builder marks implicit goals on terminal steps and stores them as `is_goal: true`; MCP/API drafts get none unless set.
- tell_the_user: "No step is marked as the goal, so completion will read 0% and anything that waits for 'completed' never fires."
- fix: Mark the final step as goal (opening and saving the flow in the builder also does this automatically).
- false_positive_guard: `is_implicit_goal: true` comes with `is_goal: true` — that counts as a goal.
- doc: dismiss-snooze-restart

### CHK-41 Attribute-based branch that probably can't match
- severity: medium   certainty: risk
- applies_to: flow
- detect: trigger `attribute` node: `data_type` absent or != definition `data_type` (CHK-09 lookup); or the attribute equals a question's `bind_attribute_fqn` on the SAME step with operator comparing to a value not among that question's `options[].value`.
- why: step triggers compare against the session's attribute snapshot in the browser; wrong type/values never match.
- tell_the_user: "The branch on step N compares '<attr>' with a value that the question can't produce."
- fix: Match the trigger value/type to the question's options.
- false_positive_guard: free-text questions.
- doc: flow-targeting

### CHK-42 Last step's button only navigates
- severity: low   certainty: risk
- applies_to: flow
- detect: a button whose actions are only `navigate` (`navigate_target` same tab or absent) with no `go_to_step`/`close_flow`, on a step with no other exit.
- why: navigation does not end or advance the flow; the same step reappears on the destination page (session resumes at the current step), and a tooltip there loses its target.
- tell_the_user: "The button sends users to another page but leaves the flow on this step, so it reappears there."
- fix: Add "Dismiss flow" or "Go to step" before the navigate action.
- false_positive_guard: `navigate_target == "new_tab"`.

### E. Competition between flows

### CHK-43 Several auto-start flows for the same audience, no throttle
- severity: medium   certainty: risk
- applies_to: flow
- detect: (step 5 competition scan) this flow auto-starts AND >= 1 other published auto-start flow has a start rule that is not obviously disjoint (same page pattern, or no page node) AND this flow has no `throttle_value`/`throttle_unit`. Report count and names; note `priority` values.
- why: only one flow runs at a time and nothing interrupts it; flows a user has never seen come first, then the least recently seen, and only then priority; without a throttle the next one starts as soon as the first closes.
- tell_the_user: "<n> other auto-start flows can match the same users. Only one shows at a time; priority is only a tie-breaker; without a throttle they pop up back to back."
- fix: Set "at least X after any other flow"; make audiences disjoint; keep auto-start flows short with a clear exit.
- Also: published copies or duplicates of the flow (same name prefix or a structurally identical start rule and page) show in turn, so a flow can seem to start twice. Name them. Certainty is definite when the start rules are identical (put it under "Should fix"), and likely when only the name matches.
- false_positive_guard: scan was capped — say "at least". Different priorities or a distinguishing condition.
- doc: debugger

### F. Custom code

### CHK-50 Button or action runs custom JavaScript
- severity: low   certainty: risk (raised below)
- applies_to: flow
- detect: any action with `type == "eval_js"` in `steps[].buttons[].actions`, `steps[].triggers[].actions`, `steps[].actions` or `steps[].questions[].actions`. Read its `code`:
  - (a) `code` empty or only whitespace → the action does nothing; treat like CHK-37 (high if it's the step's only exit, else medium), certainty definite.
  - (b) an attribute placeholder `{{name}}` that isn't wrapped in quotes or backticks (e.g. `openForm({{plan}})`) → the code breaks for text values; medium, definite. A placeholder for a multi-line text attribute inside single or double quotes → breaks when the answer has a line break; medium, likely.
  - (c) code that depends on your page (`document.querySelector(...)`, a global from your app) with nothing guarding a missing result (`?.`, `if`) → throws when that element or object isn't there; low, risk.
  - (d) code reads user attributes as plain variables instead of `{{placeholder}}`, or uses company attributes (only user attributes are available as placeholders) → medium, likely; (e) `addEventListener` inside the action (it runs once on the click, so the listener never fires; call the function directly, e.g. `window.open(url)`) → medium, likely; (f) a third-party widget opener with no Dismiss or go-to-step beside it → low, risk.
  - Raise any of these to medium when the `eval_js` action is the only action on a step's only exit (no `go_to_step`, `close_flow` or `start_flow` beside it).
- why: the code runs in the end user's page. A Content Security Policy that blocks it, a syntax error, or a missing element makes the action fail silently, and the flow can't tell.
- tell_the_user: "The '<text>' button on step N runs custom JavaScript (`<first 60 chars of code>`). <the specific problem>. If the code fails, the button does nothing. Test it on the live page."
- fix: Wrap attribute placeholders in quotes (backticks for multi-line text); guard page lookups; pair the code with a normal action (go to step or dismiss) so the user can move on even if it fails; check the browser console for CSP errors.
- false_positive_guard: none for (a), (b), (d) and (e). For (c), keep it in "Worth a look" unless it is the only exit. Code that matches none of (a)–(c) and sits beside another action (e.g. `navigator.clipboard.writeText(...)` plus go to step) gets one low "test it on the live page" line; when many flows share it, say it once in "Across these flows".
- doc: enhanced-javascript

### G. Install / runtime (data-driven)

### CHK-48 Published, but nobody has seen it
- severity: high   certainty: likely
- applies_to: flow
- detect: `flow_envs` non-empty AND views == 0 in the last 30 days AND `version_info.first_published_at` older than 2 days.
- why: no single rule — it means no user in this env has satisfied publish + audience + install together.
- tell_the_user: "It has been live since <date> with zero views in the last 30 days. Either nobody matches the rules above, or the site isn't loading Userflow with this environment's token / identifying users."
- fix: Work through the targeting findings first; then the install questions in "Cannot verify".
- false_positive_guard: very recent publish. For a manual-start flow, report it under CHK-19 instead and cite the zero views as evidence that nothing is starting it. If it was first published more than 30 days ago, also name it in the stale list (CHK-66), without writing a second finding.
- doc: install-check

### CHK-49 Live funnel shows users stalling at one step
- severity: medium   certainty: likely
- applies_to: flow (published)
- detect: `query_flow_metrics` step funnel (`include_steps: true`): a step loses >= 60% of the users who reached it, or completion rate is 0 with sessions >= 20. Cross-reference the step with CHK-27..CHK-38 findings; if CHK-40 fired, say the 0% is explained by the missing goal.
- why: evidence, not a rule; localizes which step's configuration to look at.
- tell_the_user: "<p>% of users who reach step '<name>' never get past it."
- fix: See the findings on that step.
- false_positive_guard: single-step flows; fewer than 20 sessions. The step funnel covers the current version's steps, but session and completion totals include older versions. If completions exist while the goal steps show 0 views, say under "Worth a look" that the completions probably come from an older version and may drop.

### CHK-66 Stale: no views or no completions in the last 30 days
- severity: medium   certainty: definite (high for an auto-start flow with 0 views)
- applies_to: flow (published)
- detect: from Step 5 (`query_flow_metrics`, last 30 days), a flow published in this environment for more than 30 days (`version_info.first_published_at`) with (a) 0 views in the last 30 days, or (b) 0 completions in the last 30 days.
- why: a live flow nobody sees or nobody finishes is either broken (a rule, a selector, the install) or no longer needed. Either way it needs a decision.
- tell_the_user: "<Flow> has had <0 views / 0 completions from N views> in the last 30 days."
- fix: For 0 views, work through the start-rule findings and the install questions (CHK-48); for 0 completions, look at the goal step (CHK-40) and where users drop (CHK-49). If the flow isn't needed any more, unpublish or archive it.
- false_positive_guard: published 30 days ago or less → don't judge yet. For (a), the finding itself is CHK-48 (or CHK-19 for a manual-start flow); here just name the flow in the stale list, so it isn't reported twice. 0 completions on a flow with no goal step (but some views) is CHK-40 — report it there, once, and leave the flow off the stale list; with 0 views it is still stale under (a). When most of the flows in a review went quiet at the same time, say it once under "Across these flows": the install or analytics may be the cause, not each flow.
- doc: flow-not-starting

### H. More configuration patterns

### CHK-51 Step triggers that can be true at the same time
- severity: medium   certainty: risk
- applies_to: flow
- detect: one step (usually a hidden routing step) has two or more triggers with `element` present or not-present conditions on elements that could exist together; or a button with `go_to_step` plus an element-click trigger on the same step that leads to the same place. Also: one trigger whose condition ORs several element "not present" (or "page does not match") conditions — on almost any page at least one is true, so it fires at once.
- why: if two triggers are true together, the one that fires first wins, so the flow can loop between steps, jump ahead, or move twice.
- tell_the_user: "Step N has several triggers that could all be true at once, so it may loop or skip. Can both elements be on the page at the same time?"
- fix: Keep routing triggers on one hidden step and make them mutually exclusive (add an element only one state has, or an element-not-present); remove the duplicate transition.
- false_positive_guard: triggers on clearly different pages. Whether the elements can coexist isn't visible, so phrase it as a question.

### CHK-52 Contradictory AND: one single-valued field must equal two values
- severity: high   certainty: definite (blocker when it is on the start rule's only AND path, or on the only exit of a hidden step)
- applies_to: flow
- detect: inside one `and` clause (start, hide or trigger), two or more `attribute` nodes on the same `attribute_name` (or two conditions on the same event field) that each test "is" a different value.
- why: a user has one value for a text or select attribute, so "role is A AND role is B" can never be true. The flow never starts, or the hidden step never moves on.
- tell_the_user: "The rule requires `<attribute>` to be both `<A>` and `<B>`, which can't happen."
- fix: Put the values in a Logic group joined with OR, and keep the required conditions outside that group.
- false_positive_guard: list attributes, which can hold several values; two conditions that are a range (at least / at most).
- doc: flow-targeting

### CHK-53 AND / OR grouping that looks wrong
- severity: medium   certainty: risk
- applies_to: flow
- detect: in `start_condition`: (a) many flat conditions all joined with AND where the names suggest alternatives (several roles, several pages); (b) exclusions ("not in segment A", "not in segment B", "does not contain …") joined with OR, which lets through anyone who fails only one; (c) an audience group joined with OR that matches anyone satisfying a single clause.
- why: AND needs every condition to be true, OR needs only one. Mixing them up changes who sees the flow.
- tell_the_user: "These conditions are joined with <AND/OR>. Is that what you intend? For <alternatives> you need OR; for exclusions you need AND."
- fix: Wrap alternatives in a Logic group set to OR; use AND for exclusions.
- false_positive_guard: you can't know the intent, so phrase it as a question.
- doc: flow-targeting

### CHK-54 Edits don't reach users who are already in the flow
- severity: low   certainty: definite
- applies_to: flow
- detect: informational. Say it when `draft_dirty` is true or the versions differ (CHK-02), or when the user says "it still shows the old thing" or "I just changed it".
- why: changes to closing, hide rules, start rules or dates apply to new starts after publishing. A user with a session in progress keeps the version they started on until that session ends.
- tell_the_user: "Publishing doesn't change a session that is already running. To test, use a fresh user or end the session first."
- fix: End the session (the X in the preview popup, or delete it under the user's Sessions tab), then publish and test again.
- false_positive_guard: never present as a defect.
- doc: dismiss-snooze-restart

### CHK-55 Selector written in the wrong syntax
- severity: high   certainty: definite
- applies_to: flow
- detect: a manual selector `css` (steps, beacons, element conditions) that is a bare word which is not a tag name (`submit-button` instead of `.submit-button` or `#submit`), or is not valid CSS.
- why: without the leading `.` or `#` the selector looks for an element with that tag name, which doesn't exist, so the target or element rule is never true.
- tell_the_user: "The selector `<css>` on step N has no `.` or `#` in front, so it finds nothing."
- fix: Prefix classes with `.` and ids with `#`, and test it with the builder's element test.
- false_positive_guard: plain tag selectors (`button`, `h1`) are valid.
- doc: element-not-found

### CHK-56 Input, checkbox or toggle conditions that aim at the wrong control
- severity: medium   certainty: risk
- applies_to: flow
- detect: element, `input_value` or `filled_in_input` conditions in start rules or triggers where: (a) look-alike controls (toggles, checkboxes) are picked by position or text; (b) a checkbox or toggle state is needed but the selector has no `:checked` / `:not(:checked)`; (c) a "user fills in input" rule is used where the first keystroke would count.
- why: look-alike controls match the wrong one; state needs a state selector; filled-in fires on the first character.
- tell_the_user: "This reacts to <control> by position or text, so it can match a different control, or fire too early."
- fix: Use a stable id or data attribute per control; `:checked` / `:not(:checked)` for state; a text-value condition or a short wait for inputs.
- false_positive_guard: a unique id or data attribute per control.
- doc: element-not-found

### CHK-57 Selector too broad to point at one element
- severity: medium   certainty: risk
- applies_to: flow
- detect: a selector that is a single generic class, a whole container or full-width block, or a launcher or click selector that probably also matches other buttons, modals or pages.
- why: a tooltip anchors to a large block, or the flow starts on clicks you didn't intend or on the wrong page.
- tell_the_user: "The selector on step N may match more than one element (or a whole block). Does it match exactly one on the live page?"
- fix: Narrow it to the exact element, or use a manual selector that is unique to it; check with the debugger.
- false_positive_guard: a specific id or data attribute. You can't see the live page, so phrase it as a question.
- doc: element-not-found

### CHK-58 Step waits for a click that navigates or opens an overlay
- severity: medium   certainty: risk
- applies_to: flow
- detect: a trigger with an element `click` condition where the next step is on another page or inside an overlay, and no element-present or page trigger handles the destination.
- why: a click that reloads the page, or that the app handles itself, may never reach the trigger, so users look stuck and it seems like a selector failure.
- tell_the_user: "Step N waits for a click on an element that navigates away. If the click doesn't register, users never move on."
- fix: Use an "Element is present" trigger for the destination instead, and tell users what to click.
- false_positive_guard: the next step is on the same page.
- doc: element-not-found

### CHK-59 Navigate action with a wildcard or dynamic part
- severity: high   certainty: definite
- applies_to: flow
- detect: an action `type == "navigate"` whose `url` contains `*` or a pattern such as `:id`.
- why: wildcards and `:param` patterns only work in page conditions; a navigate action needs an exact address.
- tell_the_user: "The button on step N navigates to `<url>`, but wildcards aren't supported in a navigate action."
- fix: Use a relative path with an attribute placeholder for the changing part, and send that value as an attribute from `identify()` or `group()`.
- false_positive_guard: an attribute placeholder for the changing part is fine.

### CHK-60 Navigate action with an absolute address on a multi-domain app
- severity: medium   certainty: risk
- applies_to: flow
- detect: an action `type == "navigate"` whose `url` starts with a scheme or host, while page rules or other flows suggest more than one domain, region or environment.
- why: an absolute address always goes to that one domain, so users on another domain or region land on the wrong site.
- tell_the_user: "The button on step N always goes to `<host>`. Does your app run on more than one domain or region?"
- fix: Use a relative path so it stays on the user's current domain.
- false_positive_guard: a single-domain app, or a deliberate link to another site.

### CHK-61 One environment shared by several sites, with no domain rule
- severity: medium   certainty: risk
- applies_to: flow
- detect: the start rule has no page rule that names a domain, and the environment's other flows or the user's description point to more than one site or product on the same Userflow token.
- why: content belongs to the environment, not to a website, so it shows on every site that loads that token.
- tell_the_user: "This isn't limited to one site. If several products share this environment, it will show on all of them."
- fix: Add the domain to the start rule and a "does not match" hide rule for the others, or use separate environments.
- false_positive_guard: a single site. Keep this out of the headline unless you have other evidence.
- doc: flow-targeting

### CHK-62 Time-based rule that doesn't behave as expected
- severity: medium   certainty: risk
- applies_to: flow
- detect: a `time` node, or an attribute node on signup, last-seen or first-seen dates.
- why: the current-time rule follows the time zone of whoever created the flow, not each user's; "time since signup" on a company date lets newcomers in old companies through; elapsed time is only re-checked when the user does something.
- tell_the_user: "This time rule uses <the creator's time zone / a company date>. Is that what you intend?"
- fix: Use user-level attributes and have the app compute numbers like "days since signup"; state the time zone you mean.
- false_positive_guard: a global launch time that is meant to be the same for everyone.
- doc: flow-targeting

### CHK-63 Tooltip without a backdrop where users can click away
- severity: low   certainty: risk
- applies_to: flow
- detect: a tooltip step with `backdrop_mode` absent (an absent value means no backdrop), whose target is inside a popup, menu or modal, or whose step expects a click on the target.
- why: without a backdrop users click elsewhere, which can close the popup that holds the target. The backdrop is set per step, so a flow can be inconsistent.
- tell_the_user: "Step N has no backdrop, so users can click away from the element it points at."
- fix: Turn on "Add backdrop" on those steps, and make clicking the target go to the next step.
- false_positive_guard: tips that aren't critical.

### CHK-64 Rule that relies on a user ID or company ID
- severity: medium   certainty: risk
- applies_to: flow
- detect: an attribute condition or `{{placeholder}}` that uses an attribute named like `id`, `user_id` or `company_id`, or a text placeholder meant to show an ID.
- why: the ID passed to `identify()` or `group()` identifies the user or company; it isn't automatically usable as an attribute in rules, text or links.
- tell_the_user: "This uses `<name>`. Does your app also send it as an attribute? The ID you pass to identify() isn't one."
- fix: Send the value as a custom attribute in `identify()` or `group()`, then use that attribute.
- false_positive_guard: a custom attribute with a clear name that exists in the workspace (CHK-09 confirms).
- doc: install-check

### CHK-65 Element rule used to tell mobile from desktop
- severity: medium   certainty: likely
- applies_to: flow
- detect: `element` present / not-present nodes in a start or hide rule on an element that only differs between layouts, or that is described as a mobile or desktop element.
- why: element rules also match elements that are hidden by CSS, so they don't reliably tell layouts apart.
- tell_the_user: "This rule tells mobile from desktop by an element. That element can still exist, hidden, on the other layout."
- fix: Use an attribute your app sends for the device or screen size in the start and hide rules.
- false_positive_guard: an element that is truly absent from the other layout.
- doc: flow-targeting
