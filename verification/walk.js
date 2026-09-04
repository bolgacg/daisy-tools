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
    const fills = await page.evaluate(() => [...document.querySelectorAll('[data-fill]')].filter(e => !e.textContent.trim()).map(e => e.getAttribute('data-fill')));
    const nums = await page.evaluate(() => ({ h1: document.querySelector('h1').textContent, mimir: document.querySelector('[data-fill=mimir_closed_pct]').textContent, best: document.querySelector('[data-fill=best_agentic_pct]').textContent, rows: document.querySelectorAll('#btable tbody tr.row').length, tiles: [...document.querySelectorAll('.tile .v')].map(e => e.textContent).join('/') }));
    console.log(`== ${w}px: errors=${errors.length} overflow=${overflow}px emptyFills=${JSON.stringify(fills)}`);
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
    for (const sel of ['#a1chart', '#a2chart', '#reptable', '#btable']) { const el = await page.$(sel); if (el) await el.screenshot({ path: path.resolve(__dirname, `el_${w}_${sel.slice(1)}.png`) }); }
    await page.screenshot({ path: path.resolve(__dirname, `page_${w}_full.png`), fullPage: true });
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error('WALK FAILED', e); process.exit(1); });
