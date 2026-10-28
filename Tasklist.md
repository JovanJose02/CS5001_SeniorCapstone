# Tasklist.md

Roost, a verified student sublease marketplace for UC. Team: Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja.

**Version 2.0 (2026-10-28): re-baselined to the Roost prototype** ([roost-uc-sublease](https://github.com/trivinity/roost-uc-sublease), commit `71d351b`). The A8 plan (v1.0, 2026-10-28) assumed a custom backend built from Nov 2. Most of the product now exists on Supabase and Vercel, so each original task below carries its status, and the remaining work is in T19 to T27. The A8 baseline (dates, PERT hours, effort matrix, risk register) stays in [Planning/](Planning/) and [A8_Task_List_Milestones_Timeline_Effort.pdf](A8_Task_List_Milestones_Timeline_Effort.pdf) as the historical record. Requirement IDs refer to [Requirements_Document.md](Requirements_Document.md) v2.0. Owners marked † are proposed; confirm them at the next team meeting.

## 1. Original tasks (A8) and their status

| ID | Task (A8 wording, shortened) | Owner | Status in v2.0 |
|---|---|---|---|
| T1 | Project skeleton, CI pipeline, G2 configuration, E3 migrations | Jovan | **Done differently**: Next.js app plus Supabase migrations 001 to 007. CI is still missing (moved to T25). |
| T2 | Choose the E1 email provider: free-tier limit, webhook signing, idempotency | Danvanth | **Superseded**: Supabase Auth sends the email. Custom SMTP is T19. |
| T3 | C1 wireframes and accessibility checklist | Mohamed | **Partly superseded**: the UI is built. The accessibility checklist moves into T17. |
| T4 | Fair Housing phrase list v1, including Ohio R.C. 4112 classes | Jovan | **Open** (REQ-05, GQ-02). Target M4, 2026-12-04. |
| T5 | G3 logging, audit and /healthz | Mohamed | **Superseded**: platform logs. The staff audit is part of T23; uptime is part of T26. |
| T6 | G1 authentication middleware and signed session token | Danvanth | **Done**: Supabase JWT, RLS, `requireUser()`. |
| T7 | C2 identity: UC login links, 24 h expiry, rate limits | Danvanth | **Done**: link sign-in and the domain trigger. Expiry and limits are verified in T19. |
| T8 | C4 screen() with unit tests per phrase category | Jovan | **Open**, re-hosted as a database trigger (TS §3.6). Target M6, 2027-02-05. |
| T9 | C3 listing create, validate, hold, publish, review | Jovan | **Done** except hold and review (T8, T23). |
| T10 | C3 outbox relay and C5 date-coverage search | Jovan | **Superseded**: no outbox; filtering and ranking run in the browser. Done. |
| T11 | C8 notification queue, retries, webhook, suppression | Danvanth | **Withdrawn**: no notification service; sign-in email is in T19. |
| T12 | C1 screens: sign-in, create listing, search | Mohamed | **Done.** |
| T13 | C6 messaging threads, messages, alert limits | Mohamed | **Done**: Realtime chat, contact sharing, 30-day deletion. |
| T14 | C7 approval proposals, decisions, reminder job | Danvanth | **Withdrawn** with US-03 (RD v2.0). |
| T15 | C1 screens: messages, approvals, review queue | Mohamed | **Messages done**; approvals withdrawn; the review screen is T23. |
| T16 | End-to-end tests of timing budgets and error paths | Danvanth | **Re-scoped** into T25. |
| T17 | US-04 accessibility: axe-core in CI plus an NVDA and VoiceOver pass | Mohamed | **Open** (NFR-01). Target M8, 2027-03-12. |
| T18 | Five-student user test, results, user guide | Jovan | **Open** (NFR-10); now the class test. Target M9, 2027-03-26. |

## 2. New tasks (from roost `docs/CHECKLIST.md`, "Next" and "Hardening")

| ID | Task | Requirements | Owner | Target |
|---|---|---|---|---|
| T19 | Set up custom SMTP in Supabase, raise the Auth sign-up and sign-in limits, confirm link expiry, and test delivery to a real `@mail.uc.edu` inbox (not junk) | NFR-09, CON-08, REQ-02 | Danvanth † | M2, 2026-11-13 |
| T20 | Move the phone app onto Supabase: session in AsyncStorage, the shared data layer, photo upload | REQ-25, REQ-08 | Mohamed † | M6, 2027-02-05 |
| T21 | Replace the sample Metro bus stops with SORTA GTFS data; ask UC Parking & Transportation for the official shuttle file | REQ-18, GQ-17 | Jovan † | 2027-01-29 |
| T22 | Bot protection: Cloudflare Turnstile CAPTCHA on sign-in, and rate limits on posting and messaging | NFR-05, CON-08 | Danvanth † | M6, 2027-02-05 |
| T23 | Staff screen for the report queue and held listings, with release or remove and an audit (who, when) | REQ-09, REQ-23 | Danvanth † | M7, 2027-02-26 |
| T24 | Key and account hardening: separate restricted browser Maps key, Places key restricted with a quota and budget alert, retire the review account, make the repo private | NFR-12, CON-09 | Danvanth † | M2, 2026-11-13 |
| T25 | CI and automated tests: GitHub Actions (lint, build), `rls-checks.sql`, Vitest for ranking, distance and fee math, Playwright for the AC-01 and AC-03 criteria | NFR-03, NFR-06, all TC-0nn | Mohamed † | M8, 2027-03-12 |
| T26 | Launch readiness: privacy policy and terms, Supabase Pro, uptime monitor, Storage photo cleanup when a listing is deleted | NFR-11, CON-01 | Jovan † | M10, 2027-04-09 |
| T27 | LLM suggested questions with a daily spending cap, after the advisor answers GQ-15 | REQ-29 | Team (after GQ-15) | Could; after M8 |

**Load per member (open work):** Jovan: T4, T8, T18, T21, T26. Danvanth: T19, T22, T23, T24. Mohamed: T17, T20, T25. Re-balance at M5 (2027-01-15) using real hours, as A8 §4 describes.

## 3. Risk register changes since A8

| ID | Change |
|---|---|
| RK1 | Still open: UC Mail may junk sign-in emails. Mitigation is now T19 (custom SMTP, then SPF and DKIM once a domain exists). |
| RK4 | Changed: the Render sleep risk is gone. New form: Supabase Free pauses after about 7 idle days. Mitigation: Supabase Pro before launch (T26). |
| RK6 | Closed: manager approval was withdrawn. |
| RK7 | Still open: the phrase list may miss phrases or over-flag (T4, T8). |
| RK8 | Changed: web and phone can drift apart. Mitigation: `npm run sync` from `uc-sublease/lib`, and T20 shares the Supabase data layer. |
| RK11 | New: the Google Maps key is unrestricted and visible in the page (deliberate for the demo). Mitigation: T24 plus a daily quota cap. |
| RK12 | New: until T19, only team members can receive sign-in links, which blocks the class test. Mitigation: T19 is first in priority. |
