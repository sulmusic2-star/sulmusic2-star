<div align="center">

# Tim Sullivan

### Forward-Deployed / Applied AI Engineer

I ship and operate production software by orchestrating AI agents. I built and run a live, paid answer engine for public records, and a live iOS app on the App Store, solo.

[**lastingground.com**](https://lastingground.com) &nbsp;·&nbsp; [**Portfolio**](https://sulmusic2-star.github.io/) &nbsp;·&nbsp; [**Contact**](https://sulmusic2-star.github.io/contact/)

[![live](https://img.shields.io/badge/live-lastingground.com-34d399?style=flat-square)](https://lastingground.com)
[![iOS App Store](https://img.shields.io/badge/iOS-SquadBrain-2c5b3a?style=flat-square)](https://apps.apple.com/us/app/squadbrain/id6756122317)
[![public tests](https://img.shields.io/badge/public_tests-43_passing-2c5b3a?style=flat-square)](https://github.com/sulmusic2-star/lasting-ground-showcase)
[![coverage](https://img.shields.io/badge/coverage-93%25-1a1a1a?style=flat-square)](https://github.com/sulmusic2-star/lasting-ground-showcase)

</div>

> **Currently building:** expanding deep state-by-state coverage across the U.S. for Lasting Ground, the [`groundtruth-geo`](https://github.com/sulmusic2-star/groundtruth-geo) benchmark and MCP server over the same engine, and [`agentic-engineering`](https://github.com/sulmusic2-star/agentic-engineering) — how I ship and operate production software with AI agents.

---

## GroundTruth-Geo — a deterministic, government-cited benchmark of parcel-precise property facts

[`groundtruth-geo`](https://github.com/sulmusic2-star/groundtruth-geo)

A machine-gradable benchmark of the exact questions frontier LLMs fail on geography (GPSBench / MapEval: under 25% on parcel geometry, 1–23% city-level localization). 33 questions across 7 states; every answer is a deterministic government record — FEMA / NPS / EPA — carrying an official source URL, a source date, and a reproducible content fingerprint.

- A **deterministic grader** with field-standard factuality metrics ([SimpleQA F1](https://arxiv.org/abs/2411.04368), [AA-Omniscience Index](https://arxiv.org/abs/2511.13029)). No LLM judge — ungameable.
- A **JSON-RPC stdio MCP server** exposing the records as `lookup_property_truth(address)` and `verify_property_record(record_id)` tools, so a model can be evaluated *with* the verifier and *against* it on the same questions.
- v1 baseline: a calibrated frontier model abstains on **100%** of these parcel-precise factual questions in the calibrated condition; the Lasting Ground engine answers every one, cited. The closed-book → tool gap is the artifact.

[Repo →](https://github.com/sulmusic2-star/groundtruth-geo) &nbsp;·&nbsp; [Methodology + baseline results →](https://github.com/sulmusic2-star/groundtruth-geo#readme)

---

## Lasting Ground — a live answer engine for public records

[lastingground.com](https://lastingground.com) &nbsp;·&nbsp; [`lasting-ground-showcase`](https://github.com/sulmusic2-star/lasting-ground-showcase)

Type any U.S. property address. In seconds, get source-cited public-records answers, assembled live from a dozen-plus official government systems and stamped with the source and date for every line. Available in every U.S. state and Washington, DC on a nationwide FEMA-flood baseline; covered states add their own official public layers, including local building permits and parcel-level zoning where towns publish them.

[![The Lasting Ground answer engine resolving an address into source-cited answers](https://raw.githubusercontent.com/sulmusic2-star/lasting-ground-showcase/main/docs/assets/live-answers.png)](https://lastingground.com)

- A live, **paid** product I designed and operate solo: ~200 backend services (Python / FastAPI), live geospatial queries, a serverless edge front end with Stripe.
- **Deterministic by design.** The compliance-critical answers never run through a language model, so they stay reproducible and traceable to an official source.
- I use AI agents to build and run it; the architecture and the judgment are mine.

[See it live →](https://lastingground.com) &nbsp;·&nbsp; [Case study →](https://github.com/sulmusic2-star/lasting-ground-showcase/blob/main/docs/case-study.md)

---

## SquadBrain — live on the iOS App Store

[App Store](https://apps.apple.com/us/app/squadbrain/id6756122317) &nbsp;·&nbsp; [`squadbrain-showcase`](https://github.com/sulmusic2-star/squadbrain-showcase)

A mobile sports-learning game built around roster memory. React Native, Expo, TypeScript, and Firebase, with ELO-style ranking, matchmaking, and server-validated results.

- Product logic extracted into 7 typed modules with **25 tests at 98.3% line coverage** in CI.
- Shipped end to end: App Store submission, screenshot pack, published legal and privacy pages.

[📱 App Store →](https://apps.apple.com/us/app/squadbrain/id6756122317) &nbsp;·&nbsp; [Case study →](https://github.com/sulmusic2-star/squadbrain-showcase/blob/main/docs/case-study.md)

---

## How I work

I treat Claude Code and OpenAI Codex as a small engineering team: one agent builds, another acts as a review and promotion gate, and nothing ships without passing verification against real sources and tests. The judgment is mine — architecture, what to trust, and where a model belongs versus where it doesn't.

I wrote that operating model up, with a runnable eval harness, an Agent Skill, and an MCP server, in [`agentic-engineering`](https://github.com/sulmusic2-star/agentic-engineering). (A third production app is private.)

---

## Stack

- **AI & agents** — Claude Code, OpenAI Codex, MCP, agent skills, eval harnesses, multi-agent orchestration
- **Backend & data** — Python, FastAPI, REST API design, ETL, GIS / geospatial (ArcGIS REST), real-time multi-source querying, edge caching
- **Web & payments** — Cloudflare Pages / Functions, Stripe, Google Places, CSP and security headers
- **Mobile** — React Native, Expo, TypeScript, Firebase (Auth / Firestore / Cloud Functions), Zustand
- **Practice** — Git, GitHub Actions CI, pytest + Vitest, coverage, ADRs, verify-before-ship

---

[hello@lastingground.com](mailto:hello@lastingground.com) &nbsp;·&nbsp; [Portfolio](https://sulmusic2-star.github.io/)
