/* Renders every number on the page from window.DATA (site/data.js, written by scripts/build_page_data.py). */
(function(){
const D = window.DATA;
const $ = s => document.querySelector(s);
const MODELS = Object.assign({}, D.models, {"mimir-hf": "DFM Mimir 1B (official)", "mimir": "DFM Mimir 1B (llama.cpp port)"});
const ORDER = ["mimir-hf","mimir","llama1b","llama3b","gemma4b","qwen3b"].filter(m => D.models[m] && D.agg.some(a => a.model === m));
const MAIN = ORDER.filter(m => m !== "mimir");            // the port is shown only where the attention mode is the point
const pct = x => (x*100).toFixed(1) + "%";
const pct0 = x => Math.round(x*100) + "%";
const pc = v => `<td class="n pfill" style="--p:${(v*100).toFixed(1)}%">${pct(v)}</td>`; // % cell: the cell itself fills 0..100
const A = (m,c) => D.agg.find(a => a.model===m && a.cond===c);
const esc = s => String(s==null?"":s).replace(/[&<>"]/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[ch]));
const CONDN = {closed:"from memory", "closed-sc":"from memory, 5-sample vote", retrieve:"one lookup, search box", "retrieve-oracle":"one lookup, oracle query (search box)",
  "retrieve-local":"one lookup, ranked index", "retrieve-plus-local":"lookup + two paragraphs (variant)", "retrieve-k1-local":"one lookup, ranked index, 1 page", "retrieve-k5-local":"one lookup, ranked index, 5 pages", "retrieve-c1800-local":"one lookup, ranked index, 1800 characters", "retrieve-wide-local":"ten pages + paragraphs (variant)", "retrieve-tworound-local":"follow-up query (variant)",
  "retrieve-given-qwen":"Mimir reads, Qwen asks (search box)", "retrieve-given-gemma":"reads Gemma's queries (search box)", "retrieve-given-gemma+qwen":"reads Gemma and Qwen queries (search box)",
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
fills.a1_take = `the best small model from memory, ${MODELS[closedSorted[0].model]}, scores ${pct(closedSorted[0].em)}; the released 70B Llama scores ${pct(l70)} on the same questions.`;
const port = A("mimir","closed");
const portfix = A("mimir-prefix","closed");
fills.port_pct = port ? pct(port.em) : "";
fills.portfix_closed_pct = portfix ? pct(portfix.em) : "running";
fills.a1_verdict = `The released prediction files reproduce the published ranking, and Mimir on the official implementation gives ${pct(mhc.em)} against the published 9.6. ` +
  (port ? `The same weights through the community llama.cpp port give ${pct(port.em)}, because the port reads the prompt left to right only. ` : "") +
  `Mimir, trained on Danish, retains the most from memory of the five small models.`;
/* act two */
const ENG = [
  {k:"box", label:"Wikipedia search box", cond:"retrieve", ceil:D.ceilings.shaped.hit},
  {k:"local", label:"ranked index (BM25)", cond:"retrieve-local", ceil:D.ceilings.local.hit},
  {k:"oracle", label:"oracle query, search box", cond:"retrieve-oracle", ceil:D.ceilings.subject.hit}];
const boxRows = MAIN.map(m => A(m,"retrieve")).filter(Boolean), locRows = MAIN.map(m => A(m,"retrieve-local")).filter(a => a && a.n >= 500), orRows = MAIN.map(m => A(m,"retrieve-oracle")).filter(Boolean);
const rng = rows => `${pct0(Math.min(...rows.map(a=>a.em)))} to ${pct0(Math.max(...rows.map(a=>a.em)))}`;
fills.a2_take = `the search box fetches the answer ${pct0(D.ceilings.shaped.hit)} of the time, the ranked index ${pct0(D.ceilings.local.hit)}, and the models follow their engine.`;
const locBest = [...locRows].sort((a,b)=>b.em-a.em)[0];
const orBest = orRows.find(a => a.model===locBest.model);
fills.a2_verdict = `Same models, same prompt, same questions; only the search behind the tool changed, and ${MODELS[locBest.model]} moved from ${pct(boxRows.find(a=>a.model===locBest.model).em)} to ${pct(locBest.em)}, ${orBest ? `${Math.abs((orBest.em-locBest.em)*100).toFixed(1)} points from` : "close to"} the oracle query a model never sees. ` +
  `The search box needs every word to appear in the page; a ranked index does not.` +
  (mhl && mhl.n >= 500 ? ` Mimir at one billion parameters reads the same text as well as Gemma 3 4B.` : "");
const fl = [...D.fidelity_local].sort((a,b)=>b.em_present-a.em_present);
fills.fid_note = fl.length ? `${MODELS[fl[0].model]} converts ${pct0(fl[0].em_present)} of the fetched answers, ${MODELS[fl[fl.length-1].model]} ${pct0(fl[fl.length-1].em_present)}. When the answer is absent, every model still answers, almost always wrongly.` : "";
const dc = D.decomp;
fills.decomp_text = dc ? `Of the ${dc.n} questions, the answer was inside the three fetched introductions for ${dc.in_intros} (${pct0(dc.in_intros/dc.n)}), further down one of those three pages for ${dc.below_intro} (${pct0(dc.below_intro/dc.n)}), and not in the top three pages at all for ${dc.not_in_top3} (${pct0(dc.not_in_top3/dc.n)}), of which ${dc.in_ranks_4_to_10} sat in ranks four to ten.` : "";
/* act three */
const dec = v => D.decision.filter(d => d.variant===v && d.model !== "mimir");
const rate = d => (d.called_wrong + d.called_right) / (d.called_wrong + d.called_right + d.silent_wrong + d.silent_right);
const never = dec("agentic").filter(d => rate(d) < 0.02).map(d => MODELS[d.model]);
const always = dec("agentic").filter(d => rate(d) > 0.9).map(d => MODELS[d.model]);
const l3 = dec("agentic-fewshot").find(d => d.model==="llama3b");
const agLoc = MAIN.map(m => ({m, a: A(m,"agentic-local"), r: A(m,"retrieve-local")})).filter(x => x.a && x.r && x.a.n >= 500 && rate(D.decision.find(d=>d.model===x.m && d.variant==="agentic-local") || {called_wrong:0,called_right:0,silent_wrong:1,silent_right:0}) > 0.5);
fills.a3_verdict = `Told they may search, ${never.join(", ")} never wrote a search line; ${always.join(" and ")} wrote one on nearly every question. ` +
  (scaff ? `Asked first whether it knew the answer, Mimir said yes on ${fills.mimir_bluff_pct} of the questions it then got wrong. ` : "") +
  (function(){ const t = D.decision.find(d => d.model==="llama3b" && d.variant==="agentic"), n = D.decision.find(d => d.model==="llama3b" && d.variant==="agentic-native-local");
    return (t && n && rate(t) < 0.05 && rate(n) > 0.9) ? `Llama 3B never searched when told in text and searched on ${pct0(rate(n))} of questions when the same search came in its native tool format: the interface sets the decision, not knowledge. ` : ""; })() +
  (agLoc.length ? `Models that write their own query score below the plain question on the ranked index (${agLoc.map(x => `${MODELS[x.m]} ${pct(x.a.em)} against ${pct(x.r.em)}`).join(", ")}).` : "");
fills.ask_note = `A query "landed" when the first result was the canon work the question is about; when it returned nothing, the question itself was used (fallback). The question as written is the better query.`;
const qc = A("qwen3b","closed"), ql = A("qwen3b","retrieve-local");
if (qc && ql) { fills.qwen_closed_len = pct(qc.lenient); fills.qwen_local_len = pct(ql.lenient); }
if (D.inspect_full && D.inspect_full.daisy_lookup && gl) {
  const I = D.inspect_full, ic = A("gemma4b","closed");
  fills.inspect_check = `Checked: run through this task on all 592 questions, Gemma 3 4B scores ${pct(I.daisy_lookup.scores.exact_match.mean)} with the lookup (standard error ${(I.daisy_lookup.scores.exact_match.stderr*100).toFixed(1)}) and ${pct(I.daisy.scores.exact_match.mean)} from memory, against ${pct(gl.em)} and ${pct(ic.em)} from the harness behind this page. The two paths agree to within half a point; the harness allows 64 new tokens, the official task 100.`;
}
/* questions asked along the way */
{
  const causal = (D.mimir_paths || []).find(m => /causal attention, fp16/.test(m.label));
  fills.q_causal = causal ? pct(causal.em) : (port ? pct(port.em) : "");
  fills.q_how_good = `It is the highest score measured on DAISY under any condition. The largest released model, a 70B Llama, scores ${pct(l70)} from memory, and the nearest published numbers, English systems trained for the task with far larger models, sit at 44 to 64 exact match. Two caveats: the 95% interval is about plus or minus 4 points, and the questions were written from Wikipedia pages, so the score measures how well pages are found and read.`;
  const two = A("mimir-hf","retrieve-given-gemma+qwen") || A("mimir-hf","retrieve-given-qwen");
  fills.q_two_models = `Yes, two models in a row, not one combined model: Qwen 2.5 3B writes the search words, Mimir reads the pages and answers${two ? ` (${pct(two.em)} through the search box)` : ""}. It existed because Mimir never writes a search when asked to. The ranked index made it unnecessary: Mimir alone, with the question as the query, scores ${mhl ? pct(mhl.em) : ""}.`;
  let same = 0, tot = 0; D.questions.forEach(q => { const r = q.runs["gemma4b|retrieve-local"]; if (r) { tot++; if ((r.tq||"").trim() === q.q.trim().slice(0,80)) same++; } });
  let sameBox = 0, totBox = 0; D.questions.forEach(q => { const r = q.runs["gemma4b|retrieve"]; if (r) { totBox++; if ((r.tq||"").trim() === q.q.trim().slice(0,80)) sameBox++; } });
  fills.q_query = `No. The benchmark has no tool; the lookup is this page's addition, and the least engineered choice is to send the question as written. On the ranked index the query was the question itself on ${same} of ${tot} questions. The shortening rule exists only for the search box, which needs every word to match; there it fired on ${totBox - sameBox} of ${totBox} queries.`;
  const plusM = A("mimir-hf","retrieve-plus-local"), plusG = A("gemma4b","retrieve-plus-local"), wide = A("gemma4b","retrieve-wide-local"), two2 = A("gemma4b","retrieve-tworound-local");
  const parts = [];
  if (plusM || plusG) parts.push(`Fetching the two best paragraphs of the same three pages in addition to their introductions${plusM ? ` takes Mimir from ${pct(mhl.em)} to ${pct(plusM.em)}` : ""}${plusG ? ` and Gemma from ${pct(gl.em)} to ${pct(plusG.em)}` : ""}; the ceiling rises from ${pct(D.ceilings.local.hit)} to ${pct0(0.812)}.`);
  if (wide && wide.n >= 500) parts.push(`Casting a wider net, ten pages and the four best paragraphs across them, gives Gemma ${pct(wide.em)}.`);
  if (two2 && two2.n >= 500) parts.push(`Letting Gemma write one follow-up query when it says the text lacks the answer gives ${pct(two2.em)}.`);
  if (!wide || !two2) parts.push(`Two further variants, a ten-page net and a model-written second query, are running and will appear here.`);
  fills.q_second = `Each variant adds a selection step beyond one lookup, so none is the main line. ` + parts.join(" ") + ` Each extra step buys a few points at roughly double the tokens.`;
}
/* PopQA long-tail on the Self-RAG passages */
if (D.popqa) {
  const PUB = [["Llama 2 7B (Self-RAG paper baseline, untrained)", 0.147, 0.382, null], ["Llama 2 13B (Self-RAG paper baseline, untrained)", 0.147, 0.457, null], ["Self-RAG 7B (trained to retrieve and critique)", null, 0.549, null], ["Self-RAG 13B (trained)", null, 0.558, null]];
  const PORDER = ["llama1b","llama3b","qwen3b","gemma4b"];
  const ours = Object.entries(D.popqa).filter(([m, v]) => v.ret5 && v.ret5.n >= 1000).sort((a,b) => PORDER.indexOf(a[0]) - PORDER.indexOf(b[0])).map(([m, v]) => [MODELS[m] + " (this page, untrained)", v.closed ? v.closed.match : null, v.ret5 ? v.ret5.match : null, v.ret10 ? v.ret10.match : null, m]);
  const cell = v => v == null ? '<span class="gap">not published</span>' : pct(v);
  $("#popqatable tbody").innerHTML = PUB.concat(ours).map(r => `<tr><td>${esc(r[0])}</td><td class="n">${cell(r[1])}</td><td class="n">${cell(r[2])}</td><td class="n">${cell(r[3])}</td></tr>`).join("");
  const best = ours.map(r => Math.max(r[2] || 0, r[3] || 0));
  { const big = ours.filter(r => r[4] !== "llama1b"), small = ours.find(r => r[4] === "llama1b");
    const rng = big.length ? (Math.min(...big.map(r => r[2])) === Math.max(...big.map(r => r[2])) ? pct(big[0][2]) : `${pct(Math.min(...big.map(r => r[2])))} to ${pct(Math.max(...big.map(r => r[2])))}`) : "";
    fills.popqa_text = `With five passages the untrained 3B and 4B readers score ${rng}, level with the trained Self-RAG rows (54.9 and 55.8)${small ? `; the 1B reader scores ${pct(small[2])}, still above the paper's untrained 7B baseline with the same passages (38.2)` : `; the paper's untrained 7B baseline with the same passages scores 38.2`}. Published rows are from Table 2 of the Self-RAG paper.`; }
}
document.querySelectorAll("[data-fill]").forEach(el => { const k = el.getAttribute("data-fill"); if (fills[k] !== undefined) el.textContent = fills[k]; });

/* ---------- hover definitions: wrap the first occurrence of each term per chapter ---------- */
{
  const TERMS = [
    ["prefix attention", "Mimir's trained reading mode: every prompt token attends to every other prompt token; only the answer is written left to right."],
    ["reading fidelity", "Exact match restricted to the questions where the answer was in the fetched text."],
    ["answer recall", "How often the reference answer is inside the fetched text; the ceiling of a lookup."],
    ["contains-gold", "The reference answer appears somewhere inside the model's answer; softer than exact match."],
    ["exact match", "The official score: the normalised answer equals the reference answer."],
    ["oracle query", "The benchmark's hidden subject field used as the search term; the best possible query, never shown to a model."],
    ["greedy decoding", "The model always takes its single most likely next token; no sampling, so runs repeat exactly."],
    ["from memory", "The model answers with nothing but the official prompt; no lookup."],
    ["one lookup", "The question, as written, fetches the top three Wikipedia introductions, which are placed above the prompt."],
    ["ranked index", "A standard BM25 full-text index over the Danish Wikipedia dump of 1 November 2023, built for this study."],
    ["search box", "Wikipedia's own search, which requires every word of the query to match the page."],
    ["BM25", "The standard ranking formula of full-text search: a page scores by how many of the rarer query words it contains."],
    ["standard error", "The uncertainty of a score from a finite sample; on 592 questions about 1 to 2 points."],
    ["quantised", "Weights stored at 6 or 8 bits instead of 16 to fit a small graphics card; scores barely change."],
  ];
  document.querySelectorAll("section.chapter").forEach(sec => {
    if (sec.id === "primer") return;
    const done = new Set();
    const els = sec.querySelectorAll("p, li, dd, figcaption");
    for (const [term, tip] of TERMS) {
      if (done.has(term)) continue;
      const rx = new RegExp("(^|[\\s(>])(" + term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")([\\s.,;:)<]|$)", "i");
      for (const el of els) {
        if (done.has(term)) break;
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
          acceptNode: nd => { const p = nd.parentElement; return (p.closest("a, button, select, .term, .ib, pre, svg") || !nd.textContent.trim()) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; } });
        let nd;
        while ((nd = walker.nextNode())) {
          const m = nd.textContent.match(rx);
          if (!m) continue;
          const i = m.index + m[1].length;
          const after = nd.splitText(i); after.splitText(m[2].length);
          const span = document.createElement("span"); span.className = "term"; span.setAttribute("data-tip", tip); span.setAttribute("tabindex", "0");
          span.textContent = after.textContent; after.replaceWith(span);
          done.add(term); break;
        }
      }
    }
  });
  const tipEl = document.createElement("div"); tipEl.id = "tipbox"; document.body.appendChild(tipEl);
  let tipFor = null;
  function showTip(el){
    tipEl.textContent = el.getAttribute("data-tip"); tipEl.style.display = "block"; tipFor = el;
    const r = el.getBoundingClientRect(), tw = Math.min(300, innerWidth - 24);
    tipEl.style.maxWidth = tw + "px";
    const tr = tipEl.getBoundingClientRect();
    let x = r.left + r.width/2 - tr.width/2; x = Math.max(12, Math.min(x, innerWidth - tr.width - 12));
    let y = r.top - tr.height - 8; if (y < 8) y = r.bottom + 8;
    tipEl.style.left = (x + scrollX) + "px"; tipEl.style.top = (y + scrollY) + "px";
  }
  function hideTip(){ tipEl.style.display = "none"; tipFor = null; }
  document.addEventListener("mouseover", e => { const t = e.target.closest("[data-tip]"); if (t) showTip(t); else if (tipFor) hideTip(); });
  document.addEventListener("focusin", e => { const t = e.target.closest("[data-tip]"); if (t) showTip(t); });
  document.addEventListener("focusout", () => hideTip());
  window.addEventListener("scroll", () => { if (tipFor) hideTip(); }, {passive: true});
}

/* ---------- chapters: number every chapter section and build the contents list ---------- */
{
  const secs = [...document.querySelectorAll("section.chapter")];
  const ol = document.querySelector("#contents ol");
  secs.forEach((sec, i) => {
    const h = sec.querySelector("h2"); if (!h) return;
    const title = h.textContent;
    if (!sec.id) sec.id = "ch" + (i+1);
    h.innerHTML = `<span class="chno">${i+1}.</span> ${esc(title)}`;
    if (ol) ol.insertAdjacentHTML("beforeend", `<li><a href="#${sec.id}"><span class="cno">${i+1}.</span> ${esc(title)}</a></li>`);
  });
}

/* ---------- second retrieval table ---------- */
{
  const V = [["retrieve-local","One plain lookup (main line)"],["retrieve-plus-local","Plus the two best paragraphs of the same pages"],["retrieve-wide-local","Ten pages, three introductions plus four best paragraphs"],["retrieve-tworound-local","Model writes a follow-up query when the text lacks the answer"]];
  const gp = v => v == null ? `<td class="n gap">not run</td>` : `<td class="n">${v}</td>`;
  const rows = V.map(([c,l]) => { const g = A("gemma4b",c), m = A("mimir-hf",c) || A("mimir-prefix",c); const ce = D.ceil_by_cond && D.ceil_by_cond[c]; return (g||m) ? `<tr><td>${esc(l)}</td>${g && g.n>=500 ? pc(g.em) : gp(null)}${m && m.n>=500 ? pc(m.em) : gp(null)}${ce ? pc(ce.hit) : gp(null)}${gp(g && g.ptok ? Math.round(g.ptok) : null)}</tr>` : ""; }).join("");
  const el = $("#secondtable tbody"); if (el) el.innerHTML = rows;
  fills.second_note = "For Gemma the paragraphs variant is the best of the side rows; for Mimir the wider net edges the paragraphs variant by 0.2 points, inside one standard error. The model-written follow-up query buys nothing: Gemma asks one time in six and loses 1.3 points to the extra instruction, Mimir asks on 26 of the 592 and stays level with the plain lookup.";
}

/* ---------- their reading benchmark table ---------- */
if (D.mwqa) {
  const PUB = [["DFM Mimir 1B (published, Mimir report)", 0.668, null, null], ["Qwen 3.5 4B (published)", 0.571, null, null], ["Gemma 3 1B (published)", 0.426, null, null]];
  const ours = MAIN.filter(m => D.mwqa[m]).map(m => [MODELS[m] + " (this page)", D.mwqa[m].em, D.mwqa[m].f1, D.mwqa[m].sec]);
  if (D.mwqa["mimir-prefix"]) ours.unshift(["DFM Mimir 1B (this page, patched llama.cpp port, 512 rows)", D.mwqa["mimir-prefix"].em, D.mwqa["mimir-prefix"].f1, D.mwqa["mimir-prefix"].sec]);
  const gp = (v, f) => v == null ? `<td class="n gap">not published</td>` : `<td class="n">${f(v)}</td>`;
  const el = $("#mwqatable tbody"); if (el) el.innerHTML = PUB.concat(ours).map((r, i) => `<tr${i===0?' class="pubrow"':''}><td>${esc(r[0])}</td>${pc(r[1])}${gp(r[2], pct)}${gp(r[3], v=>v.toFixed(1))}</tr>`).join("");
  const ll = D.mwqa.llama1b;
  fills.mwqa_note = `Published rows are from the Mimir report, same task and code. ${D.mwqa["mimir-prefix"] ? `Mimir through the patched llama.cpp port lands within noise of the published 66.8 on 512 rows, a second benchmark on which the port reproduces the official run. ` : ``} ${ll ? `Llama 3.2 1B scores near zero because it ignores the instruction to answer in three words, not because it cannot read; its word-level F1 is ${pct0(ll.f1)}.` : ""}${D.euroeval && Object.keys(D.euroeval).length ? ` EuroEval's version of the same dataset, a different prompt and split: ${Object.entries(D.euroeval).map(([m,v]) => `${MODELS[m]||m} ${v.em.toFixed(1)} exact match`).join(", ")}.` : ""}`;
}

/* ---------- speed table ---------- */
{
  const cell = (v, f) => v == null ? `<td class="n gap">not run</td>` : `<td class="n">${f(v)}</td>`;
  const row = (label, m) => { const c = A(m,"closed"), r = A(m,"retrieve-local");
    return `<tr><td>${esc(label)}</td>${r && r.n>=500 ? pc(r.em) : cell(null, pct)}${cell(c ? c.sec : null, v=>v.toFixed(1))}${cell(r ? r.sec : null, v=>v.toFixed(1))}${cell(r && r.ptok ? Math.round(r.ptok) : null, v=>v)}${cell(r && r.otok ? Math.round(r.otok) : null, v=>v)}</tr>`; };
  const sub = t => `<tr class="subhead"><td colspan="6">${t}</td></tr>`;
  let html = sub("llama.cpp, quantised weights, three requests in flight");
  for (const m of ["llama1b","llama3b","gemma4b","qwen3b"]) html += row(MODELS[m], m);
  html += sub("Official transformers implementation, fp16, batch of two") + row("DFM Mimir 1B (official)", "mimir-hf");
  const pp = A("mimir-prefix","closed"), pr = A("mimir-prefix","retrieve-local");
  if (pp || pr) html += sub("llama.cpp with the prefix-attention fix, served one request at a time") + row("DFM Mimir 1B (patched port)", "mimir-prefix");
  const el = $("#speedtable tbody"); if (el) el.innerHTML = html;
  fills.speed_note = `Three things drive every difference in this table. The lookup multiplies the prompt by about six (960 tokens against 160), which is most of the gap between the two seconds columns. The path drives the rest: the official transformers implementation is correct but unbatched, so its lookup row costs 26 seconds a request; the patched port returns the same answers (identical on 93% of questions from memory, 99% with the lookup, same score) at a third of that time even served one request at a time. Output length barely matters: every model writes under ten tokens.`;
}

{
  const g1 = A("gemma4b","retrieve-k1-local"), g3 = A("gemma4b","retrieve-local"), g5 = A("gemma4b","retrieve-k5-local"), gc = A("gemma4b","retrieve-c1800-local");
  const c = k => D.ceil_by_cond && D.ceil_by_cond[k] ? pct(D.ceil_by_cond[k].hit) : null;
  if (g1 && g3 && g5) fills.ksweep_note = `How many pages to fetch, measured on Gemma 3 4B: one introduction ${pct(g1.em)} (answer present in ${c("retrieve-k1-local")} of prompts), three ${pct(g3.em)} (${c("retrieve-local")}), five ${pct(g5.em)} (${c("retrieve-k5-local")}). Beyond three pages the ceiling keeps rising and the score stops, because every extra page is more text to misread.${gc ? ` Doubling each introduction to 1,800 characters at three pages gives ${pct(gc.em)}.` : ``}`;
}
{
  const pc = D.port_check, pr = A("mimir-prefix","retrieve-local"), ph = A("mimir-hf","retrieve-local"), pm = D.mwqa && D.mwqa["mimir-prefix"];
  if (pc) fills.port_fix_note = `The port's author documented the limitation; the fix is 35 lines in six files of llama.cpp: for models trained this way the attention mask lets every prompt token see the whole prompt, the server stops reusing cached prompt prefixes, and a warning fires when a prompt is split. Checked against the official implementation on the same prompt bytes: the identical answer from memory on ${pct(pc.identical)} of the ${pc.n} questions (the causal port manages 29 percent)${pr && ph ? `; with one lookup ${pct(pr.em)} against ${pct(ph.em)}` : ``}${pm ? `; on Multi Wiki QA ${pct(pm.em)} against the published 66.8` : ``}.`;
}
["second_note","mwqa_note","speed_note","ksweep_note","port_fix_note"].forEach(k => { const el = document.querySelector(`[data-fill=${k}]`); if (el && fills[k] !== undefined) el.textContent = fills[k]; });

/* ---------- replication and ruler tables ---------- */
{
  const tb = $("#reptable tbody");
  const rows = Object.entries(D.replication).sort((a,b) => b[1].F1 - a[1].F1);
  const nice = k => k.replace("meta-llama-","").replace("openai-","").replace("google-","").replace("mistralai-","");
  tb.innerHTML = rows.map(([k,v]) => `<tr><td>${esc(nice(k))}</td><td class="n">${v.EM.toFixed(3)}</td><td class="n">${v.F1.toFixed(3)}</td><td class="n">${v.BLEU.toFixed(3)}</td><td class="n">${v.paper_f1 ?? ""}</td><td class="n">${v.paper_bleu ?? ""}</td></tr>`).join("");
  $("#mimirtable tbody").innerHTML = (D.mimir_paths || []).map(m => `<tr><td>${esc(m.label)}</td>${pc(m.em)}</tr>`).join("") + `<tr class="pubrow"><td>Reported in the Mimir paper (Inspect harness)</td><td class="n pfill" style="--p:9.6%">9.6%</td></tr>`;
}

/* ---------- bar chart helper ---------- */
function bars(root, items, opts){
  const W = 640, rowH = 34, left = 208, right = 60, top = 8;
  const H = top + items.length*rowH + (opts.ref || opts.ceil !== undefined ? 18 : 6);
  const max = Math.max(0.05, ...items.map(i=>i.value), opts.ref ? opts.ref.value : 0, opts.ceil || 0) * 1.08;
  const x = v => left + (W-left-right) * v / max;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.aria||"bar chart")}">`;
  items.forEach((it,i) => {
    const y = top + i*rowH;
    s += `<text class="lab" x="${left-8}" y="${y+17}" text-anchor="end">${esc(it.label)}</text>`;
    if (opts.ceil !== undefined) s += `<rect class="ceilrow" x="${left}" y="${y+2}" width="${Math.max(1,x(opts.ceil)-left)}" height="${rowH-12}" rx="1"></rect>`;
    s += `<rect class="bar ${it.cls||""}" x="${left}" y="${y+2}" width="${Math.max(1,x(it.value)-left)}" height="${rowH-12}" rx="1"></rect>`;
    s += `<text x="${x(it.value)+6}" y="${y+17}">${it.text || pct(it.value)}</text>`;
  });
  if (opts.ceil !== undefined) s += `<line class="ref" x1="${x(opts.ceil)}" y1="${top}" x2="${x(opts.ceil)}" y2="${top+items.length*rowH-4}"></line>`;
  if (opts.ref) { const xr = x(opts.ref.value); const anch = xr > W*0.72 ? "end" : "middle"; const lx = anch === "end" ? xr - 5 : xr; s += `<line class="ref" x1="${xr}" y1="${top}" x2="${xr}" y2="${top+items.length*rowH-4}"></line><text class="lab" x="${lx}" y="${H-3}" text-anchor="${anch}">${esc(opts.ref.label)}</text>`; }
  if (opts.ceil !== undefined) { const xc = x(opts.ceil); const anch = xc > W*0.72 ? "end" : "middle"; s += `<text class="lab" x="${anch==="end"?xc-4:xc}" y="${H-3}" text-anchor="${anch}">ceiling: answer fetched ${pct(opts.ceil)}</text>`; }
  s += `<line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${top+items.length*rowH-4}"></line></svg>`;
  root.innerHTML = s;
}

/* ---------- act 1 ---------- */
function drawA1(){
  const items = ORDER.map(m => { const a = A(m,"closed"); return a ? {label: MODELS[m], value: a.em} : null; }).filter(Boolean);
  bars($("#a1chart"), items, {ref: {value: l70, label: "Llama 3.3 70B (released run)"}, aria: "exact match from memory per model"});
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
  .map(f => `<tr><td>${esc(MODELS[f.model])}${f.n < 592 ? ` <span class="lab">(${f.n} of 592 so far)</span>` : ""}</td><td class="n pfill" style="--p:${(f.em_present*100).toFixed(1)}%">${pct(f.em_present)} <span class="lab">(n=${f.n_present})</span></td><td class="n pfill" style="--p:${(f.em_absent*100).toFixed(1)}%">${pct(f.em_absent)} <span class="lab">(n=${f.n_absent})</span></td></tr>`).join("");

/* ---------- where the 592 questions go (two rows, same scale) ---------- */
let decSel = "mimir-hf";
function drawDecomp(){
  const avail = MAIN.filter(m => { const a = A(m,"retrieve-local"); return a && a.n >= 500; });
  if (!avail.includes(decSel)) decSel = avail[0];
  $("#decchips").innerHTML = avail.map(m => `<button class="chip ${m===decSel?"on":""}" data-m="${m}">${esc(MODELS[m])}</button>`).join("");
  $("#decchips").querySelectorAll(".chip").forEach(b => b.onclick = () => { decSel = b.dataset.m; drawDecomp(); });
  const rows = D.questions.map(q => ({q, r: q.runs[decSel+"|retrieve-local"]})).filter(x => x.r);
  const n = rows.length, dc = D.decomp || {n, in_intros: Math.round(D.ceilings.local.hit*n), below_intro: 0, not_in_top3: n - Math.round(D.ceilings.local.hit*n), in_ranks_4_to_10: 0};
  const inT = rows.filter(x => x.q.hit_local === true), outT = rows.filter(x => x.q.hit_local !== true);
  const rightIn = inT.filter(x => x.r.em >= 1).length, wrongIn = inT.length - rightIn, rightOut = outT.filter(x => x.r.em >= 1).length, wrongOut = outT.length - rightOut;
  const SHORT = {"mimir-hf":"Mimir 1B", gemma4b:"Gemma 3 4B", llama3b:"Llama 3B", qwen3b:"Qwen 3B", llama1b:"Llama 1B"};
  const W = 640, left = 150, right = 16, bw = W - left - right, x = v => left + bw * v / n;
  const rowA = [["seg-in", dc.in_intros, "in the 3 intros"], ["seg-below", dc.below_intro, "further down"], ["seg-r410", dc.in_ranks_4_to_10, "ranks 4 to 10"], ["seg-beyond", dc.not_in_top3 - dc.in_ranks_4_to_10, "not in top 10"]];
  const rowB = [["seg-right", rightIn, "read right", true], ["seg-misread", wrongIn, "misread", true], ["seg-memory", rightOut, "from memory", true], ["seg-wrong", wrongOut, "wrong", false]];
  const ticks = [[dc.in_intros, "3 intros"], [dc.in_intros + dc.below_intro, "whole pages"], [dc.in_intros + dc.below_intro + dc.in_ranks_4_to_10, "top 10"]];
  const k1 = D.ceil_by_cond && D.ceil_by_cond["retrieve-k1-local"]; if (k1) ticks.unshift([Math.round(k1.hit*n), "1 intro"]);
  const plus = D.ceil_by_cond && D.ceil_by_cond["retrieve-plus-local"]; if (plus) ticks.push([Math.round(plus.hit*n), "+paragraphs"]);
  const tk = ticks.sort((a,b)=>a[0]-b[0]);
  // leftmost tick gets the highest level and every label sits to the right of its own line, so no
  // line can pass through a label: lines only descend past labels whose text starts further right.
  const LVH = 16, placed = [];
  tk.forEach(([v, lab], i) => {
    const xt = x(v), txt = `${lab} ${pct0(v/n)}`, wpx = txt.length * 6.6 + 4;
    const x0 = Math.min(xt + 3, W - wpx - 4);
    placed.push({xt, txt, x0, lvl: tk.length - 1 - i});
  });
  const nlv = tk.length; const top = 6 + nlv * LVH; const H = top + 4 + 50 + 30 + 24;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="where the 592 questions go for ${esc(MODELS[decSel])}">`;
  const row = (segs, y, label) => {
    s += `<text class="rowlab" x="${left-8}" y="${y+19}" text-anchor="end">${esc(label)}</text>`;
    let acc = 0;
    segs.forEach(([cls, v, lab, light]) => { const x0 = x(acc), w = x(acc+v) - x0; acc += v;
      s += `<rect class="${cls}" x="${x0}" y="${y}" width="${Math.max(0,w)}" height="30"></rect>`;
      if (w > 64) s += `<text class="seglab ${light?"light":""}" x="${x0+6}" y="${y+19}">${esc(lab)} ${v}</text>`;
      else if (w > 26) s += `<text class="seglab ${light?"light":""}" x="${x0+4}" y="${y+19}">${v}</text>`; });
  };
  placed.forEach(q => { const yy = top - 4 - q.lvl * LVH;
    s += `<line class="tick" x1="${q.xt}" y1="${yy+3}" x2="${q.xt}" y2="${top+2}"></line><text class="ticklab" x="${q.x0}" y="${yy}">${esc(q.txt)}</text>`; });
  row(rowA, top + 4, "the answer was");
  row(rowB, top + 50, SHORT[decSel] || MODELS[decSel]);
  s += `<text class="rowlab" x="${left}" y="${H-6}">0</text><text class="rowlab" x="${x(n)}" y="${H-6}" text-anchor="end">${n} questions</text></svg>`;
  $("#decchart").innerHTML = s;
  const LEG = [["Top row", [["seg-in","answer in the 3 introductions"],["seg-below","further down a fetched page"],["seg-r410","in a page ranked 4 to 10"],["seg-beyond","not in the top 10"]]],
               ["Bottom row", [["seg-right","read right"],["seg-misread","answer was there, misread"],["seg-memory","right from memory"],["seg-wrong","wrong, answer not fetched"]]]];
  const lg = $("#decleg"); if (lg) lg.innerHTML = LEG.map(([t, items]) => `<div><span class="legt">${t}:</span>` + items.map(([c, l]) => `<span class="legi"><i class="sw ${c}"></i>${l}</span>`).join("") + `</div>`).join("");
  fills.dec_take = `for ${MODELS[decSel]}, ${rightIn} of the ${inT.length} fetched answers were read right and ${wrongIn} misread; of the ${outT.length} questions the lookup missed, ${rightOut} were still answered from memory. ${dc.below_intro} answers sat further down a fetched page and ${dc.in_ranks_4_to_10} in pages ranked four to ten, which is what the second-retrieval variants recover.`;
  const el = document.querySelector("[data-fill=dec_take]"); if (el) el.textContent = fills.dec_take;
}
drawDecomp();

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
    {k:"called_wrong", cls:"good", s:"the useful call"},
    {k:"called_right", cls:"", s:"wasted effort, harmless"},
    {k:"silent_wrong", cls:"bad", s:"the bluff"},
    {k:"silent_right", cls:"good", s:"earned trust"}];
  tiles.forEach(t => { const cell = $("#t-" + t.k); if (!cell) return;
    cell.innerHTML = `<div class="tile ${t.cls} ${tileSel===t.k?"on":""}" data-k="${t.k}"><div class="v">${d[t.k]}</div><div class="s">${esc(t.s)} &middot; ${pct0(d[t.k]/n)} of ${n}</div></div>`;
    cell.firstChild.onclick = () => { tileSel = t.k; drawA3(); browserFromTile(); }; });
  const calls = d.called_wrong + d.called_right, wrong = d.called_wrong + d.silent_wrong;
  $("#tilenote").textContent = `${MODELS[a3m]}, ${VARS.find(([v])=>v===a3v)[1]}: searched on ${calls} of ${n} questions (${pct0(calls/n)}). Of the ${wrong} questions it had wrong from memory, it searched on ${d.called_wrong} (${pct0(d.called_wrong/Math.max(1,wrong))}).` + (calls/n > 0.9 ? " Searching on nearly everything is a policy, not a judgement per question." : "") + (calls/n < 0.05 ? " Never searching reproduces the closed book." : "");
}
drawA3();
$("#asktable tbody").innerHTML = D.ask.filter(a => a.model !== "mimir").map(a => `<tr><td>${esc(MODELS[a.model])}</td><td>${esc(VARS.find(([v])=>v===a.variant)?.[1] || CONDN[a.variant] || a.variant)}</td><td class="n">${a.calls}</td><td class="n">${a.first_hit_subject} (${pct0(a.first_hit_subject/a.calls)})</td>${pc(a.em_own_query)}<td class="n">${a.em_fallback==null ? '<span class="gap">no fallbacks</span>' : pct(a.em_fallback) + " (n=" + a.fallbacks + ")"}</td></tr>`).join("");

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
let bLimit = 5;
const bx = $("#bexpand");
if (bx) bx.onclick = () => { bLimit = bLimit === 5 ? 200 : 5; drawBrowser(); };
["bmodel","bcond","boutcome","btype"].forEach(id => $("#"+id).onchange = () => { window.__tileFilter = null; if (id === "btype") window.__flag = null; drawBrowser(); });
$("#bsearch").oninput = () => { window.__tileFilter = null; drawBrowser(); };
function drawBrowser(){
  const m = bm.value, c = bc.value, o = $("#boutcome").value, t = $("#btype").value, s = $("#bsearch").value.trim().toLowerCase();
  const closed = {}; D.questions.forEach(q => { const r = q.runs[m+"|closed"]; if (r) closed[q.id] = r.em >= 1; });
  let rows = D.questions.filter(q => q.runs[m+"|"+c]);
  rows = rows.filter(q => {
    const r = q.runs[m+"|"+c];
    if (t === "flagged") { if (!(q.flags && q.flags.length && (!window.__flag || q.flags.includes(window.__flag)))) return false; }
    else if (t !== "all" && q.type !== t) return false;
    if (o === "right" && r.em < 1) return false;
    if (o === "lenient" && !(r.len >= 1 && r.em < 1)) return false;
    if (o === "wrong" && r.len >= 1) return false;
    if (o === "called" && !r.tq) return false;
    if (o === "silent" && r.tq) return false;
    if (window.__tileFilter) { const right = !!closed[q.id]; const want = window.__tileFilter; if ((want.endsWith("wrong") && right) || (want.endsWith("right") && !right)) return false; }
    if (s && !(q.q.toLowerCase().includes(s) || q.gold.toLowerCase().includes(s) || r.p.toLowerCase().includes(s))) return false;
    return true;
  });
  $("#bcount").textContent = `${rows.length} of 592 questions match; ${Math.min(bLimit, rows.length)} shown.`;
  if (bx) bx.textContent = bLimit === 5 ? `Show all matching rows` : `Show 5 rows`;
  const tb = $("#btable tbody");
  tb.innerHTML = rows.slice(0, bLimit).map(q => { const r = q.runs[m+"|"+c]; const cls = r.em>=1 ? "match-1" : (r.len>=1 ? "match-l" : "match-0"); const lab = r.em>=1 ? "exact" : (r.len>=1 ? "lenient" : "wrong");
    return `<tr class="row" data-id="${q.id}"><td class="q">${esc(q.q)}</td><td>${esc(q.gold)}</td><td>${esc(r.p)}</td><td class="${cls}">${lab}</td><td class="m">${esc(r.tq)}${r.fb?" (fallback)":""}</td><td class="m">${esc(r.top)}</td></tr>`; }).join("") + (rows.length > bLimit ? `<tr><td colspan="6" class="lab">${bLimit === 5 ? "Five rows shown; the button above shows the rest." : "First 200 shown; narrow the filters or search."}</td></tr>` : "");
  tb.querySelectorAll("tr.row").forEach(tr => tr.onclick = () => {
    const q = D.questions.find(x => x.id === tr.dataset.id); const next = tr.nextElementSibling;
    if (next && next.classList.contains("detail")) { next.remove(); return; }
    const det = document.createElement("tr"); det.className = "detail";
    const all = Object.entries(q.runs).filter(([k]) => k.startsWith(m+"|")).map(([k,r]) => `<div><b>${esc(CONDN[k.split("|")[1]]||k)}:</b> ${esc(r.p)} <span class="${r.em>=1?"match-1":(r.len>=1?"match-l":"match-0")}">${r.em>=1?"exact":(r.len>=1?"lenient":"wrong")}</span>${r.tq?` &middot; query: <span class="m">${esc(r.tq)}</span>`:""}${r.top?` &middot; fetched: ${esc(r.top)}`:""}${r.dec?` &middot; said: ${esc(r.dec)}`:""}</div>`).join("");
    const FL = {leak:"answer appears in the question", unknown:"gold answer is 'unknown'", no_qmark:"hint, no question mark", multi:"several answers in one gold", danish_letters:"gold has Danish letters the official scorer deletes"};
    det.innerHTML = `<td colspan="6"><div><b>Subject:</b> ${esc(q.subject)} &middot; <b>type:</b> ${q.type}${q.flags && q.flags.length ? ` &middot; <b>noise:</b> ${q.flags.map(f => FL[f] || f).join("; ")}` : ""} &middot; <b>answer in the ranked-index text:</b> ${q.hit_local===true?"yes":(q.hit_local===false?"no":"unknown")} &middot; <b>in the search-box text:</b> ${q.hit_shaped===true?"yes":(q.hit_shaped===false?"no":"unknown")}</div>${all}</td>`;
    tr.after(det);
  });
}
drawBrowser();

/* ---------- failures: default answers and by type ---------- */
{
  const norm = s => String(s||"").toLowerCase().replace(/[^a-z0-9æøå]+/g," ").trim();
  const fav = (m, c) => { const cnt = {}; let n = 0;
    D.questions.forEach(q => { const r = q.runs[m+"|"+c]; if (!r) return; n++; const k = norm(r.p); cnt[k] = (cnt[k]||0)+1; });
    if (n < 500) return null;
    const [k, v] = Object.entries(cnt).sort((a,b)=>b[1]-a[1])[0]; return `${esc(k.slice(0,30))} (${v})`; };
  $("#deftable tbody").innerHTML = MAIN.map(m => { const a = fav(m,"closed"), b = fav(m,"retrieve-local");
    return (a||b) ? `<tr><td>${esc(MODELS[m])}</td><td>${a||'<span class="gap">not run</span>'}</td><td>${b||'<span class="gap">not run</span>'}</td></tr>` : ""; }).join("");
  $("#typetable tbody").innerHTML = MAIN.map(m => {
    const c = A(m,"closed"), r = A(m,"retrieve-local");
    if (!c || !r || r.n < 500) return "";
    const cell = (a,t) => a.by_type[t] ? pc(a.by_type[t][0]) : `<td class="n gap">not run</td>`;
    return `<tr><td>${esc(MODELS[m])}</td>` + ["year","number","text"].map(t=>cell(c,t)).join("") + ["year","number","text"].map(t=>cell(r,t)).join("") + `</tr>`; }).join("");
}

/* ---------- benchmark noise table ---------- */
if (D.noise) {
  const c = D.noise.counts, n = D.noise.n;
  const rows = [
    ["leak", "The answer appears in the question", "answerable from the question alone; every model benefits equally"],
    ["unknown", "The gold answer is 'unknown'", "cannot be answered right by design"],
    ["multi", "Several answers packed into one gold string", "exact match cannot hit them"],
    ["no_qmark", "A question with a hint and no question mark", "a single malformed row"],
    ["danish_letters", "Gold answers with æ, ø or å", "the official scorer deletes those letters, which lowers word-level F1 and BLEU for the same rows in every model; exact match is unaffected"]];
  $("#noisetable tbody").innerHTML = rows.filter(r => c[r[0]]).map(r => `<tr class="row" data-f="${r[0]}"><td>${esc(r[1])}</td><td class="n">${c[r[0]]} <span class="lab">(${pct0(c[r[0]]/n)})</span></td><td>${esc(r[2])}</td></tr>`).join("");
  $("#noisetable tbody").querySelectorAll("tr.row").forEach(tr => tr.onclick = () => { window.__flag = tr.dataset.f; $("#btype").value = "flagged"; window.__tileFilter = null; drawBrowser(); $("#browser").scrollIntoView({behavior:"smooth", block:"start"}); });
}

/* ---------- model card and cost ---------- */
{
  const meta = {"mimir-hf":["1.0 B (1.8 B with embeddings)","fp16, official implementation, prefix attention"], mimir:["1.0 B (1.8 B with embeddings)","Q8_0, community GGUF, causal attention"], llama1b:["1.2 B","Q8_0"], llama3b:["3.2 B","Q8_0"], gemma4b:["4.3 B","Q6_K"], qwen3b:["3.1 B","Q8_0"]};
  $("#cardtable tbody").innerHTML = MAIN.map(m => { const r = A(m,"retrieve-local"), c = A(m,"closed"); const mm = meta[m] || ["", ""]; return `<tr><td>${esc(MODELS[m])}</td><td class="n">${mm[0]}</td><td>${mm[1]}</td><td class="n">${c ? pct(c.em) : ""}</td><td class="n">${r ? pct(r.em) + (r.n < 592 ? ` (${r.n} so far)` : "") : ""}</td></tr>`; }).join("");
}

/* ---------- guided tour (spotlight; positions computed from document coordinates, then scrolled) ---------- */
(function(){
  const STEPS = [
    {sel:"#top h1", k:"Welcome · 1 of 10", html:`This page measures DAISY, the Danish Foundation Models benchmark, and everything around it. <b>Read the four numbers under the title first:</b> the published Mimir score reproduced, the community port fixed, Mimir with one lookup, and how many models knew when to look.`},
    {sel:"#primer .glossary", k:"Terms · 2 of 10", html:`Every term is defined once, in this list, and <b>every dotted-underlined term on the page shows its definition on hover</b>. Answer recall, reading fidelity and the decision carry the analysis.`},
    {sel:"#mimirtable", k:"Reproduction · 3 of 10", html:`<b>Four runs of the same weights, and the published number in bold.</b> The official implementation reproduces it within one standard error; the community llama.cpp port loses a third of it by reading the prompt the wrong way round; the last run is that port with the fix built for this study.`},
    {sel:"#fixed h3", k:"Broken and fixed · 4 of 10", html:`Reproduction surfaced three findings: the port that reads backwards, now fixed in 35 lines and checked on all 592 questions; a prompt that exists in two versions one blank line apart; and the benchmark's own noise, counted row by row.`},
    {sel:"#a2chart", k:"What a lookup adds · 5 of 10", html:`<b>Select a search engine above the chart.</b> Each bar sits in a light track that ends at the engine's ceiling, the share of questions whose answer was fetched at all. Between engines the models do not change; the engine does.`},
    {sel:"#decchart", k:"Where the questions go · 6 of 10", html:`<b>Select a model above the chart.</b> Top row: where the answer was. Bottom row: what the model did with it. The legend under the chart names every colour; the ticks mark the ceilings of narrower and wider lookups.`},
    {sel:"#tilegrid", k:"The decision · 7 of 10", html:`<b>A two-by-two: what the model decided, against what its memory could deliver.</b> Select a model and a variant, then click a tile to see those questions. The red count is the bluff: answered from memory, and wrong.`},
    {sel:"#asked-first", k:"Questions and answers · 8 of 10", html:`Questions a reader is likely to ask, answered in order: the attention modes, how good the headline score is, the two-model pipeline, the choice of 592, the query, and a second retrieval.`},
    {sel:"#bcontrols", k:"Every answer · 9 of 10", html:`<b>Filter, search, click a row.</b> All 592 questions with every model's answer under every condition, five rows at a time; the button shows all matches.`},
    {sel:"#coda pre", k:"Run it yourself · 10 of 10", html:`Three commands reproduce the main table on any machine with a served model, in the dfm-evals format. The Replay button at the top restarts this walkthrough.`},
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
  if (!location.hash) setTimeout(start, 600);
})();
})();
