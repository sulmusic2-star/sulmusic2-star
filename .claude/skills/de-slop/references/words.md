# Words: patterns to cut and how to rewrite them

Adapted from humanizer (Siqi Chen, MIT) and stop-slop (Hardik Pandya, MIT), which draw on Wikipedia's
"Signs of AI writing". Condensed and reorganized, with new examples and patterns for product and web copy.
See `../licenses/NOTICE.md`.

Watched words and phrases are in code spans so the linter skips this file's examples, and the
before-and-after examples are blockquotes for the same reason. The ids in parentheses after each heading
are the rule ids `scripts/slop_lint.py` reports.

## Why it happens

A model writes the most likely next phrase, which is the choice that suits the widest range of readers.
A person writes for one reader about one subject, so their choices are uneven and specific. Each pattern
below is a default choice in one form: staging (signalling importance instead of adding a fact), rhythm
applied by rule, inflated significance, decorative formatting, chat leftovers, and writing for a reader
who has no context.

Word lists change with each model generation; structures change slowly. Treat the structures as the
stronger evidence. Wikipedia's editors track vocabulary by era; their 2026 list adds `challenge`,
`clearer`, `dependable`, `echoed`, `foster`, `leverage`, `matters`, `multifaceted`, `practical`,
`prioritize`, `quietly`, `steady` and `universally`. Those words are weak alone; act when several cluster.

## How to edit

1. Read the whole text once and mark every tell, strongest first. Look at paragraph shape as well as
   sentences: three parallel examples, or the same closer after every section, is a tell at larger scale.
2. Draft the rewrite. Keep every supported claim. Shorten, merge, split and reorder freely, but don't
   add a fact, number, name, date or quote that isn't in the source.
3. Read the draft aloud. Ask what still sounds generated. Check that no fact was added or dropped.
4. Search again for the tells that survive rewrites most often: contrasts, closers, triads, dashes and
   bold labels.
5. Score it (the table in `SKILL.md`) and run the linter.

If a writing sample exists, match its sentence length, punctuation and vocabulary; the sample beats
these rules, including the dash rule.

## A. Staging instead of stating

The strongest tells. One sighting justifies an edit.

**1. Not X but Y** (`not-x-but-y, its-not-x-its-y, isnt-just`). Watch for `not just X, but Y`,
`it's not X, it's Y`, `X rather than Y` when nobody claimed X, the same contrast split over two
sentences, and a clipped negative tail (`..., no guessing`). The negative half invents a claim so the
positive half sounds bigger. State Y. Keep a contrast only when readers hold X to be true.

> Before: It's not just a tracker. It's an early-warning system for your pipeline.
> After: It lists siting items from town agendas, usually several days before the meeting.

**2. Formula negations** (`no-x-no-y-just, negative-listing, clipped-negatives`). `No X, no Y, just Z`;
`Not a X. Not a Y. A Z.`; a pair of clipped negatives repeated as a slogan (`no account, no email`).
Say the fact once, in a full sentence, where it matters.

> Before: No signup. No email. Just a link.
> After: You don't need an account. The watchlist's private link is the only key.

**3. One-line closers and fragments** (`closer`). `That's the point.` `This matters.` `Read that again.`
A one-sentence paragraph that restates the one before it, or a row of fragments for drama. Cut the
closer, or replace it with a consequence the paragraph didn't state.

> Before: Most agendas go up five days ahead. That's your window.
> After: Most agendas go up five days ahead, which leaves time to read the packet and call the planner.

**4. Run-ups** (`throat-clearing, worth-noting`). `Here's the thing`, `Let's dive in`, `The truth is`,
`It turns out`, `When it comes to`, `At its core`, `It's worth noting that`. Delete the run-up and start
with the point.

**5. Arguing with no one.** `This isn't about X`, `To be clear`, `You might think... but`,
`A tempting approach would be`. An objection or option the text never raised. Cut it unless a real
reader holds that view.

**6. Question headings and rhetorical questions** (`heading-question, rhetorical-cta`). `Will it survive?`,
`Ready to get started?`, `Tired of missing hearings?`. A heading names what the section holds; a CTA
says what happens.

> Before: Will a moratorium survive? The Attorney General's record
> After: How the Attorney General has ruled on moratoria

**7. Two-part headings** (`heading-and-why`). `Towns we can't read yet, and why`. The `, and why` tail is a
model habit. Name the content: "Towns we can't read yet".

## B. Rhythm by rule

**8. Forced triads.** Three adjectives, three parallel clauses, three examples, whether or not the
meaning has three parts. Keep a list of three when there are three things. Otherwise use two, or one
developed example.

**9. Dashes everywhere** (`em-dash, spaced-en-dash`). A dash lets the writer skip deciding how two clauses
relate. Use a comma, colon, period or parentheses. Leave hyphens, number ranges (`2022–2026`) and dashes
inside code or quotations alone.

**10. Same length, same shape.** Three sentences of equal length in a row, every paragraph ending on a
short punchy line, repeated sentence openings. Merge, split or reorder until the rhythm follows the
content.

**11. Stacked qualifiers** (`stacked-hedge`). `could potentially`, `may possibly`, `arguably`. Keep one
qualifier where the evidence is uncertain. Keep legal and safety caveats.

**12. Passive voice that hides the actor.** `Items are flagged`, `Mistakes were made`. Name who acts
when it helps: "We flag items", "The Attorney General disapproved the article". Weak alone.

## C. Inflation and borrowed authority

**13. Stock AI vocabulary** (`ai-vocab, hype, landscape`). `delve`, `tapestry`, `testament`, `pivotal`,
`underscore`, `showcase`, `intricate`, `meticulous`, `vibrant`, `realm`, `seamless`, `robust`,
`cutting-edge`, `unlock`, `empower`, `streamline`, `elevate`, `harness`, `leverage`, `landscape` used
abstractly, `in today's fast-paced world`. Use the plain word, or a number.

**14. Inflated significance** (`significance, crucial`). `plays a key role`, `a pivotal moment`,
`marks a shift`, `reflects a broader trend`, `crucial`, `vital`, `invaluable`, `actionable insights`.
Keep the fact and drop the weight. End on the last concrete fact, not a send-off.

**15. Sales language** (`marketing, hype`). `powerful`, `effortless`, `stay ahead`, `never miss`,
`peace of mind`, `all in one place`, `at your fingertips`, `the features you care about`. Say what the
product does, for whom, with a number when there is one.

> Before: Stay ahead of every hearing with powerful, real-time alerts.
> After: New items reach your Slack channel once a day, after the morning agenda scan.

**16. Vague declaratives** (`vague-declarative`). `The stakes are high.`
`The implications are significant.` Name the stake or the implication, or cut the sentence.

**17. Borrowed authority** (`borrowed-authority`). `Experts agree`, `studies show`, `industry reports`,
lists of outlets that "featured" someone, follower counts. Cite the source and what it said, or cut.

**18. Avoiding is and has** (`copula-dodge`). `serves as`, `stands as`, `functions as`, `boasts`,
`features`. Use is, are, has.

**19. -ing riders** (`ing-rider`). `..., highlighting its commitment to transparency`,
`..., ensuring a seamless experience`. Cut the rider; keep it only if the source supports the claim.

**20. Vague association** (`vague-association`). `associated with`, `in connection with`. Name the
relationship: founded, owns, chairs, applied for.

## D. Filler and hedges

**21. Adverbs that add nothing** (`filler-adverb, just, very`). `simply`, `really`, `truly`, `actually`,
`basically`, `just`, `very`, `quietly`, `deeply`. Cut them; if the sentence goes flat, the verb or noun
needs fixing.

**22. Stock transitions** (`transition-opener`). `Additionally,`, `Furthermore,`, `Moreover,`,
`Ultimately,`, `In conclusion,`. Start with the content; let order do the linking.

**23. Generic calls to action** (`generic-cta`). `Learn more`, `Get started`, `Discover`, `Click here`.
Name what happens: "Create a watchlist", "See the 34 tracked actions".

## E. Formatting by rule

**24. Bold as decoration** (`bold-label-list`). Bold on every list item, or `- **Label:** text` lists whose
labels add nothing. Remove the bold; turn label lists into sentences unless the labels carry information.

**25. Title Case headings** (`title-case`). Use sentence case. Proper names keep their capitals.

**26. Emoji and arrows** (`emoji, arrow`). Decoration on headings, bullets, links and buttons. Remove them.

**27. Middle-dot meta strings** (`middot-meta`). `Board · Oct 6 · 3 items`. Use separate elements, a
comma, or a line break.

## F. Leftovers from the chat and the draft

**28. Chat residue** (`chat-residue`). `Great question!`, `I hope this helps`, `Let me know if`,
`Would you like me to`, `Here is a summary`. Remove the wrapper, keep the content.

**29. Knowledge-limit hedges** (`cutoff-hedge`). `As of my last update`,
`While specific details are limited`, `based on available information`. Say what the source does not
show, or cut it.

**30. Placeholders** (`placeholder`). `[Insert date]`, `lorem ipsum`, `TODO:`. Fill or remove.

**31. Writing about the page** (`self-reference`). `The table below shows`, `Items are shown first`,
`Everything below is measured against these rules`, `This section explains`. The reader sees the
layout. Keep a convention only when the reader can't infer it, and state it once.

> Before: Items for meetings still ahead are shown first, with when we first saw them.
> After: (Cut. The list is sorted by meeting date, and each item already says when we first saw it.)

**32. Claims the page doesn't keep.** `Every number links to its evidence` when the numbers aren't links.
Make it true or cut it.

## G. Product and interface copy

- Name things by what the user does, not how the system works: "daily messages to your Slack channel",
  then mention "webhook" where the user pastes the URL.
- A button says what happens; the confirmation reuses the verb. "Create watchlist" leads to "Watchlist
  created". "Delete watchlist" asks "Delete this watchlist?" and offers "Delete" and "Keep it".
- Errors say what went wrong and how to fix it, without apology: "Choose at least one town."
- Empty states point to the next action: "No items for meetings ahead yet. Recent items are below."
- Pricing pages state what exists today and what is planned, with dates if you have them. Never imply a
  plan is for sale when it isn't.
- Repeated facts (free, no account) belong in one place each, not as a refrain on every page.

## When to leave it alone

A person can make any of these choices on purpose. Leave a watched phrase inside a quotation, a title, a
proper name, a legal citation, or a passage about the phrase itself. Text written before late 2022 is not
AI-written. People who judge by feel do little better than chance, so act on clusters of tells, and keep
the details that carry a writer's voice: an odd specific detail, mixed feelings, a dated reference, an
aside the writer can explain.
