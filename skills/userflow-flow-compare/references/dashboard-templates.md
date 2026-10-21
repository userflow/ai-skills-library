# Widget templates

Condensed, working templates from validated dry runs. Adapt data and labels; keep structure, colors, and behavior. All widgets: sr-only summary first, CSS variables for theming, no gradients/shadows, sentence case, round all displayed numbers.

## 1. Picker widget (Phase 1)

Load `visualize:read_me` module `interactive` first. Embed the flow list as compact JSON (`{i: id, n: name, t: type}`).

```html
<h2 class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);">Flow comparison setup: pick a flow type, search and select two flows, choose a date range, then compare.</h2>
<div style="max-width:640px;">
  <label style="font-size:13px;color:var(--text-secondary);display:block;margin-bottom:6px;">Flow type</label>
  <select id="typeSel" style="width:100%;margin-bottom:1.25rem;"></select>
  <!-- two identical search blocks, ids s1/l1/p1/p1n/x1 and s2/l2/p2/p2n/x2 -->
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-bottom:1.25rem;">
    <div>
      <label style="font-size:13px;color:var(--text-secondary);display:block;margin-bottom:6px;">Flow 1</label>
      <input id="s1" type="text" placeholder="Search flows" style="width:100%;" autocomplete="off">
      <div id="l1" style="border:0.5px solid var(--border);border-radius:var(--radius);margin-top:4px;max-height:180px;overflow-y:auto;display:none;background:var(--surface-2);"></div>
      <div id="p1" style="display:none;margin-top:6px;font-size:13px;padding:6px 10px;background:var(--bg-accent);color:var(--text-accent);border-radius:var(--radius);justify-content:space-between;"><span id="p1n"></span><i class="ti ti-x" id="x1" style="cursor:pointer;margin-left:8px;" aria-label="Clear flow 1"></i></div>
    </div>
    <!-- Flow 2 block: same, ids suffixed 2 -->
  </div>
  <label style="font-size:13px;color:var(--text-secondary);display:block;margin-bottom:6px;">Date range</label>
  <div id="ranges" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1.5rem;"></div>
  <button id="go" style="width:100%;" disabled>Compare flows ↗</button>
  <p id="hint" style="font-size:13px;color:var(--text-muted);margin-top:8px;">Select a type, two flows, and a range</p>
</div>
```

Script logic (implement exactly this behavior):
- `TYPE_LABELS = {flow:"Flow (guides & tours)", checklist:"Checklist", announcement:"Announcement", launcher:"Launcher", banner:"Banner", resource_center:"Resource center"}`; option text includes per-type count, e.g. `"Flow (guides & tours) — 78 published"`.
- `RANGES = ["Last day","Last 1 week","Last 15 days","Last 1 month","Last quarter","Last 6 months","Last year"]`; render as buttons; selected chip gets `background: var(--bg-accent); color: var(--text-accent); border-color: var(--border-accent)`. Default selection: "Last 1 month".
- Search render: filter flows by `f.t === sel.type && name includes query && f.i !== otherSelection.i`, cap at 30 rows, rows are divs with hover `var(--surface-1)`. On click: store selection, show pill, hide input+list. Clear icon reverses it. `blur` hides the list after a 180ms timeout so clicks land.
- Type change clears both selections.
- Compare button enabled only when both flows chosen; `onclick`:
  `sendPrompt("Compare these two "+sel.type+" flows over "+sel.range.toLowerCase()+": Flow 1 = \""+f1.n+"\" (id "+f1.i+"), Flow 2 = \""+f2.n+"\" (id "+f2.i+"). Build the comparison dashboard.")`

## 2. Guide flow / checklist dashboard (Phase 2)

Load `visualize:read_me` module `chart` first. Structure top to bottom:

1. sr-only summary sentence with the headline numbers.
2. Custom legend: `#2a78d6` square + flow 1 name, `#eb6834` square + flow 2 name.
3. Metric card grid `repeat(auto-fit,minmax(150px,1fr))`, each card `background:var(--surface-1); border-radius:var(--radius); padding:1rem`, 13px muted label, 24px/500 value with a `vs <other>` span in 13px secondary. Cards: Views, Unique viewers, Completion rate, Missing element errors.
4. Step funnel per flow with views (skip a flow with all-zero steps; the dormancy story goes in prose). Rows: `grid-template-columns:170px minmax(0,1fr) 90px`. Bar width = round(step views / first-step views × 100)%, min 4% when nonzero. Bar color `#2a78d6`; the single worst-drop step's bar is `#e34948`. Right column: count plus `(−N%)` step-over-step drop when >0, colored `var(--text-danger)` when drop ≥50%.
5. Chart.js line chart of views time series, height ~220px wrapper, both flows (flow 2 dashed `[5,4]`), `fill:true` with `rgba(42,120,214,0.1)` on flow 1 only, `legend:{display:false}`, y `beginAtZero, precision:0`, x `maxTicksLimit:8`. Canvas gets `role="img"`, descriptive `aria-label`, fallback text.
6. Follow-up buttons calling `sendPrompt`, each label ending in ` ↗`: view individual sessions for the stronger flow; re-run with a different range; check publication history when a flatline-to-zero was detected.

## 3. Announcement dashboard (Phase 2)

Same skeleton as template 2 with these swaps:
- Metric cards: Views, Reactions, Comments, Engagement per 100 views (`(reactions+comments)/views*100`, `.toFixed(1)`, guard divide-by-zero → show 0).
- No funnel section, no missing-element card.
- Trend chart identical; when the window is long and early periods are all zero for both flows, trim leading zero buckets and say so in the section label (e.g. "Weekly views — shown from mid-May (all earlier weeks were zero)").

## Chart conventions (all dashboards)

- Series colors fixed: flow 1 `#2a78d6`, flow 2 `#eb6834`; flow 2 always dashed so color is never the only differentiator.
- Chart.js 4.4.1 from `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js`; canvas wrapper div holds the height, `responsive:true, maintainAspectRatio:false`.
- Everything numeric through `Math.round` / `.toFixed(1)` / `toLocaleString()` before display.
