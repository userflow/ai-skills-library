# Artifact templates

Two pieces: the **agent picker** (step 1, an inline Visualizer widget) and the **report** (step 6, a self-contained HTML file). Both are tested templates. Keep the structure and behaviour; swap the data.

Contents
1. Agent picker widget
2. Report: how the template works
3. Report: the `DATA` contract
4. Report: filling rules
5. Report: full HTML template
6. Pre-flight checklist

---

## 1. Agent picker widget

Load the Visualizer `interactive` module first. Follow the Visualizer's own conventions here (CSS variables, sentence case, weights 400/500, no brand fonts) because the picker lives in the chat, not in the report.

Fill `FLOWS` from `list_flows` (assistant flows only): published first, then by `edited_at` descending. Fill `ENV_*` from `describe_session`.

```html
<h2 class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);">Pick an Adoption Agent and a time window for the topic report.</h2>
<p style="font-size:13px;color:var(--text-secondary);margin:0 0 8px;">Environment: <span style="color:var(--text-primary);">ENV_NAME</span></p>
<div id="flows" style="display:flex;flex-direction:column;gap:6px;margin-bottom:1.25rem;"></div>
<label style="font-size:13px;color:var(--text-secondary);display:block;margin-bottom:6px;">Time window</label>
<div id="wins" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;"></div>
<div id="custom" style="display:none;gap:8px;align-items:center;margin-bottom:8px;font-size:13px;color:var(--text-secondary);">
  <input type="date" id="from" style="width:auto;"> to <input type="date" id="to" style="width:auto;">
</div>
<p id="err" style="font-size:13px;color:var(--text-danger);margin:0 0 8px;min-height:1em;"></p>
<button id="go" style="width:100%;">Build topic report ↗</button>
<script>
const FLOWS=[
  {id:"7b561881-418c-481f-98cf-5f8266b89cbc",name:"Userflow Adoption Agent",state:"published",pubs:198,edited:"2026-10-07"},
  {id:"c83c9cc4-d639-4cd0-9834-2efb23a57a9f",name:"Userflow AI Assistant Harsh Copy",state:"draft",pubs:8,edited:"2026-06-26"},
  {id:"809f0ee6-aab4-480e-b2ae-38f9d77a641f",name:"Userflow AI Assistant",state:"draft",pubs:0,edited:"2026-03-23"}
];
const ENV_ID="ENV_UUID";
const WINS=["Last 7 days","Last 30 days","Last 90 days","Custom"];
let sel=FLOWS.find(f=>f.state==="published")?.id||FLOWS[0].id, win="Last 30 days";
const fl=document.getElementById("flows"), wn=document.getElementById("wins");
function stateLabel(f){return f.state==="published"?"published":(f.pubs>0?"unpublished (was live)":"never published");}
function paintFlows(){fl.innerHTML="";FLOWS.forEach(f=>{const b=document.createElement("button");const on=f.id===sel;const dim=f.pubs===0;
  b.style.cssText="text-align:left;display:flex;justify-content:space-between;gap:12px;padding:8px 12px;font-size:13px;opacity:1;"+(on?"background:var(--bg-accent);color:var(--text-accent);border-color:var(--border-accent);":"")+(dim&&!on?"color:var(--text-muted);":"");
  b.innerHTML='<span><span style="font-weight:500;">'+f.name+'</span> <span style="font-family:var(--font-mono);font-size:12px;">'+f.id.slice(0,8)+'</span></span><span style="font-size:12px;white-space:nowrap;">'+stateLabel(f)+' · '+f.pubs+' pubs · edited '+f.edited+'</span>';
  b.onclick=()=>{sel=f.id;paintFlows();};fl.appendChild(b);});}
function paintWins(){wn.innerHTML="";WINS.forEach(w=>{const b=document.createElement("button");const on=w===win;b.textContent=w;b.style.cssText="font-size:13px;padding:6px 12px;"+(on?"background:var(--bg-accent);color:var(--text-accent);border-color:var(--border-accent);":"");b.onclick=()=>{win=w;document.getElementById("custom").style.display=w==="Custom"?"flex":"none";paintWins();};wn.appendChild(b);});}
paintFlows();paintWins();
document.getElementById("from").oninput=document.getElementById("to").oninput=()=>{document.getElementById("err").textContent="";};
document.getElementById("go").onclick=()=>{const f=FLOWS.find(x=>x.id===sel);let w=win.toLowerCase();
  if(win==="Custom"){const a=document.getElementById("from").value,b=document.getElementById("to").value;
    if(!a||!b||a>b){document.getElementById("err").textContent="Pick a start date on or before the end date";return;} w=a+" to "+b;}
  sendPrompt('Build the Adoption Agent topic report for "'+f.name+'" (flow id '+f.id+', env '+ENV_ID+') over '+w+'.');};
</script>
```

Why it's built this way:
- The flow ID prefix is shown on every row because names collide; the user should be able to tell three "Userflow AI Assistant" rows apart at a glance.
- "unpublished (was live)" vs "never published" comes from `total_publications`, not `state` (see `api-notes.md` §2). Never-published rows are muted but still clickable.
- The `sendPrompt` text carries the full UUID and env ID, so the next turn needs no lookup.

---

## 2. Report: how the template works

The report is one HTML file with a single `DATA` object near the bottom. You fill `DATA`; the script renders everything else. Rankings, "also #N in …" badges, empty states and chronological message order are all computed in the page, so the three sections can never disagree with each other or with the cards.

What the page renders, top to bottom:
1. **Hero** (Userflow Dark frame → Light Blue card): agent name, window, environment, short flow ID, four KPI tiles (conversations + messages, % conversations with an unanswered message, disliked conversations + liked, topic count + test conversations set aside).
2. **Jump links** to the three sections, with topic counts.
3. **Couldn't answer**: topics with unanswered messages, by unanswered-message count. Customer topics first, Test-badged topics after them.
4. **Negative feedback**: topics with disliked messages, by disliked-message count, with the users' `feedback` text quoted at the top of each card.
5. **Asked most often**: customer topics by conversation count, then an "Internal / test traffic" subgroup, then "Other one-off questions".
6. **Footer**: coverage line, your method notes, generated date.

Each topic card expands to its conversations (15 shown, rest behind a "Show N more" button), sorted so the most relevant ones for that section come first. Each conversation expands to the full transcript in time order, with per-message status (answered / couldn't find an answer / agent action), rating, and feedback. Long agent replies are clamped; click to expand.

Styling follows Userflow brand visuals: Figtree, the four primary colours, secondary colours only as small badges (Lavender = Test, Orange = escalation and dislikes, Grey = language and unanswered). Don't restyle it per run.

---

## 3. Report: the `DATA` contract

```js
const DATA = {
  meta: {
    agent_name: "Userflow Adoption Agent",
    flow_id: "7b561881-418c-481f-98cf-5f8266b89cbc",
    env_name: "Production",
    window_label: "Last 30 days (15 Sep – 15 Oct 2026)",
    generated_at: "15 Oct 2026",
    coverage: { read: 316, total: 316 }        // conversations clustered vs total_count
  },
  kpis: {                                       // from get_adoption_agent_analytics, not your pulls
    conversations: 316, messages: 672,
    unanswered_convs: 104, disliked_convs: 7, liked_convs: 2,
    test_convs: 18                              // sum of conversations in Test-badged topics
  },
  topics: [
    {
      id: "launcher-scroll",                    // any unique slug
      name: "Launcher misbehaving on the page",
      description: "Launchers lag while scrolling or attach to only one of several matching elements, and the agent repeats generic CSS advice.",
      is_test: false,                           // true → Test badge, sorted after customer topics
      is_other: false,                          // exactly one topic may be true: "Other one-off questions"
      languages: ["English", "Portuguese"],     // optional; omit when English-only
      counts: {
        conversations: 2,                       // distinct conversations in this topic
        unanswered: 1,                          // messages with is_unanswered === true, in window
        disliked: 2,                            // messages with rating === "dislike", in window
        chains: 2                               // conversations flagged chain: true
      },
      conversation_ids: ["c79034d7-…", "6ab3e50c-…"],
      feedback: [                               // non-empty feedback text from disliked messages
        { text: "you are not solving the issue", user_id: "348e6675-…", t: "2026-10-13T08:11:49Z" }
      ]
    }
  ],
  conversations: {
    "c79034d7-…": {
      user_id: "348e6675-…",
      started: "2026-10-13T08:10:22Z",          // conversation inserted_at
      chain: true,                              // escalation chain (see SKILL.md step 4)
      messages: [                               // any order; the page sorts by t
        { t: "2026-10-13T08:11:22Z", user: "…", assistant: "…",
          unanswered: true,                     // is_unanswered, keep null as null
          rating: "dislike",                    // "dislike" | "like" | null
          feedback: null,                       // "" from the API → null
          out_of_window: false }                // optional; true if before start_date
      ]
    }
  },
  notes: [                                      // footer bullets, plain sentences
    "KPI row uses analytics totals; section counts come from the conversations read.",
    "The built-in topic model filed ~70% of messages under one generic topic, so it wasn't used."
  ]
};
```

---

## 4. Report: filling rules

- **Every id in `conversation_ids` must exist in `conversations`.** A missing one renders nothing and silently shrinks the topic. Assert this before writing the file.
- **A conversation can belong to more than one topic only if it genuinely covers two subjects.** Default to one topic: where its opening question points.
- **Counts must match the conversations you attach.** Compute `counts` from the same messages you put in `conversations`, not from memory of the raw pulls. The in-window filter (`out_of_window`) applies to `unanswered` and `disliked`.
- **Include the full transcript** for every conversation you attach (every message, both sides, verbatim). Truncate nothing; the page handles long replies.
- **Normalise `feedback`.** The API returns `""` and `null` for "no comment". Pass both as `null`, and only list non-empty text in `topic.feedback`.
- **Don't put a disliked conversation in the "Other" topic.** Give it a real topic, even a topic of one.
- **Never invent fields.** If something isn't in the data (user names, plans, companies), leave it out; the page doesn't need it.
- **Escape nothing yourself.** The page escapes all text when it renders. Write `DATA` as plain JSON with `ensure_ascii=False` so non-English text stays readable.
- **Build `DATA` with a script, not by hand,** once there are more than a handful of conversations. Save the pulled conversations to JSON files as you page through them, write your topic assignments as a `{conversation_id: topic_id}` map, and let a short Python script assemble `DATA`, compute counts, run the id check, and substitute it into the template. Hand-typing hundreds of transcripts is where errors creep in.
- **Size.** A full month (~300 conversations, ~700 messages) produces a file of roughly 0.5–1 MB. That's fine. If it goes far beyond a few MB, attach the most relevant 30 conversations per topic and say so in `notes`.

Substitute two placeholders: `__DATA_JSON__` (the JSON) and `__AGENT_NAME__` (page title).

---

## 5. Report: full HTML template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Adoption Agent topics — __AGENT_NAME__</title>
<link href="https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,400;0,500;0,600;0,700;0,800;1,700&display=swap" rel="stylesheet">
<style>
:root{
  --uf-light-blue:#BEDDFD;--uf-deep-blue:#74B0FF;--uf-white:#FFFFFF;--uf-dark:#121941;
  --uf-orange:#FFD0AF;--uf-deep-orange:#FE784E;--uf-green:#D5FEC0;--uf-deep-green:#1A5554;
  --uf-lavender:#C3BEFF;--uf-deep-purple:#4E2656;--uf-grey:#E9EEF2;--uf-cream:#FFFDF8;
  --muted:#4A547A;--subtle:#7A82A3;--border:#D8DEF0;--border-strong:#B8C3E0;
  --font:'Figtree',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  --mono:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace;
}
*{box-sizing:border-box}
body{margin:0;font-family:var(--font);font-size:15px;line-height:1.35;letter-spacing:-0.01em;color:var(--uf-dark);background:var(--uf-white);-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:24px 20px 64px}
.hero{background:var(--uf-dark);border-radius:32px;padding:20px}
.hero-card{background:var(--uf-light-blue);border-radius:24px;padding:28px 28px 24px}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
h1{font-size:clamp(28px,4.5vw,44px);font-weight:800;line-height:0.95;letter-spacing:-0.02em;margin:0 0 12px}
h1 em,h2 em{font-style:italic;color:var(--uf-dark)}
h2 em{color:var(--uf-deep-blue)}
.sub{color:var(--muted);margin:0;font-size:15px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:20px}
.kpi{background:var(--uf-white);border-radius:18px;padding:14px 16px}
.kpi b{display:block;font-size:30px;font-weight:800;letter-spacing:-0.02em;line-height:1}
.kpi span{display:block;font-size:13px;color:var(--muted);margin-top:6px}
.kpi small{display:block;font-size:12px;color:var(--subtle);margin-top:2px}
nav.jump{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0 8px}
nav.jump a{font-size:13px;font-weight:600;color:var(--uf-dark);text-decoration:none;border:1px solid var(--border-strong);border-radius:999px;padding:6px 12px}
nav.jump a:hover{background:var(--uf-grey)}
section{margin-top:36px}
h2{font-size:28px;font-weight:800;line-height:0.95;letter-spacing:-0.02em;margin:0 0 8px}
.lede{color:var(--muted);margin:0 0 16px;max-width:760px}
.empty{color:var(--muted);background:var(--uf-grey);border-radius:12px;padding:14px 16px}
.subhead{font-size:12px;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:var(--subtle);margin:20px 0 8px}
details.topic{border:1px solid var(--border);border-radius:18px;margin-bottom:10px;background:var(--uf-white)}
details.topic[open]{border-color:var(--border-strong)}
details.topic>summary{list-style:none;cursor:pointer;padding:14px 16px;display:grid;grid-template-columns:36px 1fr auto;gap:12px;align-items:start}
details.topic>summary::-webkit-details-marker{display:none}
.rank{font-weight:800;font-size:18px;color:var(--subtle);text-align:right;padding-top:1px}
.tname{font-weight:700;font-size:16px}
.tdesc{color:var(--muted);font-size:14px;margin-top:3px}
.badges{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.badge{font-size:11.5px;font-weight:600;border-radius:999px;padding:3px 9px;white-space:nowrap}
.b-test{background:var(--uf-lavender);color:var(--uf-deep-purple)}
.b-repeat{background:var(--uf-light-blue);color:var(--uf-dark)}
.b-chain{background:var(--uf-orange);color:#7A3410}
.b-lang{background:var(--uf-grey);color:var(--muted)}
.metric{text-align:right;white-space:nowrap}
.metric b{display:block;font-size:22px;font-weight:800;letter-spacing:-0.02em;line-height:1}
.metric span{font-size:12px;color:var(--muted)}
.bar{height:6px;background:var(--uf-grey);border-radius:999px;margin-top:6px;width:110px;margin-left:auto;overflow:hidden}
.bar i{display:block;height:100%;background:var(--uf-deep-blue);border-radius:999px}
.tbody{padding:0 16px 16px 64px}
.quotes{margin:4px 0 12px}
.quote{border-left:3px solid var(--uf-deep-orange);background:var(--uf-cream);border-radius:0 12px 12px 0;padding:8px 12px;margin-bottom:6px;font-size:14px}
.quote small{display:block;color:var(--subtle);font-size:12px;margin-top:2px}
details.convo{border-top:1px solid var(--border)}
details.convo>summary{cursor:pointer;padding:10px 0;font-size:13.5px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
details.convo>summary .uid{font-family:var(--mono);font-size:12px;color:var(--subtle)}
details.convo>summary .when{color:var(--subtle);font-size:12px}
details.convo>summary .first{flex:1 1 280px;color:var(--uf-dark)}
.flag{font-size:11px;font-weight:700;border-radius:6px;padding:1px 6px}
.f-un{background:var(--uf-grey);color:var(--muted)}
.f-dis{background:var(--uf-orange);color:#7A3410}
.f-like{background:var(--uf-green);color:var(--uf-deep-green)}
.turns{padding:2px 0 12px}
.turn{margin:8px 0}
.u,.a{border-radius:12px;padding:8px 12px;font-size:14px;white-space:pre-wrap;word-break:break-word}
.u{background:var(--uf-light-blue);margin-right:15%}
.a{background:var(--uf-grey);margin-left:15%;color:var(--muted)}
.a.clamp{max-height:7.2em;overflow:hidden;position:relative;cursor:pointer}
.a.clamp::after{content:"show more";position:absolute;right:8px;bottom:4px;font-size:11px;font-weight:700;color:var(--uf-dark);background:var(--uf-grey);padding-left:8px}
.meta{font-size:11.5px;color:var(--subtle);margin:3px 2px 0}
.meta.r{text-align:right}
.fb{font-size:13px;color:#7A3410;margin:4px 0 0 15%}
.more{font-size:13px;font-weight:600;background:none;border:1px solid var(--border-strong);border-radius:999px;padding:6px 12px;cursor:pointer;margin-top:8px;font-family:inherit;color:var(--uf-dark)}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--border);color:var(--muted);font-size:13px}
footer ul{margin:6px 0 0;padding-left:18px}
@media (max-width:640px){
  details.topic>summary{grid-template-columns:24px 1fr}
  .metric{grid-column:2;text-align:left}.bar{margin-left:0}
  .tbody{padding:0 12px 14px 12px}.u{margin-right:0}.a{margin-left:0}.fb{margin-left:0}
}
</style>
</head>
<body>
<div class="wrap" id="app"></div>
<script>
/* ===== Fill this object; nothing below it needs editing. ===== */
const DATA = __DATA_JSON__;
/* ============================================================= */

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt = n => Number(n).toLocaleString("en-US");
const pct = (a,b) => b ? Math.round(100*a/b) + "%" : "–";
const day = t => new Date(t).toLocaleDateString("en-GB",{day:"numeric",month:"short"});
const time = t => new Date(t).toLocaleString("en-GB",{day:"numeric",month:"short",hour:"2-digit",minute:"2-digit",timeZone:"UTC"}) + " UTC";
const short = id => String(id || "").slice(0,8) + "…";

const T = DATA.topics;
const C = DATA.conversations;

// Sort every conversation's messages chronologically: the API returns them unordered.
Object.values(C).forEach(c => c.messages.sort((a,b) => new Date(a.t) - new Date(b.t)));

// Rankings are derived from the counts, so the three sections can never disagree with the cards.
const byDesc = k => (a,b) => (b.counts[k] - a.counts[k]) || (b.counts.conversations - a.counts.conversations);
// Test-badged topics sink below customer topics wherever they appear, so internal QA never tops a customer-facing ranking.
const custFirst = cmp => (a,b) => (!!a.is_test - !!b.is_test) || cmp(a,b);
const rankUn  = T.filter(t => t.counts.unanswered > 0 && !t.is_other).sort(custFirst(byDesc("unanswered")));
const rankDis = T.filter(t => t.counts.disliked > 0).sort(custFirst(byDesc("disliked")));
const freqAll = T.filter(t => !t.is_other).sort(byDesc("conversations"));
const rankFreq = freqAll.filter(t => !t.is_test);
const rankTest = freqAll.filter(t => t.is_test);
const other = T.find(t => t.is_other);
const pos = (list,t) => list.indexOf(t) + 1;

function repeatBadges(t, here){
  const out = [];
  if (here !== "un"   && pos(rankUn,t))   out.push(`also #${pos(rankUn,t)} couldn't answer`);
  if (here !== "dis"  && pos(rankDis,t))  out.push(`also #${pos(rankDis,t)} negative feedback`);
  if (here !== "freq" && pos(rankFreq,t)) out.push(`also #${pos(rankFreq,t)} most asked`);
  return out.map(b => `<span class="badge b-repeat">${esc(b)}</span>`).join("");
}

function convoHTML(id){
  const c = C[id]; if (!c) return "";
  const first = c.messages[0]?.user || "";
  const un = c.messages.filter(m => m.unanswered === true).length;
  const dis = c.messages.filter(m => m.rating === "dislike").length;
  const like = c.messages.filter(m => m.rating === "like").length;
  const flags = [
    un ? `<span class="flag f-un">${un} unanswered</span>` : "",
    dis ? `<span class="flag f-dis">${dis} disliked</span>` : "",
    like ? `<span class="flag f-like">${like} liked</span>` : "",
    c.chain ? `<span class="flag f-dis">escalation</span>` : ""
  ].join(" ");
  const turns = c.messages.map(m => `
    <div class="turn">
      <div class="u">${esc(m.user)}</div>
      <div class="meta">${esc(time(m.t))}${m.out_of_window ? " · before window" : ""}</div>
      <div class="a${(m.assistant || "").length > 260 || (m.assistant || "").split("\n").length > 4 ? " clamp" : ""}" onclick="this.classList.remove('clamp')">${esc(m.assistant)}</div>
      <div class="meta r">${m.unanswered === true ? "agent: couldn't find an answer" : m.unanswered === null ? "agent action" : "answered"}${m.rating === "dislike" ? " · 👎 disliked" : m.rating === "like" ? " · 👍 liked" : ""}</div>
      ${m.feedback ? `<div class="fb">“${esc(m.feedback)}”</div>` : ""}
    </div>`).join("");
  return `<details class="convo">
    <summary><span class="uid">${esc(short(c.user_id))}</span><span class="when">${esc(day(c.messages[0]?.t || c.started))} · ${c.messages.length} msg</span><span class="first">${esc(first.length > 140 ? first.slice(0,140) + "…" : first)}</span>${flags}</summary>
    <div class="turns">${turns}</div>
  </details>`;
}

function topicHTML(t, rank, here, max){
  const metricKey = here === "un" ? "unanswered" : here === "dis" ? "disliked" : "conversations";
  const metricLabel = here === "un" ? "unanswered msgs" : here === "dis" ? "disliked msgs" : "conversations";
  const v = t.counts[metricKey];
  // In the negative-feedback section, put conversations with dislikes first; elsewhere, unanswered first.
  const score = id => { const c = C[id]; if (!c) return 0;
    const d = c.messages.filter(m => m.rating === "dislike").length, u = c.messages.filter(m => m.unanswered === true).length;
    return here === "dis" ? d*100 + u : here === "un" ? u*100 + d : c.messages.length; };
  const ids = [...t.conversation_ids].sort((a,b) => score(b) - score(a));
  const LIMIT = 15;
  const shown = ids.slice(0, LIMIT).map(id => convoHTML(id)).join("");
  const rest = ids.length > LIMIT ? `<div class="hidden" style="display:none">${ids.slice(LIMIT).map(id => convoHTML(id)).join("")}</div><button class="more" onclick="this.previousElementSibling.style.display='block';this.remove()">Show ${ids.length - LIMIT} more conversations</button>` : "";
  const quotes = (here === "dis" && t.feedback?.length) ? `<div class="quotes">${t.feedback.map(f => `<div class="quote">“${esc(f.text)}”<small>${esc(short(f.user_id))} · ${esc(day(f.t))}</small></div>`).join("")}</div>` : "";
  return `<details class="topic">
    <summary>
      <div class="rank">${rank}</div>
      <div>
        <div class="tname">${esc(t.name)}</div>
        <div class="tdesc">${esc(t.description)}</div>
        <div class="badges">
          ${t.is_test ? '<span class="badge b-test">Test</span>' : ""}
          ${t.counts.chains ? `<span class="badge b-chain">${t.counts.chains} escalation chain${t.counts.chains > 1 ? "s" : ""}</span>` : ""}
          ${t.languages?.length ? `<span class="badge b-lang">${esc(t.languages.join(", "))}</span>` : ""}
          ${repeatBadges(t, here)}
        </div>
      </div>
      <div class="metric"><b>${fmt(v)}</b><span>${metricLabel}</span><div class="bar"><i style="width:${max ? Math.max(4, 100*v/max) : 0}%"></i></div></div>
    </summary>
    <div class="tbody">${quotes}${shown}${rest}</div>
  </details>`;
}

function sectionHTML(id, title, lede, list, here, emptyMsg, extra = ""){
  const key = here === "un" ? "unanswered" : here === "dis" ? "disliked" : "conversations";
  const max = Math.max(0, ...list.map(t => t.counts[key]));
  return `<section id="${id}"><h2>${title}</h2><p class="lede">${lede}</p>
    ${list.length ? list.map((t,i) => topicHTML(t, i+1, here, max)).join("") : `<div class="empty">${emptyMsg}</div>`}${extra}</section>`;
}

const k = DATA.kpis, m = DATA.meta;
let html = `
<div class="hero"><div class="hero-card">
  <p class="eyebrow">Adoption Agent · topic report</p>
  <h1>What people <em>asked</em> ${esc(m.agent_name)}</h1>
  <p class="sub">${esc(m.window_label)} · ${esc(m.env_name)} · flow ${esc(short(m.flow_id))}</p>
  <div class="kpis">
    <div class="kpi"><b>${fmt(k.conversations)}</b><span>conversations</span><small>${fmt(k.messages)} messages</small></div>
    <div class="kpi"><b>${pct(k.unanswered_convs, k.conversations)}</b><span>had an unanswered message</span><small>${fmt(k.unanswered_convs)} conversations</small></div>
    <div class="kpi"><b>${fmt(k.disliked_convs)}</b><span>disliked conversations</span><small>${fmt(k.liked_convs)} liked</small></div>
    <div class="kpi"><b>${fmt(T.filter(t=>!t.is_other).length)}</b><span>topics</span><small>${rankTest.length ? fmt(k.test_convs) + " test conversations set aside" : "no test traffic detected"}</small></div>
  </div>
</div></div>
<nav class="jump"><a href="#unanswered">Couldn't answer (${rankUn.length})</a><a href="#negative">Negative feedback (${rankDis.length})</a><a href="#frequent">Asked most often (${rankFreq.length})</a></nav>`;

html += sectionHTML("unanswered", "Couldn't <em>answer</em>",
  "Ranked by messages where the agent said it couldn't find a match in its knowledge base. This is the agent's own report, not a correctness check: a confident wrong answer counts as answered.",
  rankUn, "un", "The agent reported an answer for every message in this window.");

html += sectionHTML("negative", "Negative <em>feedback</em>",
  "Topics containing thumbs-down messages. Where users wrote a comment, it's quoted at the top of the topic.",
  rankDis, "dis", "No thumbs-down in this window. Dislikes are rare and opt-in, so absence isn't proof of satisfaction.");

let freqExtra = "";
if (rankTest.length){
  const max = Math.max(...rankTest.map(t => t.counts.conversations));
  freqExtra += `<p class="subhead">Internal / test traffic</p>` + rankTest.map((t,i) => topicHTML(t, i+1, "freq", max)).join("");
}
if (other){
  freqExtra += `<p class="subhead">Other one-off questions</p>` + topicHTML(other, "·", "freq", other.counts.conversations);
}
html += sectionHTML("frequent", "Asked most <em>often</em>",
  "Ranked by conversations. Topics badged Test look like internal or QA traffic and are kept separate from customer demand.",
  rankFreq, "freq", "No customer topics in this window.", freqExtra);

html += `<footer>
  <b>How this was built.</b> Clustered from ${fmt(m.coverage.read)} of ${fmt(m.coverage.total)} conversations${m.coverage.read < m.coverage.total ? " (all disliked and unanswered conversations read in full; the rest sampled)" : ""}. Topics come from what users wrote, not the agent's replies or the built-in topic model.
  <ul>${(DATA.notes || []).map(n => `<li>${esc(n)}</li>`).join("")}</ul>
  <p>Generated ${esc(m.generated_at)}. User IDs are shortened internal IDs. Transcripts are verbatim.</p>
</footer>`;

document.getElementById("app").innerHTML = html;
</script>
</body>
</html>
```

---

## 6. Pre-flight checklist

Before calling `present_files`:

- [ ] Every `conversation_ids` entry resolves in `conversations`.
- [ ] Topic counts recomputed from attached messages, in-window only.
- [ ] Exactly zero or one `is_other` topic, and it holds no disliked conversation.
- [ ] Test-badged topics are excluded from nothing except the headline; their counts still show.
- [ ] `kpis` come from `get_adoption_agent_analytics`; `coverage.total` is `total_count` from the unfiltered pull.
- [ ] Opened the file once (headless browser or by reading back the rendered section counts) to confirm it renders without a script error. A JSON syntax error leaves a blank page.
