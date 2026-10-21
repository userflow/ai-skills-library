# Widget templates

Condensed working templates from the validated dry run. Keep structure, colors, and behavior; swap data. All widgets: sr-only summary heading first, CSS variables for theming, no gradients/shadows, sentence case, buttons that message Claude end in " ↗".

## 1. Time-frame picker (Phase 2)

Load `visualize:read_me` module `interactive` first.

```html
<h2 class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);">Choose the time frame for summarising the NPS flow's feedback.</h2>
<div style="max-width:560px;">
<p style="font-size:13px;margin:0 0 1rem;"><span style="color:var(--text-muted);">Flow verified:</span> <span style="padding:3px 10px;background:var(--bg-accent);color:var(--text-accent);border-radius:var(--radius);font-size:13px;">FLOW_NAME ✓ nps question found</span></p>
<label style="font-size:13px;color:var(--text-secondary);display:block;margin-bottom:6px;">Time frame</label>
<div id="ranges" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1.5rem;"></div>
<button id="go" style="width:100%;">Summarise NPS feedback ↗</button>
</div>
<script>
const RANGES=["Last 1 week","Last 15 days","Last 1 month","Last quarter","Last 6 months","Last year"];
let range="Last quarter";
const rd=document.getElementById("ranges");
RANGES.forEach(r=>{const b=document.createElement("button");b.textContent=r;b.style.cssText="font-size:13px;padding:6px 12px;";b.onclick=()=>{range=r;paint();};rd.appendChild(b);});
function paint(){[...rd.children].forEach(b=>{const on=b.textContent===range;b.style.background=on?"var(--bg-accent)":"transparent";b.style.color=on?"var(--text-accent)":"var(--text-primary)";b.style.borderColor=on?"var(--border-accent)":"var(--border-strong)";});}
paint();
document.getElementById("go").onclick=()=>{sendPrompt("Summarise NPS feedback for \"FLOW_NAME\" (id FLOW_UUID) over "+range.toLowerCase()+". Group positive and negative comments with expandable user lists.");};
</script>
```

## 2. Comment summary (Phase 3)

No chart module needed. Structure top to bottom:

```html
<h2 class="sr-only" style="...sr-only styles...">One-sentence summary with counts and main themes.</h2>
<p style="font-size:13px;color:var(--text-muted);margin:0 0 1rem;">FLOW_NAME · RANGE · N comments from M responses</p>

<details open style="background:var(--surface-1);border-radius:var(--radius);padding:0.75rem 1rem;margin-bottom:10px;">
  <summary style="cursor:pointer;font-weight:500;color:#348452;">Positive — N comments <span style="font-weight:400;color:var(--text-muted);">(tap for users)</span></summary>
  <p style="font-size:13px;color:var(--text-secondary);margin:10px 0;">Thematic summary; if the flow has no promoter feedback question, say the positive column is near-empty by design.</p>
  <div id="posList"></div>
</details>

<details open style="...same, heading color:#e34948;...">
  <summary ...>Negative — N comments <span ...>(tap for users)</span></summary>
  <p ...><b>Theme label (count):</b> theme summary.<br><br><b>Next theme (count):</b> ...</p>
  <div id="negList"></div>
</details>

<div style="display:flex;gap:8px;flex-wrap:wrap;">
  <button onclick="sendPrompt('Draft a promoter feedback question to add to the NPS flow')">Draft promoter question ↗</button>
  <button onclick="sendPrompt('Summarise the same NPS flow comments over the last year instead')">Try last year ↗</button>
</div>

<script>
// rows: [shortUserId, score, "Mon D", "comment (light paraphrase, specifics preserved)"]
const POS=[["067433d1",7,"Jul 6","I love the product — but pricing gets expensive..."]];
const NEG=[["ae20c46a",8,"Jul 9","Pricey; the 100/month AI chat limit is consumed by testing..."]];
function color(s){return s>=9?"#348452":(s>=7?"#d97917":"#e34948");}
function fill(id,rows){
  const el=document.getElementById(id);
  rows.forEach(r=>{
    const c=color(r[1]);
    const d=document.createElement("div");
    d.style.cssText="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-top:0.5px solid var(--border);font-size:13px;";
    d.innerHTML='<span style="min-width:34px;text-align:center;font-weight:500;padding:2px 6px;border-radius:4px;background:'+c+'1a;color:'+c+';">'+r[1]+'</span><span style="min-width:78px;color:var(--text-muted);font-family:monospace;">'+r[0]+'…</span><span style="min-width:52px;color:var(--text-muted);">'+r[2]+'</span><span style="color:var(--text-secondary);">'+r[3]+'</span>';
    el.appendChild(d);
  });
}
fill("posList",POS);fill("negList",NEG);
</script>
```

Conventions:
- Score badge colors by score value: ≥9 `#348452`, 7–8 `#d97917`, ≤6 `#e34948` — even though sections are sentiment-based, so score/sentiment divergence is visible.
- User IDs: first 8 chars + `…`, monospace, muted.
- Both sections render even when empty (empty Positive + promoter-blind-spot note is itself the finding).
- No NPS score card, segment split bar, or trend chart anywhere — comment summary only.
