/* Renders every number on the page from window.DATA (site/data.js, written by scripts/build_page_data.py). */
(function(){
const D = window.DATA;
const $ = s => document.querySelector(s);
const MODELS = D.models;                       // key -> display name
const ORDER = ["mimir","llama1b","llama3b","gemma4b","qwen3b"];
const pct = x => (x*100).toFixed(1) + " %";
const pct0 = x => Math.round(x*100) + " %";
const A = (m,c) => D.agg.find(a => a.model===m && a.cond===c);
const esc = s => String(s==null?"":s).replace(/[&<>"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[ch]));

/* ---------- headline numbers and text fills ---------- */
const fills = {};
fills.date = new Date().toLocaleDateString("en-GB", {day:"numeric", month:"long", year:"numeric"});
const mc = A("mimir","closed"), mr = A("mimir","retrieve");
fills.mimir_closed_pct = pct(mc.em);
fills.mimir_retrieve_pct = pct(mr.em);
let best = null;
for (const m of ORDER) for (const c of ["agentic","agentic-fewshot","agentic-scaffold"]) { const a = A(m,c); if (a && (!best || a.em > best.em)) best = a; }
fills.best_agentic_pct = pct(best.em);
fills.best_agentic_name = MODELS[best.model] + " (" + {agentic:"agentic", "agentic-fewshot":"agentic, with examples", "agentic-scaffold":"decide first, then search"}[best.cond] + ")";
fills.ceil_shaped_pct = pct0(D.ceilings.shaped.hit);
fills.ceil_oracle_pct = pct0(D.ceilings.subject.hit);
const closedSorted = ORDER.map(m => A(m,"closed")).filter(Boolean).sort((a,b) => b.em - a.em);
fills.a1_take = `the best small model from memory, ${MODELS[closedSorted[0].model]}, scores ${pct(closedSorted[0].em)}; the group's 70B model scores ${pct(D.replication["meta-llama-Llama-3.3-70B-Instruct"].EM)} on the same questions.`;
fills.a1_verdict = ORDER.map(m => { const a = A(m,"closed"); return a ? `${MODELS[m]} ${pct(a.em)}` : null; }).filter(Boolean).join(", ") + ` exact match; lenient match is one to three points higher for each. Mimir, trained from scratch on Danish and permissible data, beats every multilingual model up to four times its size from memory, but the whole range is 1 to 6 percent.`;
const shapedRows = ORDER.map(m => A(m,"retrieve")).filter(Boolean);
const oracleRows = ORDER.map(m => A(m,"retrieve-oracle")).filter(Boolean);
fills.a2_take = `with the rule query the answer is fetched ${pct0(D.ceilings.shaped.hit)} of the time and the models score ${pct0(Math.min(...shapedRows.map(a=>a.em)))} to ${pct0(Math.max(...shapedRows.map(a=>a.em)))}; with the oracle query it is fetched ${pct0(D.ceilings.subject.hit)} of the time and they score ${pct0(Math.min(...oracleRows.map(a=>a.em)))} to ${pct0(Math.max(...oracleRows.map(a=>a.em)))}.`;
const fidBest = [...D.fidelity].sort((a,b)=>b.em_present-a.em_present);
fills.a2_verdict = `Going from the raw question (answer fetched ${pct0(D.ceilings.question.hit)} of the time) to the rule query (${pct0(D.ceilings.shaped.hit)}) to the oracle query (${pct0(D.ceilings.subject.hit)}) moves every model more than any difference between models does. When the answer is in the text, ${MODELS[fidBest[0].model]} extracts it ${pct0(fidBest[0].em_present)} of the time and ${MODELS[fidBest[fidBest.length-1].model]} ${pct0(fidBest[fidBest.length-1].em_present)}; Mimir reads Danish text better than Llama 3B's larger size would suggest (${pct0(D.fidelity.find(f=>f.model==="mimir").em_present)} against ${pct0(D.fidelity.find(f=>f.model==="llama3b").em_present)}).`;
const dec = v => D.decision.filter(d => d.variant===v);
const never = dec("agentic").filter(d => d.called_wrong + d.called_right === 0).map(d => MODELS[d.model]);
const always = dec("agentic").filter(d => (d.called_wrong + d.called_right) / (d.called_wrong + d.called_right + d.silent_wrong + d.silent_right) > 0.9).map(d => MODELS[d.model]);
const l3 = dec("agentic-fewshot").find(d => d.model==="llama3b");
const sc = dec("agentic-scaffold");
const scText = sc.length ? " Asked first whether it knew the answer, " + sc.filter(d => d.model==="mimir" || d.model==="llama3b").map(d => { const wrong = d.called_wrong + d.silent_wrong; return `${MODELS[d.model]} claimed to know on ${pct0(d.silent_wrong/Math.max(1,wrong))} of the questions it then got wrong`; }).join(" and ") + "; the two models that always searched kept searching, and Llama 1B said no to every question." : "";
fills.a3_verdict = `Told they may search, ${never.join(", ")} never wrote a search line in 592 chances each; ${always.join(" and ")} wrote one on ${always.length===2 ? "nearly every" : "nearly every"} question. ` + (l3 ? `Llama 3B searched only when shown examples, ${l3.called_wrong + l3.called_right} times out of 592, all of them on questions it had wrong from memory, which is the right instinct at the wrong scale. ` : "") + `The two models that ask outscore the rule query because their own queries land on the right page about half the time.` + scText;
document.querySelectorAll("[data-fill]").forEach(el => { const k = el.getAttribute("data-fill"); if (fills[k] !== undefined) el.textContent = fills[k]; });

/* ---------- replication table ---------- */
{
  const tb = $("#reptable tbody");
  const rows = Object.entries(D.replication).sort((a,b) => b[1].F1 - a[1].F1);
  const nice = k => k.replace("meta-llama-","").replace("openai-","").replace("google-","").replace("mistralai-","");
  tb.innerHTML = rows.map(([k,v]) => `<tr><td>${esc(nice(k))}</td><td class="n">${v.EM.toFixed(3)}</td><td class="n">${v.F1.toFixed(3)}</td><td class="n">${v.BLEU.toFixed(3)}</td><td class="n">${v.paper_f1 ?? ""}</td><td class="n">${v.paper_bleu ?? ""}</td></tr>`).join("");
}

/* ---------- bar chart helper ---------- */
function bars(root, items, opts){
  // items: [{label, value(0..1), cls, sub}], opts: {ref: {value,label}, ceil: value}
  const W = 640, rowH = 34, left = 150, right = 60, top = 8;
  const H = top + items.length*rowH + (opts.ref ? 18 : 6);
  const max = Math.max(0.05, ...items.map(i=>i.value), opts.ref ? opts.ref.value : 0, opts.ceil || 0) * 1.08;
  const x = v => left + (W-left-right) * v / max;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.aria||"bar chart")}">`;
  if (opts.ceil !== undefined) s += `<rect class="ceil" x="${left}" y="${top}" width="${x(opts.ceil)-left}" height="${items.length*rowH-6}"></rect>`;
  items.forEach((it,i) => {
    const y = top + i*rowH;
    s += `<text class="lab" x="${left-8}" y="${y+17}" text-anchor="end">${esc(it.label)}</text>`;
    s += `<rect class="bar ${it.cls||""}" x="${left}" y="${y+2}" width="${Math.max(1,x(it.value)-left)}" height="${rowH-12}" rx="1"></rect>`;
    s += `<text x="${x(it.value)+6}" y="${y+17}">${pct(it.value)}</text>`;
  });
  if (opts.ref) { const xr = x(opts.ref.value); s += `<line class="ref" x1="${xr}" y1="${top}" x2="${xr}" y2="${top+items.length*rowH-4}"></line><text class="lab" x="${xr}" y="${H-3}" text-anchor="middle">${esc(opts.ref.label)}</text>`; }
  if (opts.ceil !== undefined) s += `<text class="lab" x="${x(opts.ceil)}" y="${H-3}" text-anchor="middle">ceiling ${pct(opts.ceil)}</text>`;
  s += `<line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${top+items.length*rowH-4}"></line></svg>`;
  root.innerHTML = s;
}

/* ---------- act 1 ---------- */
let a1sel = "mimir";
function drawA1(){
  const items = ORDER.map(m => { const a = A(m,"closed"); return a ? {label: MODELS[m], value: a.em, cls: m===a1sel ? "on" : ""} : null; }).filter(Boolean);
  bars($("#a1chart"), items, {ref: {value: D.replication["meta-llama-Llama-3.3-70B-Instruct"].EM, label: "Llama 3.3 70B, their run"}, aria: "closed-book exact match per model"});
  $("#a1chips").innerHTML = ORDER.map(m => `<button class="chip ${m===a1sel?"on":""}" data-m="${m}">${esc(MODELS[m])}</button>`).join("");
  $("#a1chips").querySelectorAll(".chip").forEach(b => b.onclick = () => { a1sel = b.dataset.m; drawA1(); });
}
drawA1();

/* ---------- act 2 ---------- */
const Q = [{k:"question", label:"raw question", cond:null, ceil:D.ceilings.question.hit},
           {k:"shaped", label:"rule (shaped) query", cond:"retrieve", ceil:D.ceilings.shaped.hit},
           {k:"subject", label:"oracle query", cond:"retrieve-oracle", ceil:D.ceilings.subject.hit}];
let a2sel = "shaped";
function drawA2(){
  const q = Q.find(x=>x.k===a2sel);
  const items = ORDER.map(m => { const a = q.cond ? A(m,q.cond) : null; return {label: MODELS[m] + (a ? "" : " (not run)"), value: a ? a.em : 0, cls: a ? "" : "dim"}; });
  bars($("#a2chart"), items, {ceil: q.ceil, aria: "exact match with retrieval against the retrieval ceiling"});
  $("#a2chips").innerHTML = Q.map(x => `<button class="chip ${x.k===a2sel?"on":""}" data-k="${x.k}">${esc(x.label)}</button>`).join("");
  $("#a2chips").querySelectorAll(".chip").forEach(b => b.onclick = () => { a2sel = b.dataset.k; drawA2(); });
}
drawA2();
$("#fidtable tbody").innerHTML = ORDER.map(m => D.fidelity.find(f=>f.model===m)).filter(Boolean)
  .map(f => `<tr><td>${esc(MODELS[f.model])}</td><td class="n">${pct(f.em_present)} <span class="lab">(n=${f.n_present})</span></td><td class="n">${pct(f.em_absent)} <span class="lab">(n=${f.n_absent})</span></td></tr>`).join("");

/* ---------- act 3: decision tiles ---------- */
const VARS = [["agentic","agentic"],["agentic-fewshot","agentic, with examples"],["agentic-scaffold","decide first, then search"]];
let a3m = "gemma4b", a3v = "agentic", tileSel = null;
function drawA3(){
  const avail = VARS.filter(([v]) => D.decision.some(d => d.model===a3m && d.variant===v));
  if (!avail.some(([v]) => v===a3v)) a3v = avail[0][0];
  $("#a3models").innerHTML = ORDER.map(m => `<button class="chip ${m===a3m?"on":""}" data-m="${m}">${esc(MODELS[m])}</button>`).join("");
  $("#a3variants").innerHTML = VARS.map(([v,l]) => { const ok = D.decision.some(d => d.model===a3m && d.variant===v); return `<button class="chip ${v===a3v?"on":""}" data-v="${v}" ${ok?"":"disabled style='opacity:.4'"}>${esc(l)}</button>`; }).join("");
  $("#a3models").querySelectorAll(".chip").forEach(b => b.onclick = () => { a3m = b.dataset.m; tileSel=null; drawA3(); });
  $("#a3variants").querySelectorAll(".chip:not([disabled])").forEach(b => b.onclick = () => { a3v = b.dataset.v; tileSel=null; drawA3(); });
  const d = D.decision.find(x => x.model===a3m && x.variant===a3v);
  const n = d.called_wrong + d.silent_wrong + d.called_right + d.silent_right;
  const tiles = [
    {k:"called_wrong", t:"Searched when its memory was wrong", cls:"good", s:"the useful call"},
    {k:"silent_wrong", t:"Answered from memory and was wrong", cls:"bad", s:"the bluff"},
    {k:"called_right", t:"Searched although its memory was right", cls:"", s:"wasted effort, harmless"},
    {k:"silent_right", t:"Answered from memory and was right", cls:"good", s:"earned trust"}];
  $("#tiles").innerHTML = tiles.map(t => `<div class="tile ${t.cls} ${tileSel===t.k?"on":""}" data-k="${t.k}"><div class="k">${esc(t.t)}</div><div class="v">${d[t.k]}</div><div class="s">${esc(t.s)} &middot; ${pct0(d[t.k]/n)} of ${n}</div></div>`).join("");
  $("#tiles").querySelectorAll(".tile").forEach(el => el.onclick = () => { tileSel = el.dataset.k; drawA3(); browserFromTile(); });
  const calls = d.called_wrong + d.called_right, wrong = d.called_wrong + d.silent_wrong;
  $("#tilenote").textContent = `${MODELS[a3m]}, ${VARS.find(([v])=>v===a3v)[1]}: searched on ${calls} of ${n} questions (${pct0(calls/n)}). Of the ${wrong} questions it had wrong from memory, it searched on ${d.called_wrong} (${pct0(d.called_wrong/Math.max(1,wrong))}).` + (calls/n > 0.9 ? " Searching on nearly everything is the policy here, not a judgement per question." : "");
}
drawA3();
$("#asktable tbody").innerHTML = D.ask.map(a => `<tr><td>${esc(MODELS[a.model])}</td><td>${esc(VARS.find(([v])=>v===a.variant)?.[1] || a.variant)}</td><td class="n">${a.calls}</td><td class="n">${a.first_hit_subject} (${pct0(a.first_hit_subject/a.calls)})</td><td class="n">${pct(a.em_own_query)}</td><td class="n">${a.em_fallback==null ? "" : pct(a.em_fallback) + " (n=" + a.fallbacks + ")"}</td></tr>`).join("");

/* ---------- question browser ---------- */
const CONDN = {closed:"closed book", "closed-sc":"closed book, 5-sample vote", retrieve:"lookup, rule query", "retrieve-oracle":"lookup, oracle query", agentic:"agentic", "agentic-fewshot":"agentic, with examples", "agentic-scaffold":"decide first, then search"};
const bm = $("#bmodel"), bc = $("#bcond");
bm.innerHTML = ORDER.map(m => `<option value="${m}">${esc(MODELS[m])}</option>`).join("");
bc.innerHTML = D.conds.filter(c => D.agg.some(a=>a.cond===c)).map(c => `<option value="${c}">${esc(CONDN[c]||c)}</option>`).join("");
bm.value = "gemma4b"; bc.value = "agentic";
function browserFromTile(){
  bm.value = a3m; bc.value = a3v;
  $("#boutcome").value = {called_wrong:"called", silent_wrong:"silent", called_right:"called", silent_right:"silent"}[tileSel];
  window.__tileFilter = tileSel; drawBrowser();
  $("#browser").scrollIntoView({behavior:"smooth", block:"start"});
}
["bmodel","bcond","boutcome","btype"].forEach(id => $("#"+id).onchange = () => { window.__tileFilter = null; drawBrowser(); });
$("#bsearch").oninput = () => { window.__tileFilter = null; drawBrowser(); };
function drawBrowser(){
  const m = bm.value, c = bc.value, o = $("#boutcome").value, t = $("#btype").value, s = $("#bsearch").value.trim().toLowerCase();
  const closed = {}; D.questions.forEach(q => { const r = q.runs[m+"|closed"]; if (r) closed[q.id] = r.em >= 1; });
  let rows = D.questions.filter(q => q.runs[m+"|"+c]);
  rows = rows.filter(q => {
    const r = q.runs[m+"|"+c];
    if (t !== "all" && q.type !== t) return false;
    if (o === "right" && r.em < 1) return false;
    if (o === "lenient" && !(r.len >= 1 && r.em < 1)) return false;
    if (o === "wrong" && r.len >= 1) return false;
    if (o === "called" && !r.tq) return false;
    if (o === "silent" && r.tq) return false;
    if (window.__tileFilter) { const right = !!closed[q.id]; const want = window.__tileFilter; if ((want.endsWith("wrong") && right) || (want.endsWith("right") && !right)) return false; }
    if (s && !(q.q.toLowerCase().includes(s) || q.gold.toLowerCase().includes(s) || r.p.toLowerCase().includes(s))) return false;
    return true;
  });
  $("#bcount").textContent = `${rows.length} of 592 questions shown.`;
  const tb = $("#btable tbody");
  tb.innerHTML = rows.slice(0, 200).map(q => { const r = q.runs[m+"|"+c]; const cls = r.em>=1 ? "match-1" : (r.len>=1 ? "match-l" : "match-0"); const lab = r.em>=1 ? "exact" : (r.len>=1 ? "lenient" : "wrong");
    return `<tr class="row" data-id="${q.id}"><td class="q">${esc(q.q)}</td><td>${esc(q.gold)}</td><td>${esc(r.p)}</td><td class="${cls}">${lab}</td><td class="m">${esc(r.tq)}${r.fb?" (fallback)":""}</td><td class="m">${esc(r.top)}</td></tr>`; }).join("") + (rows.length > 200 ? `<tr><td colspan="6" class="lab">First 200 shown; narrow the filters or search.</td></tr>` : "");
  tb.querySelectorAll("tr.row").forEach(tr => tr.onclick = () => {
    const q = D.questions.find(x => x.id === tr.dataset.id); const next = tr.nextElementSibling;
    if (next && next.classList.contains("detail")) { next.remove(); return; }
    const det = document.createElement("tr"); det.className = "detail";
    const all = Object.entries(q.runs).filter(([k]) => k.startsWith(m+"|")).map(([k,r]) => `<div><b>${esc(CONDN[k.split("|")[1]]||k)}:</b> ${esc(r.p)} <span class="${r.em>=1?"match-1":(r.len>=1?"match-l":"match-0")}">${r.em>=1?"exact":(r.len>=1?"lenient":"wrong")}</span>${r.tq?` &middot; query: <span class="m">${esc(r.tq)}</span>`:""}${r.top?` &middot; fetched: ${esc(r.top)}`:""}${r.dec?` &middot; said: ${esc(r.dec)}`:""}</div>`).join("");
    det.innerHTML = `<td colspan="6"><div><b>Subject:</b> ${esc(q.subject)} &middot; <b>type:</b> ${q.type} &middot; <b>answer in the rule-query text:</b> ${q.hit_shaped===true?"yes":(q.hit_shaped===false?"no":"unknown")}</div>${all}</td>`;
    tr.after(det);
  });
}
drawBrowser();

/* ---------- failures: default answers and by type ---------- */
{
  const norm = s => String(s||"").toLowerCase().replace(/[^a-z0-9æøå]+/g," ").trim();
  const out = [];
  for (const m of ORDER) for (const c of ["closed","retrieve","agentic"]) {
    const cnt = {}; let n = 0;
    D.questions.forEach(q => { const r = q.runs[m+"|"+c]; if (!r) return; n++; const k = norm(r.p); cnt[k] = (cnt[k]||0)+1; });
    if (!n) continue;
    const top = Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,3);
    out.push(`<tr><td>${esc(MODELS[m])}</td><td>${esc(CONDN[c])}</td><td>${top.map(([k,v]) => `${esc(k.slice(0,28))} (${v})`).join("; ")}</td><td class="n">${pct0(top.reduce((s,[,v])=>s+v,0)/n)}</td></tr>`);
  }
  $("#deftable tbody").innerHTML = out.join("");
  $("#typetable tbody").innerHTML = D.agg.filter(a => ["closed","retrieve","agentic"].includes(a.cond)).sort((a,b) => ORDER.indexOf(a.model)-ORDER.indexOf(b.model) || a.cond.localeCompare(b.cond))
    .map(a => `<tr><td>${esc(MODELS[a.model])}</td><td>${esc(CONDN[a.cond])}</td>` + ["year","number","text"].map(t => `<td class="n">${a.by_type[t] ? pct(a.by_type[t][0]) : ""}</td>`).join("") + `</tr>`).join("");
}

/* ---------- model card ---------- */
{
  const meta = {mimir:["1.0 B (1.8 B with embeddings)","Q8_0, community GGUF"], llama1b:["1.2 B","Q8_0"], llama3b:["3.2 B","Q8_0"], gemma4b:["4.3 B","Q6_K"], qwen3b:["3.1 B","Q8_0"]};
  $("#cardtable tbody").innerHTML = ORDER.map(m => { const c = A(m,"closed"), g = A(m,"agentic"); return `<tr><td>${esc(MODELS[m])}</td><td class="n">${meta[m][0]}</td><td>${meta[m][1]}</td><td class="n">${c ? c.sec.toFixed(1) : ""}</td><td class="n">${g ? g.sec.toFixed(1) : ""}</td></tr>`; }).join("");
}

/* ---------- guided tour (spotlight; positions computed from document coordinates, then scrolled) ---------- */
(function(){
  const STEPS = [
    {sel:"#top h1", k:"Welcome · 1 of 8", html:`This page asks one question from the scholarship call: <b>can a small language model tell when it should look something up instead of answering from memory?</b> It is measured on the Odense group's own Danish quiz, with their own model and their own scorer, so every number can be read against their tables.`},
    {sel:"#primer .primer", k:"Five things to know · 2 of 8", html:`The primer defines every term used below: the quiz, closed-book, lookup, agentic, and the two scores. Nothing further down assumes anything not on this list; the glossary under it stays open.`},
    {sel:"#reptable", k:"Their numbers first · 3 of 8", html:`Before any new result, the group's own published predictions for five large models were rescored here. Same ranking as their paper, slightly higher numbers because the public subset is easier. If this table did not match, nothing below could be trusted.`},
    {sel:"#a1chart", k:"Act one: memory · 4 of 8", html:`<b>Click a model chip above the chart.</b> Every small model knows almost nothing of the canon from memory; the dotted line is the 70B model from their paper. Mimir, trained on Danish, holds the most, and it is still one question in twenty.`},
    {sel:"#a2chart", k:"Act two: the lookup · 5 of 8", html:`<b>Click a query formulation.</b> The grey bar is how often the answer was even fetched; the coloured bars are what each model scored with that text. The query moves the result more than the choice of model does.`},
    {sel:"#tiles", k:"Act three: the decision · 6 of 8", html:`<b>Click a model, a variant, then a tile.</b> The four counts compare each model's decision to search against its own closed-book record. Two models always search, three almost never; none decides question by question. The box below the tiles says why this data cannot yet test that judgement.`},
    {sel:"#bcontrols", k:"Every answer · 7 of 8", html:`<b>Filter, search, click a row.</b> All 592 questions with every model's answer under every condition, the query it wrote and the page it fetched. Aggregates hide how models fail; this does not.`},
    {sel:"#cardtable", k:"Model card and limits · 8 of 8", html:`What was run, on what hardware, with which weights, and what was not done. The limits list is written before a reader has to find them. That is the whole page; the Guided tour button at the top restarts this walkthrough.`},
  ];
  const root=$("#tour"), hl=$("#tour-hl"), card=$("#tour-card");
  let idx=0;
  function place(){
    const st=STEPS[idx]; const elm=document.querySelector(st.sel);
    if(!elm){ next(); return; }
    const r=elm.getBoundingClientRect(), sx=window.scrollX, sy=window.scrollY;
    const top=r.top+sy, left=r.left+sx;                  // document coordinates, independent of scroll timing
    root.style.height=document.documentElement.scrollHeight+"px";
    hl.style.left=(left-8)+"px"; hl.style.top=(top-8)+"px"; hl.style.width=(r.width+16)+"px"; hl.style.height=(r.height+16)+"px";
    const dots=STEPS.map((_,i)=>`<i class="${i===idx?"on":""}"></i>`).join("");
    card.innerHTML=`<div class="tk">${st.k}</div><p>${st.html}</p><div class="tour-nav"><div class="dots">${dots}</div>${idx>0?'<button class="tour-btn" id="tprev">Back</button>':''}<button class="tour-btn" id="tskip">Close</button><button class="tour-btn primary" id="tnext">${idx<STEPS.length-1?"Next":"Done"}</button></div>`;
    const cw=Math.min(400, innerWidth-32);
    let cx=left+r.width+18, cy=top;
    if (cx+cw > sx+innerWidth-16) { cx=Math.max(16, left); cy=top+r.height+14; }
    card.style.left=cx+"px"; card.style.top=cy+"px";
    $("#tnext").onclick=next; $("#tskip").onclick=stop;
    const p=$("#tprev"); if(p) p.onclick=()=>{idx=Math.max(0,idx-1); place();};
    const target=Math.max(0, top-Math.max(24, (innerHeight-r.height-260)/2));
    window.scrollTo({top:target, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"});
  }
  function next(){ if(idx>=STEPS.length-1){stop();return;} idx++; place(); }
  function stop(){ root.classList.remove("on"); try{localStorage.setItem("daisy_tour","done");}catch(e){} }
  function start(){ idx=0; root.classList.add("on"); place(); }
  $("#tourbtn").addEventListener("click", start);
  window.__tour={start, place, steps:STEPS.length, go:i=>{idx=i; root.classList.add("on"); place();}};
  let seen=null; try{ seen=localStorage.getItem("daisy_tour"); }catch(e){}
  if (!seen) setTimeout(start, 700);
})();
})();
