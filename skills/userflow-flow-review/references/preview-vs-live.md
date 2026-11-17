# Preview vs live — why a flow behaves differently

1. Preview force-starts the DRAFT. It skips: published-in-env check, start rule, start frequency, platform check. So "works in preview" says nothing about targeting or publishing. (CHK-01, CHK-25)
2. Preview does NOT skip "constrain to current company" or locale gating — it fails with the same error. (CHK-07)
3. In preview a missing tooltip element never ends the flow — you get a preview-only notice. Live, with theme behavior "dismiss", the flow silently ends. (CHK-27..30)
4. Snooze does not snooze in preview; it shows an alert.
5. "Start another flow" in preview starts the other flow's draft; live it must be published. (CHK-39)
6. A preview session stays open until closed with the X and can keep showing builder-only messages.
7. Preview sessions don't count toward "once per user" — live sessions, including your own tests, do. (CHK-20)
8. Live users get the PUBLISHED version; preview and this review use the draft. (CHK-02)
9. The Chrome extension injects Userflow.js for preview; live needs the real install with the right token and an identified user. If preview or the element picker won't work at all, see `chrome-extension` in `help-docs.md`.
10. Live, only one flow shows at a time; preview pushes its flow in regardless of what else would be running. (CHK-43)
