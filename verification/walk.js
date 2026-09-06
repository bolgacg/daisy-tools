// Headless check of the results page: errors, overflow, screenshots, tour placement at two widths.
const path = require('path');
const { chromium } = require(process.env.PW || '/home/bolgac/projects/minimalist-workout-app/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const url = 'file://' + path.resolve(__dirname, '../site/index.html');
  for (const [w, h] of [[1536, 900], [390, 844]]) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(1200);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    // no two text elements inside any one SVG may intersect
    const svgOverlaps = await page.evaluate(() => {
      const bad = [];
      document.querySelectorAll('.viz-root svg').forEach((svg, si) => {
        const ts = [...svg.querySelectorAll('text')].map(t => ({ t: t.textContent.trim(), r: t.getBoundingClientRect() })).filter(x => x.t);
        for (let i = 0; i < ts.length; i++) for (let j = i + 1; j < ts.length; j++) {
          const a = ts[i].r, b = ts[j].r;
          const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
          if (ox > 1 && oy > 1) bad.push(`svg${si}: "${ts[i].t}" x "${ts[j].t}" (${Math.round(ox)}x${Math.round(oy)}px)`);
        }
      });
      return bad;
    });
    // no silently empty table cell: every td must have text or carry class "gap"/"lab" or data-empty-ok
    const emptyCells = await page.evaluate(() => {
      const bad = [];
      document.querySelectorAll('table tbody td').forEach(td => {
        if (!td.textContent.trim() && !td.querySelector('.gap') && !td.classList.contains('gap') && !td.hasAttribute('data-empty-ok')) {
          const tbl = td.closest('table'); bad.push((tbl ? '#' + tbl.id : '?') + ' row ' + (td.parentElement.rowIndex ?? '?'));
        }
      });
      return bad.slice(0, 10);
    });
    const fills = await page.evaluate(() => [...document.querySelectorAll('[data-fill]')].filter(e => !e.textContent.trim()).map(e => e.getAttribute('data-fill')));
    const nums = await page.evaluate(() => ({ h1: document.querySelector('h1').textContent, mimir: document.querySelector('[data-fill=mimirhf_closed_pct]').textContent, best: document.querySelector('[data-fill=mimirhf_local_pct]').textContent, rows: document.querySelectorAll('#btable tbody tr.row').length, tiles: [...document.querySelectorAll('.tile .v')].map(e => e.textContent).join('/') }));
    console.log(`== ${w}px: errors=${errors.length} overflow=${overflow}px emptyFills=${JSON.stringify(fills)} svgOverlaps=${svgOverlaps.length} emptyCells=${emptyCells.length}`);
    svgOverlaps.slice(0, 8).forEach(o => console.log('    OVERLAP', o));
    emptyCells.forEach(c => console.log('    EMPTYCELL', c));
    if (svgOverlaps.length || emptyCells.length) process.exitCode = 1;
    console.log('   ', JSON.stringify(nums));
    errors.slice(0, 5).forEach(e => console.log('    ERR', e));
    // tour: walk every step, log highlight geometry
    await page.evaluate(() => { try { localStorage.setItem('daisy_tour', 'done'); } catch (e) {} });
    const n = await page.evaluate(() => window.__tour.steps);
    for (let i = 0; i < n; i++) {
      await page.evaluate(i => window.__tour.go(i), i);
      await page.waitForTimeout(700);
      const g = await page.evaluate(() => { const hl = document.getElementById('tour-hl').getBoundingClientRect(); const c = document.getElementById('tour-card').getBoundingClientRect(); return { hlTop: Math.round(hl.top), hlH: Math.round(hl.height), cardTop: Math.round(c.top), cardH: Math.round(c.height), overlap: !(c.top >= hl.bottom || c.bottom <= hl.top || c.left >= hl.right || c.right <= hl.left) }; });
      console.log(`    step ${i + 1}: highlight top ${g.hlTop} h ${g.hlH} | card top ${g.cardTop} h ${g.cardH} | overlaps highlight: ${g.overlap}`);
      if (i === 3 || i === 5) await page.screenshot({ path: path.resolve(__dirname, `tour_${w}_step${i + 1}.png`) });
    }
    await page.evaluate(() => document.getElementById('tskip').click());
    await page.waitForTimeout(300);
    await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(300);
    await page.screenshot({ path: path.resolve(__dirname, `page_${w}_top.png`) });
    for (const sel of ['#a1chart', '#a2chart', '#decchart', '#tilegrid', '#reptable', '#mimirtable', '#speedtable', '#typetable', '#deftable', '#noisetable', '#secondtable', '#mwqatable', '#popqatable', '#cardtable', '#btable', '.headline', '#contents']) { const el = await page.$(sel); if (el) { try { await el.scrollIntoViewIfNeeded(); await el.screenshot({ path: path.resolve(__dirname, `el_${w}_${sel.replace(/[#.]/g, '')}.png`) }); } catch (e) {} } }
    await page.screenshot({ path: path.resolve(__dirname, `page_${w}_full.png`), fullPage: true });
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error('WALK FAILED', e); process.exit(1); });
