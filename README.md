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

> **Currently building:** expanding Lasting Ground's flood-insurance and parcel-zoning coverage across Massachusetts, and [`agentic-engineering`](https://github.com/sulmusic2-star/agentic-engineering) — how I ship and operate production software with AI agents.

---

## Lasting Ground — a live answer engine for public records

[lastingground.com](https://lastingground.com) &nbsp;·&nbsp; [`lasting-ground-showcase`](https://github.com/sulmusic2-star/lasting-ground-showcase)

Type a Massachusetts address. In seconds, get source-cited answers on flood, zoning, and insurance, assembled live from a dozen-plus official government systems and stamped with the source and date for every line.

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
