// Screenshots at 390 and 1366 of the pages the spec names, plus the overflow check at 390 and axe on each.
//   node shots.cjs <base url> <out dir> <path> [<path> ...]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const axe = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const [base, out, ...paths] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const name = (u) => (u === '/' ? 'home' : u.replace(/^\//, '').replace(/[^a-z0-9]+/gi, '-'));
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const results = [];
  for (const width of [390, 1366]) {
    const ctx = await b.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, deviceScaleFactor: 1, bypassCSP: true });
    const p = await ctx.newPage();
    for (const u of paths) {
      const res = await p.goto(base + u, { waitUntil: 'networkidle' });
      const file = path.join(out, `${name(u)}-${width}.png`);
      await p.screenshot({ path: file, fullPage: true });
      const overflow = await p.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
      let violations = [];
      await p.addScriptTag({ content: axe });
      violations = await p.evaluate(async () => {
        const r = await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice'] });
        return r.violations.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length, eg: v.nodes[0] && v.nodes[0].html.slice(0, 160) }));
      });
      results.push({ u, width, status: res && res.status(), file, overflow, violations });
      console.log(`${width} ${u} status ${res && res.status()} overflow=${overflow} axe=${violations.length ? violations.length + ' violations' : 'clean'} -> ${file}`);
      for (const v of violations) console.log('    ', v.impact, v.id, 'x' + v.n, '|', v.eg);
    }
    await ctx.close();
  }
  await b.close();
  fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(results, null, 1));
})();
