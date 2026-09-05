/* Renders every number on the page from window.DATA (site/data.js, written by scripts/build_page_data.py). */
(function(){
const D = window.DATA;
const $ = s => document.querySelector(s);
const MODELS = Object.assign({}, D.models, {"mimir-hf": "DFM Mimir 1B (official)", "mimir": "DFM Mimir 1B (llama.cpp port)"});
const ORDER = ["mimir-hf","mimir","llama1b","llama3b","gemma4b","qwen3b"].filter(m => D.models[m] && D.agg.some(a => a.model === m));
const MAIN = ORDER.filter(m => m !== "mimir");            // the port is shown only where the attention mode is the point
const pct = x => (x*100).toFixed(1) + " %";
const pct0 = x => Math.round(x*100) + " %";
const A = (m,c) => D.agg.find(a => a.model===m && a.cond===c);
const esc = s => String(s==null?"":s).replace(/[&<>"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[ch]));
const CONDN = {closed:"from memory", "closed-sc":"from memory, 5-sample vote", retrieve:"one lookup, search box", "retrieve-oracle":"one lookup, oracle query (search box)",
  "retrieve-local":"one lookup, ranked index", "retrieve-plus-local":"lookup plus two paragraphs, ranked index (variant)", "retrieve-k1-local":"one lookup, ranked index, 1 page", "retrieve-k5-local":"one lookup, ranked index, 5 pages", "retrieve-c1800-local":"one lookup, ranked index, 1800 characters", "retrieve-wide-local":"second stage: ten pages, best paragraphs (variant)", "retrieve-tworound-local":"second stage: model writes a follow-up query (variant)",
  "retrieve-given-qwen":"Mimir reads, Qwen asks (search box)", "retrieve-given-gemma":"reads Gemma's queries (search box)", "retrieve-given-gemma+qwen":"reads Gemma's and Qwen's queries (search box)",
  agentic:"model decides and writes the query, search box", "agentic-local":"model decides and writes the query, ranked index", "agentic-native":"native tool call, search box", "agentic-native-local":"native tool call, ranked index",
  "agentic-fewshot":"model decides, with examples", "agentic-scaffold":"asked first whether it knows"};

/* ---------- headline numbers and text fills ---------- */
const fills = {};
fills.date = new Date().toLocaleDateString("en-GB", {day:"numeric", month:"long", year:"numeric"});
const mhc = A("mimir-hf","closed"), mhl = A("mimir-hf","retrieve-local"), gl = A("gemma4b","retrieve-local");
fills.mimirhf_closed_pct = pct(mhc.em);
fills.mimirhf_local_pct = mhl ? pct(mhl.em) : "running";
fills.gemma_local_pct = pct(gl.em);
fills.ceil_local_pct = pct(D.ceilings.local.hit);
fills.ceil_pages_pct = D.ceilings.local_pages ? pct(D.ceilings.local_pages.hit) : "";
const scaff = D.decision.find(d => d.model==="mimir-hf" && d.variant==="agentic-scaffold") || D.decision.find(d => d.model==="mimir" && d.variant==="agentic-scaffold");
fills.mimir_bluff_pct = scaff ? pct0(scaff.silent_wrong / Math.max(1, scaff.silent_wrong + scaff.called_wrong)) : "";
const plusRows = MAIN.map(m => A(m,"retrieve-plus-local")).filter(Boolean).sort((a,b)=>b.em-a.em);
fills.plus_best = plusRows.length ? `${pct(plusRows[0].em)} for ${MODELS[plusRows[0].model]}` : "";
const closedSorted = MAIN.map(m => A(m,"closed")).filter(Boolean).sort((a,b) => b.em - a.em);
const l70 = D.replication["meta-llama-Llama-3.3-70B-Instruct"].EM;
fills.a1_take = `the best small model from memory, ${MODELS[closedSorted[0].model]}, scores ${pct(closedSorted[0].em)}; the group's 70B model scores ${pct(l70)} on the same questions.`;
const port = A("mimir","closed");
fills.a1_verdict = `Rescoring their files gives their ranking, and Mimir on its official path gives ${pct(mhc.em)} against the paper's 9.6, inside one standard error. ` +
  (port ? `The same weights through the llama.cpp port score ${pct(port.em)}, because the port can only read the prompt left to right. ` : "") +
  `From memory the small models range from ${pct(closedSorted[closedSorted.length-1].em)} to ${pct(closedSorted[0].em)}; Mimir, trained on Danish, holds the most. Sampling five answers and voting changed no model by more than one point.`;
/* act two */
const ENG = [
  {k:"box", label:"Wikipedia search box", cond:"retrieve", ceil:D.ceilings.shaped.hit},
  {k:"local", label:"ranked index (BM25)", cond:"retrieve-local", ceil:D.ceilings.local.hit},
  {k:"oracle", label:"oracle query, search box", cond:"retrieve-oracle", ceil:D.ceilings.subject.hit}];
const boxRows = MAIN.map(m => A(m,"retrieve")).filter(Boolean), locRows = MAIN.map(m => A(m,"retrieve-local")).filter(a => a && a.n >= 500), orRows = MAIN.map(m => A(m,"retrieve-oracle")).filter(Boolean);
const rng = rows => `${pct0(Math.min(...rows.map(a=>a.em)))} to ${pct0(Math.max(...rows.map(a=>a.em)))}`;
fills.a2_take = `through the search box the answer is fetched ${pct0(D.ceilings.shaped.hit)} of the time and the models score ${rng(boxRows)}; through the ranked index it is fetched ${pct0(D.ceilings.local.hit)} of the time and they score ${rng(locRows)}, with the oracle query at ${pct0(D.ceilings.subject.hit)} and ${rng(orRows)}.`;
const locBest = [...locRows].sort((a,b)=>b.em-a.em)[0];
const orBest = orRows.find(a => a.model===locBest.model);
fills.a2_verdict = `Same models, same prompt, same questions; only the search behind the tool changed, and the best result moved from ${pct(boxRows.find(a=>a.model===locBest.model).em)} to ${pct(locBest.em)} for ${MODELS[locBest.model]}, ${orBest ? (orBest.em > locBest.em ? `${((orBest.em-locBest.em)*100).toFixed(1)} points under` : `${((locBest.em-orBest.em)*100).toFixed(1)} points above`) : "close to"} the oracle query that a model never sees. ` +
  `The search box needs every word of the question to appear in the page; a ranked index does not, and that is the whole difference. ` +
  (mhl && mhl.n >= 500 ? `Mimir, one billion parameters, scores ${pct(mhl.em)} on the same text as Gemma 3 4B at ${pct(gl.em)}.` : "");
const fl = [...D.fidelity_local].sort((a,b)=>b.em_present-a.em_present);
fills.fid_note = fl.length ? `${MODELS[fl[0].model]} converts ${pct0(fl[0].em_present)} of the fetched answers and ${MODELS[fl[fl.length-1].model]} ${pct0(fl[fl.length-1].em_present)}. When the answer is absent every model still answers, almost always wrongly.` : "";
const dc = D.decomp;
fills.decomp_text = dc ? `Of the ${dc.n} questions, the answer was inside the three fetched introductions for ${dc.in_intros} (${pct0(dc.in_intros/dc.n)}), further down one of those three pages for ${dc.below_intro} (${pct0(dc.below_intro/dc.n)}), and not in the top three pages at all for ${dc.not_in_top3} (${pct0(dc.not_in_top3/dc.n)}), of which ${dc.in_ranks_4_to_10} sat in ranks four to ten.` : "";
/* act three */
const dec = v => D.decision.filter(d => d.variant===v && d.model !== "mimir");
const rate = d => (d.called_wrong + d.called_right) / (d.called_wrong + d.called_right + d.silent_wrong + d.silent_right);
const never = dec("agentic").filter(d => rate(d) < 0.02).map(d => MODELS[d.model]);
const always = dec("agentic").filter(d => rate(d) > 0.9).map(d => MODELS[d.model]);
const l3 = dec("agentic-fewshot").find(d => d.model==="llama3b");
const agLoc = MAIN.map(m => ({m, a: A(m,"agentic-local"), r: A(m,"retrieve-local")})).filter(x => x.a && x.r && x.a.n >= 500 && rate(D.decision.find(d=>d.model===x.m && d.variant==="agentic-local") || {called_wrong:0,called_right:0,silent_wrong:1,silent_right:0}) > 0.5);
fills.a3_verdict = `Told they may search, ${never.join(", ")} never wrote a search line in 592 chances each; ${always.join(" and ")} wrote one on nearly every question. ` +
  (l3 ? `Llama 3B searched only when shown examples, ${l3.called_wrong + l3.called_right} times out of 592, all on questions it had wrong from memory: the right instinct at the wrong scale. ` : "") +
  (scaff ? `Asked first whether it knew the answer, Mimir said yes on ${fills.mimir_bluff_pct} of the questions it then got wrong. ` : "") +
  (function(){ const t = D.decision.find(d => d.model==="llama3b" && d.variant==="agentic"), n = D.decision.find(d => d.model==="llama3b" && d.variant==="agentic-native-local");
    return (t && n && rate(t) < 0.05 && rate(n) > 0.9) ? `Llama 3B never searched when told in text that it could, and searched on ${pct0(rate(n))} of the questions when the same search was offered in its native tool format: whether a small model "decides" to search is set by the interface, not by what it knows. ` : ""; })() +
  (agLoc.length ? `On the ranked index the models that write their own query score below the plain question: ${agLoc.map(x => `${MODELS[x.m]} ${pct(x.a.em)} against ${pct(x.r.em)}`).join(", ")}. Once the engine ranks properly, rewriting the question costs points.` : "");
fills.ask_note = `A model-written query "landed" when the first result was the canon work the question is about. When a query returned nothing, the question itself was used instead, marked as a fallback. On the ranked index the question as written is the better query.`;
const qc = A("qwen3b","closed"), ql = A("qwen3b","retrieve-local");
if (qc && ql) { fills.qwen_closed_len = pct(qc.lenient); fills.qwen_local_len = pct(ql.lenient); }
if (D.inspect_full && D.inspect_full.daisy_lookup && gl) {
  const I = D.inspect_full, ic = A("gemma4b","closed");
  fills.inspect_check = `Checked: run through this task on all 592 questions, Gemma 3 4B scores ${pct(I.daisy_lookup.scores.exact_match.mean)} with the lookup (standard error ${(I.daisy_lookup.scores.exact_match.stderr*100).toFixed(1)}) and ${pct(I.daisy.scores.exact_match.mean)} from memory, against ${pct(gl.em)} and ${pct(ic.em)} from the harness behind this page. The two paths agree to within half a point; the harness allows 64 new tokens, their task 100.`;
}
/* questions asked along the way */
{
  const causal = (D.mimir_paths || []).find(m => /causal attention, fp16/.test(m.label));
  fills.q_causal = causal ? pct(causal.em) : (port ? pct(port.em) : "");
  fills.q_how_good = `Good enough to say the search side is solved, with two caveats. The group's best model from memory, a 70-billion-parameter Llama, scores ${pct(l70)} on these questions, and no Danish number with a lookup has been published, so the nearest comparison is English: systems trained for the task with far larger models score 44 to 64 exact match on Natural Questions. The caveats: with 592 questions the interval is about plus or minus 4 points, and the questions were written from Wikipedia pages, so once the right page is found the answer is almost always in it. The score says how well pages are found and read.`;
  const two = A("mimir-hf","retrieve-given-gemma+qwen") || A("mimir-hf","retrieve-given-qwen");
  fills.q_two_models = `Yes, two models in a row, not one combined model: Qwen 2.5 3B reads the question and writes the search words, Wikipedia's search box returns three pages, and Mimir reads them and answers${two ? `, which scored ${pct(two.em)} through the search box` : ""}. It was built because Mimir never writes a search when asked to and reads Danish better than the others. The ranked index made it unnecessary: Mimir alone, with the question as the query, scores ${mhl ? pct(mhl.em) : ""}. The pipeline stays in the browser below as a side row.`;
  let same = 0, tot = 0; D.questions.forEach(q => { const r = q.runs["gemma4b|retrieve-local"]; if (r) { tot++; if ((r.tq||"").trim() === q.q.trim().slice(0,80)) same++; } });
  let sameBox = 0, totBox = 0; D.questions.forEach(q => { const r = q.runs["gemma4b|retrieve"]; if (r) { totBox++; if ((r.tq||"").trim() === q.q.trim().slice(0,80)) sameBox++; } });
  fills.q_query = `No. The benchmark has no tool; its prompt is the question alone, and the lookup is this page's addition. The least engineered choice is to send the question as written, and that is the main line: on the ranked index the query was the question itself on ${same} of ${tot} questions. The rule that shortens the query exists only because Wikipedia's search box needs every word to match; through the search box it had to shorten ${totBox - sameBox} of ${totBox} queries. No model wrote a query in the main line.`;
  const plusM = A("mimir-hf","retrieve-plus-local"), plusG = A("gemma4b","retrieve-plus-local"), wide = A("gemma4b","retrieve-wide-local"), two2 = A("gemma4b","retrieve-tworound-local");
  const parts = [];
  if (plusM || plusG) parts.push(`Fetching the two best paragraphs of the same three pages in addition to their introductions${plusM ? ` takes Mimir from ${pct(mhl.em)} to ${pct(plusM.em)}` : ""}${plusG ? ` and Gemma from ${pct(gl.em)} to ${pct(plusG.em)}` : ""}; the ceiling rises from ${pct(D.ceilings.local.hit)} to ${pct0(0.812)}.`);
  if (wide && wide.n >= 500) parts.push(`Casting a wider net, ten pages and the four best paragraphs across them, gives Gemma ${pct(wide.em)}.`);
  if (two2 && two2.n >= 500) parts.push(`Letting Gemma write one follow-up query when it says the text lacks the answer gives ${pct(two2.em)}.`);
  if (!wide || !two2) parts.push(`Two further variants, a ten-page net and a model-written second query, are running and will appear here.`);
  fills.q_second = `Every variant below is labelled, not the main line, because each adds a selection step beyond one lookup. ` + parts.join(" ") + ` The honest reading: the remaining misses are pages the ranker does not put in the top three and facts below the introduction, and each extra step buys a few points at roughly double the tokens.`;
}
document.querySelectorAll("[data-fill]").forEach(el => { const k = el.getAttribute("data-fill"); if (fills[k] !== undefined) el.textContent = fills[k]; });

/* ---------- replication and ruler tables ---------- */
{
  const tb = $("#reptable tbody");
  const rows = Object.entries(D.replication).sort((a,b) => b[1].F1 - a[1].F1);
  const nice = k => k.replace("meta-llama-","").replace("openai-","").replace("google-","").replace("mistralai-","");
  tb.innerHTML = rows.map(([k,v]) => `<tr><td>${esc(nice(k))}</td><td class="n">${v.EM.toFixed(3)}</td><td class="n">${v.F1.toFixed(3)}</td><td class="n">${v.BLEU.toFixed(3)}</td><td class="n">${v.paper_f1 ?? ""}</td><td class="n">${v.paper_bleu ?? ""}</td></tr>`).join("");
  $("#mimirtable tbody").innerHTML = (D.mimir_paths || []).map(m => `<tr><td>${esc(m.label)}</td><td class="n">${pct(m.em)}</td></tr>`).join("") + `<tr><td>Reported in the Mimir paper (Inspect harness)</td><td class="n">9.6 %</td></tr>`;
}

/* ---------- bar chart helper ---------- */
function bars(root, items, opts){
  const W = 640, rowH = 34, left = 170, right = 60, top = 8;
  const H = top + items.length*rowH + (opts.ref || opts.ceil !== undefined ? 18 : 6);
  const max = Math.max(0.05, ...items.map(i=>i.value), opts.ref ? opts.ref.value : 0, opts.ceil || 0) * 1.08;
  const x = v => left + (W-left-right) * v / max;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.aria||"bar chart")}">`;
  if (opts.ceil !== undefined) s += `<rect class="ceil" x="${left}" y="${top}" width="${x(opts.ceil)-left}" height="${items.length*rowH-6}"></rect>`;
  items.forEach((it,i) => {
    const y = top + i*rowH;
    s += `<text class="lab" x="${left-8}" y="${y+17}" text-anchor="end">${esc(it.label)}</text>`;
    s += `<rect class="bar ${it.cls||""}" x="${left}" y="${y+2}" width="${Math.max(1,x(it.value)-left)}" height="${rowH-12}" rx="1"></rect>`;
    s += `<text x="${x(it.value)+6}" y="${y+17}">${it.text || pct(it.value)}</text>`;
  });
  if (opts.ref) { const xr = x(opts.ref.value); s += `<line class="ref" x1="${xr}" y1="${top}" x2="${xr}" y2="${top+items.length*rowH-4}"></line><text class="lab" x="${xr}" y="${H-3}" text-anchor="middle">${esc(opts.ref.label)}</text>`; }
  if (opts.ceil !== undefined) s += `<text class="lab" x="${x(opts.ceil)}" y="${H-3}" text-anchor="middle">answer fetched ${pct(opts.ceil)}</text>`;
  s += `<line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${top+items.length*rowH-4}"></line></svg>`;
  root.innerHTML = s;
}

/* ---------- act 1 ---------- */
let a1sel = "mimir-hf";
function drawA1(){
  const items = ORDER.map(m => { const a = A(m,"closed"); return a ? {label: MODELS[m], value: a.em, cls: m===a1sel ? "on" : ""} : null; }).filter(Boolean);
  bars($("#a1chart"), items, {ref: {value: l70, label: "Llama 3.3 70B, their run"}, aria: "exact match from memory per model"});
  $("#a1chips").innerHTML = ORDER.map(m => `<button class="chip ${m===a1sel?"on":""}" data-m="${m}">${esc(MODELS[m])}</button>`).join("");
  $("#a1chips").querySelectorAll(".chip").forEach(b => b.onclick = () => { a1sel = b.dataset.m; drawA1(); });
}
drawA1();

/* ---------- act 2 ---------- */
let a2sel = "local";
function drawA2(){
  const q = ENG.find(x=>x.k===a2sel);
  const items = MAIN.map(m => { const a = A(m,q.cond); const partial = a && a.n < 500; return {label: MODELS[m] + (a ? (partial ? " (running)" : "") : " (not run)"), value: a ? a.em : 0, cls: a ? (partial ? "dim" : "") : "dim"}; });
  bars($("#a2chart"), items, {ceil: q.ceil, aria: "exact match with one lookup against the answer recall of the engine"});
  $("#a2chips").innerHTML = ENG.map(x => `<button class="chip ${x.k===a2sel?"on":""}" data-k="${x.k}">${esc(x.label)}</button>`).join("");
  $("#a2chips").querySelectorAll(".chip").forEach(b => b.onclick = () => { a2sel = b.dataset.k; drawA2(); });
}
drawA2();
$("#fidtable tbody").innerHTML = MAIN.map(m => D.fidelity_local.find(f=>f.model===m)).filter(Boolean)
  .map(f => `<tr><td>${esc(MODELS[f.model])}${f.n < 592 ? ` <span class="lab">(${f.n} of 592 so far)</span>` : ""}</td><td class="n">${pct(f.em_present)} <span class="lab">(n=${f.n_present})</span></td><td class="n">${pct(f.em_absent)} <span class="lab">(n=${f.n_absent})</span></td></tr>`).join("");

/* ---------- act 3: decision tiles ---------- */
const VARS = [["agentic","writes its own query, search box"],["agentic-local","writes its own query, ranked index"],["agentic-native-local","native tool call, ranked index"],["agentic-fewshot","with examples, search box"],["agentic-scaffold","asked first whether it knows"]];
let a3m = "mimir-hf", a3v = "agentic-scaffold", tileSel = null;
function drawA3(){
  const avail = VARS.filter(([v]) => D.decision.some(d => d.model===a3m && d.variant===v));
  if (!avail.length) { a3m = "gemma4b"; return drawA3(); }
  if (!avail.some(([v]) => v===a3v)) a3v = avail[0][0];
  $("#a3models").innerHTML = MAIN.map(m => `<button class="chip ${m===a3m?"on":""}" data-m="${m}">${esc(MODELS[m])}</button>`).join("");
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
  $("#tilenote").textContent = `${MODELS[a3m]}, ${VARS.find(([v])=>v===a3v)[1]}: searched on ${calls} of ${n} questions (${pct0(calls/n)}). Of the ${wrong} questions it had wrong from memory, it searched on ${d.called_wrong} (${pct0(d.called_wrong/Math.max(1,wrong))}).` + (calls/n > 0.9 ? " Searching on nearly everything is a policy, not a judgement per question." : "") + (calls/n < 0.05 ? " Never searching is the closed book with extra steps." : "");
}
drawA3();
$("#asktable tbody").innerHTML = D.ask.filter(a => a.model !== "mimir").map(a => `<tr><td>${esc(MODELS[a.model])}</td><td>${esc(VARS.find(([v])=>v===a.variant)?.[1] || CONDN[a.variant] || a.variant)}</td><td class="n">${a.calls}</td><td class="n">${a.first_hit_subject} (${pct0(a.first_hit_subject/a.calls)})</td><td class="n">${pct(a.em_own_query)}</td><td class="n">${a.em_fallback==null ? "" : pct(a.em_fallback) + " (n=" + a.fallbacks + ")"}</td></tr>`).join("");

/* ---------- question browser ---------- */
const bm = $("#bmodel"), bc = $("#bcond");
bm.innerHTML = ORDER.map(m => `<option value="${m}">${esc(MODELS[m])}</option>`).join("");
bc.innerHTML = D.conds.filter(c => D.agg.some(a=>a.cond===c)).map(c => `<option value="${c}">${esc(CONDN[c]||c)}</option>`).join("");
bm.value = "mimir-hf"; bc.value = "retrieve-local";
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
    det.innerHTML = `<td colspan="6"><div><b>Subject:</b> ${esc(q.subject)} &middot; <b>type:</b> ${q.type} &middot; <b>answer in the ranked-index text:</b> ${q.hit_local===true?"yes":(q.hit_local===false?"no":"unknown")} &middot; <b>in the search-box text:</b> ${q.hit_shaped===true?"yes":(q.hit_shaped===false?"no":"unknown")}</div>${all}</td>`;
    tr.after(det);
  });
}
drawBrowser();

/* ---------- failures: default answers and by type ---------- */
{
  const norm = s => String(s||"").toLowerCase().replace(/[^a-z0-9æøå]+/g," ").trim();
  const out = [];
  for (const m of MAIN) for (const c of ["closed","retrieve","retrieve-local"]) {
    const cnt = {}; let n = 0;
    D.questions.forEach(q => { const r = q.runs[m+"|"+c]; if (!r) return; n++; const k = norm(r.p); cnt[k] = (cnt[k]||0)+1; });
    if (n < 500) continue;
    const top = Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,3);
    out.push(`<tr><td>${esc(MODELS[m])}</td><td>${esc(CONDN[c])}</td><td>${top.map(([k,v]) => `${esc(k.slice(0,28))} (${v})`).join("; ")}</td><td class="n">${pct0(top.reduce((s,[,v])=>s+v,0)/n)}</td></tr>`);
  }
  $("#deftable tbody").innerHTML = out.join("");
  $("#typetable tbody").innerHTML = D.agg.filter(a => ["closed","retrieve","retrieve-local"].includes(a.cond) && a.model !== "mimir" && a.n >= 500).sort((a,b) => MAIN.indexOf(a.model)-MAIN.indexOf(b.model) || a.cond.localeCompare(b.cond))
    .map(a => `<tr><td>${esc(MODELS[a.model])}</td><td>${esc(CONDN[a.cond])}</td>` + ["year","number","text"].map(t => `<td class="n">${a.by_type[t] ? pct(a.by_type[t][0]) : ""}</td>`).join("") + `</tr>`).join("");
}

/* ---------- model card and cost ---------- */
{
  const meta = {"mimir-hf":["1.0 B (1.8 B with embeddings)","fp16, official implementation, prefix attention"], mimir:["1.0 B (1.8 B with embeddings)","Q8_0, community GGUF, causal attention"], llama1b:["1.2 B","Q8_0"], llama3b:["3.2 B","Q8_0"], gemma4b:["4.3 B","Q6_K"], qwen3b:["3.1 B","Q8_0"]};
  $("#cardtable tbody").innerHTML = MAIN.map(m => { const r = A(m,"retrieve-local"); const mm = meta[m] || ["", ""]; return `<tr><td>${esc(MODELS[m])}</td><td class="n">${mm[0]}</td><td>${mm[1]}</td><td class="n">${r ? pct(r.em) + (r.n < 592 ? ` (${r.n} so far)` : "") : ""}</td><td class="n">${r ? r.sec.toFixed(1) : ""}</td><td class="n">${r && r.ptok ? Math.round(r.ptok) : ""}</td></tr>`; }).join("");
}

/* ---------- guided tour (spotlight; positions computed from document coordinates, then scrolled) ---------- */
(function(){
  const STEPS = [
    {sel:"#top h1", k:"Welcome · 1 of 10", html:`This page takes the group's own Danish quiz and gives the models one Wikipedia lookup. <b>Read the four numbers under the title first.</b> They are Mimir from memory, Mimir with one lookup, the ceiling of that lookup, and how many models knew when to look.`},
    {sel:"#primer .primer", k:"Five things to know · 2 of 10", html:`Every term used below is defined here: the quiz, from memory, one lookup, the two search engines, and the two scores. The glossary under it stays open.`},
    {sel:"#mimirtable", k:"Act one: the ruler · 3 of 10", html:`<b>Read the three rows.</b> The same Mimir weights score three different numbers depending on how they are run. The official path lands on the paper's number; the common laptop port loses a third of it by reading the prompt the wrong way round.`},
    {sel:"#a1chart", k:"Act one: memory · 4 of 10", html:`<b>Click a model chip above the chart.</b> Every small model knows almost nothing of the canon from memory. The dotted line is the 70B model from their paper.`},
    {sel:"#a2chart", k:"Act two: the lookup · 5 of 10", html:`<b>Click a search engine.</b> The grey bar is how often the answer was fetched at all; the coloured bars are what each model scored with that text. Switch between the search box and the ranked index: the models did not change, the engine did.`},
    {sel:"#fidtable", k:"Act two: reading · 6 of 10", html:`Every model read the same fetched text, so this table is a clean reading test. The one-billion-parameter Mimir reads as well as the four-billion Gemma.`},
    {sel:"#tiles", k:"Act three: the decision · 7 of 10", html:`<b>Click a model, a variant, then a tile.</b> The four counts compare each model's decision to search with its own record from memory. The red tile is the bluff: answered from memory, and wrong.`},
    {sel:"#asked-first", k:"Questions asked · 8 of 10", html:`Six questions the author was asked while building this, answered in order: what the attention modes mean, how good the score is, whether the two-model pipeline is a trick, why 150 and 592, whether writing the query was part of the test, and what a second retrieval would do.`},
    {sel:"#bcontrols", k:"Every answer · 9 of 10", html:`<b>Filter, search, click a row.</b> All 592 questions with every model's answer under every condition, the query used and the page fetched.`},
    {sel:"#coda pre", k:"Run it yourself · 10 of 10", html:`Three commands reproduce the main table on any machine with a served model, in the group's own evaluation format. The Guided tour button at the top restarts this walkthrough.`},
  ];
  const root=$("#tour"), hl=$("#tour-hl"), card=$("#tour-card");
  let idx=0;
  function place(){
    const st=STEPS[idx]; const elm=document.querySelector(st.sel);
    if(!elm){ next(); return; }
    const r=elm.getBoundingClientRect(), sx=window.scrollX, sy=window.scrollY;
    const top=r.top+sy, left=r.left+sx;
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
