# Looks: visual tells of generated sites and their fixes

Adapted from Anthropic's frontend-design skill (Apache-2.0). Changed: condensed, reorganized as a
tell-and-fix catalogue for reworking existing sites, and extended with fixes for tables, fonts under a
strict Content Security Policy, and a screenshot review loop. See `../licenses/NOTICE.md`.

## Where the tells come from

A generated page reaches for the choice that fits any subject. Each trait below is fine for some brief;
it becomes a tell when it appears regardless of subject. When the brief or an existing brand pins a
choice down, follow it. When an axis is free, don't spend it on a default.

## The tells

### Palette

- Warm cream page (around `#F4F1EA` to `#F7F6F2`) with a high-contrast serif display and a terracotta or
  clay accent (around `#D97757`).
- Near-black page (`#0B0B0B`, `#111`) with one acid-green, electric-blue or vermilion accent.
- Purple-to-blue gradient washes behind the hero; colored glows; frosted-glass panels.
- Status colors that don't mean anything consistent across the site.

### Layout and components

- The SaaS card kit: every piece of content in an identical rounded card, one border radius on every
  element whatever its role, the same soft grey shadow (`rgba(0,0,0,.05)` to `.1`) under each.
- Feature grids of three or four equal cards, each with an icon, a bold label and two lines of text.
- A broadsheet pastiche: hairline rules, zero radius and dense newspaper columns with no reason.
- Numbered markers (`01`, `02`, `03`) on things that aren't a sequence.

### Template chrome

- A tracked-out ALL-CAPS eyebrow above every heading.
- Meta strings joined with middle dots (`Board · Oct 6 · 3 items`).
- Labels built as `WORD — fragment` with a spaced dash.
- Monospace for dates and small data labels, as decoration.
- An arrow appended to every link and button.
- Uppercase, letter-spaced table headers.

### The default hero

- One-line promise, a lead paragraph, two buttons (solid and ghost), then a row of four stat cards with
  a big number and a small grey label.
- A centered layout with a gradient background and a product screenshot tilted in 3D.

### Type

- Inter, Roboto, Poppins or the system UI font everywhere, at the same two weights.
- One word of the headline set in a different color, weight or italic.
- No real scale: every heading a step of the same clamp().

### Motion

- Every section fades and slides up on scroll; every card lifts on hover. Motion that answers a person's
  action (opening, expanding, confirming) is fine; motion for its own sake reads as generated.

### Copy inside the design

- Slogan headings ("Know before the hearing"), question headings, `Get started` and `Learn more`
  buttons, testimonials and logos that don't exist. See `words.md`.

### One skeleton for every page

- Eyebrow, H1, lead, two buttons, stat cards, card grid, whatever the page is for. A watchlist form, a
  ledger of legal decisions and a pricing page should not share a hero.

## What to do instead

### 1. Plan from the subject

Before touching CSS, write down:

- Subject, audience and the page's main job, one sentence each.
- The subject's world: its documents, objects, materials, places and vocabulary. A municipal records
  service has posted notices, warrants, clerk's time stamps, decision letters and statute citations. A
  bakery has flour, paper bags, chalkboards and handwritten prices.
- Color: 4 to 6 named hex values with roles (page, ink, muted, rule, one accent, status colors).
- Type: one or two families and their roles.
- Layout: a sentence and a rough ASCII wireframe for the key page, with alignment.
- One principle that makes this site unlike its neighbors.

Then review the plan against the tells. Imagine the page you would make for a similar brief; any part of
this plan that matches it is a default, so change it and note why.

### 2. Open with the most characteristic thing

Put the subject's most typical object on the first screen, made from real content: the next items on
actual agendas, a real record, a working search, the actual product doing its job. A stat row is one
option among many. If you use numbers, a compact table of labeled figures with sources often reads as
more credible than big-number cards.

### 3. Make structure carry information

| Content | Use | Avoid |
|---|---|---|
| Comparisons across rows | A table with aligned, tabular figures | A card per row |
| Dated events | A timeline or dated list | A grid of equal cards |
| A set of peers (plans, topics) | A table or a plain list | Feature cards with icons |
| Steps | A numbered list | Numbering on non-sequences |
| Quotations from documents | `<blockquote>` or `<q>` with the source | Body text in quote marks |
| Status | One color system used the same way on every page | Colors picked per component |

Borders, rules and labels should each say something: this is a separate object, this row ends here, this
value is a date. Remove the ones that don't.

### 4. Spend boldness once

Pick one element to be memorable and keep the rest quiet: plain backgrounds, few borders, one accent.
Before shipping, take one decoration away.

### 5. Type

- Choose for the subject, not from habit. One family can carry a whole site; a second must be clearly
  different and have its own job (headings, numerals, quotations).
- Sentence-case headings. A real scale with clear steps. Body at 16px or more, lines under about 75
  characters, `font-variant-numeric: tabular-nums` in tables.
- Under a strict CSP (`font-src` falls back to `default-src 'self'`), self-host fonts. Subset to Latin
  and convert to woff2 with fontTools, then ship the OFL text next to the files:

  ```sh
  pip install fonttools brotli
  pyftsubset Font[wght].ttf --unicodes="U+0000-00FF,U+0131,U+0152-0153,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2190-2193,U+2212,U+2215" \
    --layout-features="kern,liga,tnum,lnum,case" --flavor=woff2 --output-file=font-latin.woff2
  ```

  Use `font-display: swap`, preload only the face used above the fold, and keep the total under about
  100 KB.

### 6. Tables on phones

Wide tables either scroll inside their own container (never the page) or stack: each row becomes a
block, cells show their column name from a `data-label` attribute, numbers sit inline. Keep the first
column (the row's name) bold so stacked rows stay scannable.

### 7. Quality floor

- No horizontal page scroll at 390px. Check `document.documentElement.scrollWidth` against the
  viewport width in a headless browser.
- Visible keyboard focus on every interactive element.
- WCAG AA contrast (4.5:1 for body text, 3:1 for large text and UI borders) in light and dark themes.
- `prefers-reduced-motion` respected.
- Tap targets at least 40px tall on touch layouts.
- Status never shown by color alone: badges carry words.

### 8. Review with screenshots

Take full-page screenshots at desktop width and at 390px, in light and dark, before and after. Look at
each one for the tells above. A minimal Playwright loop:

```js
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  for (const [w, h, name] of [[1366, 900, 'desktop'], [390, 844, 'mobile']]) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto('http://127.0.0.1:8080/', { waitUntil: 'networkidle' });
    const wide = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    await page.screenshot({ path: `home-${name}.png`, fullPage: true });
    console.log(name, wide ? 'HORIZONTAL SCROLL' : 'ok');
  }
  await browser.close();
})();
```

## Self-check

- With the logo and words removed, could someone tell what this site is about?
- Does every border, label, number marker and color encode something?
- Is there exactly one memorable element?
- Does each page's shape fit its job?
- Light, dark, 390px and keyboard: all fine?
- Did you take one accessory off?
