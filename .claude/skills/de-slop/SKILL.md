---
name: de-slop
description: >-
  Remove AI slop from copy and from web design. Use this whenever someone says text "sounds like AI",
  "reads like ChatGPT", "feels generated", or that a site "looks AI-generated", "looks vibe-coded" or "looks
  like a template", and whenever they ask to clean up copy, humanize or de-slop text, or review a website,
  landing page, product page, README or marketing copy, even if they never mention AI. Covers the words
  (staged contrasts, stock AI vocabulary, hype, filler, dashes, slogans, a self-scoring pass) and the looks
  (cream-and-serif or SaaS-card templates, eyebrow labels, big-number stat heroes, default fonts), and ships
  a dependency-free linter, scripts/slop_lint.py, for a repeatable check after every build.
---

# De-slop

Make copy read like a specific person wrote it for a specific reader, and make pages look like someone
designed them for this subject. Two passes, Words then Looks, followed by a check you can repeat.

Generated text and generated design fail the same way: each choice is the safest default for any reader
and any subject. The fix is the same too. Choose for this reader and this subject, and keep every fact.

## Rules that never bend

- Facts don't change. Keep every number, date, name, claim and caveat, each with its source link. Never
  invent customers, testimonials, logos, quotes, ratings or user counts. If a sentence needs a fact you
  don't have, write a simpler sentence or ask.
- Behavior doesn't change. Keep URLs, element IDs, classes and form fields that scripts depend on, or
  update the scripts in the same change.
- Quotations stay verbatim. Mark them (`<q>`, `<blockquote>`) so the linter skips them.

## Workflow

1. **Baseline.** Run the linter and save the output:
   `python3 .claude/skills/de-slop/scripts/slop_lint.py PATHS --summary`.
   For a site, also take screenshots at desktop width and at 390px.
2. **Inventory the facts.** List every number with its proof link and every caveat (beta, pricing not
   final, not legal advice). This list must survive the rewrite unchanged.
3. **Words pass** (below, details in `references/words.md`).
4. **Looks pass** (below, details in `references/design.md`).
5. **Verify.** Lint again and aim for `clean` or `near-clean`. Screenshot again (desktop, 390px, dark
   mode if the site has one) and check for horizontal scroll. Click through forms and filters. Diff the
   numbers against step 2.
6. **Report** the before and after scores, the biggest changes, and anything you were unsure about.

## Words

### Cut these on sight

<!-- slop-lint: off (this list quotes the patterns it bans) -->
- **Staging.** "Not just X but Y", "it's not X, it's Y", "no X, no Y, just Z", a one-line closer that
  repeats the paragraph, "Here's the thing", question headings, two-part "X, and why" headings.
- **Inflation.** Stock AI words (delve, pivotal, seamless, robust, landscape, unlock, empower, leverage,
  showcase, testament), claims of significance ("plays a key role"), sales language ("powerful",
  "never miss a hearing"), unnamed authorities ("experts say").
- **Filler.** Adverbs that add nothing (simply, really, just, actually), stacked hedges ("could
  potentially"), stock transitions (Additionally, Moreover), "It's worth noting".
- **Rhythm by rule.** Ideas forced into threes, a dash in every paragraph, sentences of equal length, the
  same slogan repeated on every page ("no account, no email").
- **Writing about the page.** "The table below", "shown first", "everything below is measured against".
  The reader can see the page.
- **Leftovers.** Chat wrappers ("I hope this helps"), knowledge-limit hedges, placeholders.
<!-- slop-lint: on -->

### Rewrite like this

- Lead with the fact the reader came for, and put the number first: "240 of 351 towns", not "a large
  share of towns".
- Use concrete nouns and plain verbs: is, has, reads, posts, flags, votes. Name the board, the statute,
  the date.
- Vary sentence length. Let a long sentence carry the detail and a short one land the point, but not
  in a pattern.
- Headings name what the section holds, in sentence case. "How far ahead agendas are posted", not
  "Know before the hearing".
- A button says what happens ("Create watchlist") and the confirmation uses the same word ("Watchlist
  created").
- Keep a caveat when it changes what the reader does. Say it once, in the place it applies.
- Hedge only where the evidence is uncertain; state everything else plainly.
- Errors say what happened and how to fix it. Empty states say what to do next.
- Rewrite the sentence around its point instead of patching one flagged phrase at a time.

### Self-score the words

Rate the draft 1 to 10 on each line. Below 40 of 50, revise and score again.

| Dimension | Question |
|---|---|
| Directness | Does each sentence state something, or announce that something is coming? |
| Specificity | Could this sentence appear unchanged on a competitor's page? (It shouldn't.) |
| Rhythm | Read it aloud. Do sentence lengths and openings vary? |
| Trust | Does it treat the reader as smart and busy, without hype, hand-holding or false urgency? |
| Density | Can any sentence go without losing a fact? |

Then run the linter. It catches the mechanical tells only; triads, vague claims and invented facts still
need your read.

## Looks

### The tells

- **Palette by default.** Warm cream background with a high-contrast serif and a terracotta accent; or
  near-black with one acid-green accent.
- **The SaaS card kit.** Everything chopped into identical rounded cards with the same soft grey shadow,
  one radius on every element, gradient washes as decoration.
- **Template chrome.** A tracked all-caps eyebrow above every heading, meta strings joined with middle
  dots, monospace for small labels, an arrow after every link, 01/02/03 markers on things that aren't
  steps.
- **The default hero.** Big number, small label, four across, two buttons under a one-line promise.
- **Default type.** Inter or Roboto everywhere, or one headline word set in a different color.
- **Motion by default.** Every section fades up on scroll; every card lifts on hover.
- **One skeleton for every page.** Eyebrow, H1, lead, two buttons, stat cards, whatever the page is for.

### Do this instead

1. Ground the design in the subject. List the objects, documents, materials and vocabulary of the
   subject's world; distinct choices come from there. Write a short plan with 4 to 6 named colors, one
   or two typefaces with roles, a layout idea and one principle. Check the plan against the tells above
   and change any part you would have produced for any other product.
2. Open with the most characteristic thing in that world, using real content: a live record, a real
   document, a working tool. Use a stat row only when it is the best option.
3. Let structure carry information. Tables for comparisons, lists for sets, a timeline for dated
   events, numbered steps only for sequences, cards only for separate objects.
4. Spend boldness in one place and keep everything around it quiet. Before shipping, remove one
   accessory.
5. Choose type on purpose: one or two families with clear roles, sentence-case headings, a real scale,
   lines under about 75 characters. Under a strict CSP, self-host a subset woff2 with its license.
6. Hold the quality floor. No horizontal scroll at 390px, tables that work on a phone, visible focus,
   AA contrast in light and dark, reduced motion respected.

### Self-check the looks

Answer yes or no; each "no" is a fix.

- With the logo and words removed, could you tell what subject this site is about?
- Does each border, label, number marker and color encode something?
- Is there one memorable element, with everything around it quieter?
- Do different pages have different shapes, matched to what each page is for?
- Does it work at 390px, in dark mode, and with the keyboard?

## The linter

```sh
python3 .claude/skills/de-slop/scripts/slop_lint.py site/*.html site/topics docs/README.md --summary
python3 .claude/skills/de-slop/scripts/slop_lint.py copy.txt              # every hit as file:line
python3 .claude/skills/de-slop/scripts/slop_lint.py site --max-density 1  # exit 1 above 1 per 1,000 words, for CI
python3 .claude/skills/de-slop/scripts/slop_lint.py --list-rules
```

It reads HTML (visible text, headings, `title`, `alt`, `placeholder`, `aria-label`, meta descriptions),
Markdown, plain text and CSS. Each hit adds its rule's weight: 1 is weak alone, 2 is a usual tell, 3 is
near-certain. It skips code, `<q>`, `<blockquote>`, curly-quoted text, elements with `data-slop-ignore`,
lines marked `slop-lint: ignore`, and regions between `slop-lint: off` and `slop-lint: on`. Use the
markers for proper names and quotations, not to hide copy you wrote. `--no-looks` scores the words only.

## Applying it to 351 Watch

351 Watch reads Massachusetts, New York and Rhode Island town board agendas and flags siting items.

- The paying readers are energy and data-center developers and land-use and energy lawyers. They know
  "ZBA", "40B" and "G.L. c. 40A, §3", so don't explain the basics to them. Residents, reporters and town
  officials use it free and mostly land on town pages; spell terms out there on first use.
- Write like a careful municipal reporter: plain, exact, dated. Skip urgency theater.
- Lead with value, and put pricing last: what we catch, how many days before the meeting, and in which
  towns. Keep dollar amounts and plan tables off public pages during the beta; `/pricing` says what is
  free now and that watching many places will be a paid plan later.
- Every number keeps its proof link, to `/proof`, the Attorney General's letter or the agenda itself.
  A number without a source gets cut, not rounded into a vaguer claim.
- Keep the caveats: the free founding beta, paid plans that are planned and not on sale,
  "informational only, not legal advice", and the towns we can't read, with the reason.
- Agenda snippets are quotations. Render them in `<q>` or `<blockquote>` and never edit them.
- Check after each build (bash):

  ```sh
  python3 projects/351watch/build.py
  python3 .claude/skills/de-slop/scripts/slop_lint.py projects/351watch/site/*.html \
    projects/351watch/site/{ma,ny,ri,topics} projects/351watch/site/styles.css --summary
  ```

## Sources

Adapted from three MIT and Apache-2.0 skills. License texts are in `licenses/`, and `licenses/NOTICE.md`
lists what was adapted and changed.

- [humanizer](https://github.com/blader/humanizer) by Siqi Chen, MIT. Pattern catalogue and editing
  process, itself based on Wikipedia's "Signs of AI writing".
- [stop-slop](https://github.com/hardikpandya/stop-slop) by Hardik Pandya, MIT. Phrase and structure
  lists, and the five-dimension scoring rubric (adapted here).
- [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) by Anthropic,
  Apache-2.0. The visual tells of generated sites and the plan-then-critique design process.
- [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
  WikiProject AI Cleanup. Pattern names and vocabulary eras, paraphrased.
