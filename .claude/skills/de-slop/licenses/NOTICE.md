# Third-party notices

The de-slop skill adapts material from the projects below. Their license texts are in this folder.

## humanizer

- Source: https://github.com/blader/humanizer (`SKILL.md`, version 3.1.0, commit 225a6f3, 2026-09-27)
- Copyright (c) 2025 Siqi Chen. MIT License: `LICENSE-humanizer-MIT.txt`.
- Used in: `../SKILL.md` (Words section), `../references/words.md`, `../scripts/slop_lint.py` (rule lists).
- Changes: condensed and reorganized the pattern catalogue; wrote new before-and-after examples; added
  patterns for product and interface copy; turned part of the catalogue into regular expressions.

## stop-slop

- Source: https://github.com/hardikpandya/stop-slop (`SKILL.md`, `references/phrases.md`,
  `references/structures.md`, commit 8da1f03, 2026-03-18)
- Copyright (c) 2025 Hardik Pandya. MIT License: `LICENSE-stop-slop-MIT.txt`.
- Used in: `../SKILL.md` (self-scoring table), `../references/words.md`, `../scripts/slop_lint.py`.
- Changes: replaced the Authenticity dimension with Specificity and raised the revise threshold from 35
  to 40 of 50; merged the phrase and structure lists into the humanizer-based catalogue.

## frontend-design

- Source: https://github.com/anthropics/skills/tree/main/skills/frontend-design (`SKILL.md`,
  commit dbd4588, 2026-10-09)
- Copyright Anthropic. Apache License 2.0: `LICENSE-frontend-design-Apache-2.0.txt`.
- Used in: `../SKILL.md` (Looks section), `../references/design.md`, the CSS checks in
  `../scripts/slop_lint.py`.
- Changes: condensed and reorganized as a catalogue of tells and fixes for reworking existing sites;
  added guidance on tables for phones, self-hosted fonts under a strict Content Security Policy, and a
  screenshot review loop.

## Wikipedia: Signs of AI writing

- Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (WikiProject AI Cleanup, read
  2026-10-12). Text available under CC BY-SA 4.0.
- Used for pattern names and the note on vocabulary by model era. Nothing is copied beyond short lists
  of individual words, which are paraphrased and cited.
