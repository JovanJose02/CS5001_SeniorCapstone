# Requirements Document

| Item | Detail |
|---|---|
| Project | Roost, a verified student sublease marketplace for UC |
| Course | CS5001 Senior Design I, Assignment 9 (Week 9) |
| Team members | Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja |
| Document version | 2.0 (2026-10-28) |
| Companion document | [Technical_Specification.md](Technical_Specification.md) v2.0, which traces to this version |
| Prototype | [roost-uc-sublease](https://github.com/trivinity/roost-uc-sublease) (commit `71d351b`, 2026-10-26); live at https://roost-uc-sublease.vercel.app |

---

## 1. Version and Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | 2026-09 (Week 4) | Baseline: US-01 to US-05, UC-01, UC-02, AC-01.1 to AC-02.2 ([User_Stories.md](User_Stories.md) v1.0). | Team |
| 0.2 | 2026-10-14 (Week 7) | D2 Part 4 numbers NFR-01 to NFR-07; every story is Must. | Team |
| 1.0 | 2026-10-28 | Consolidated D0, D1, D2 and A8 into REQ-01 to REQ-16, NFR-01 to NFR-11 and CON-01 to CON-08. NFR-07 withdrawn (it became CON-01). Not submitted. | Jovan Jose Asker Fredy |
| 2.0 | 2026-10-28 | **Realigned to the Roost prototype and the advisor meetings** (Technical Specification §8). REQ-11 to REQ-14 withdrawn: property-manager approval was replaced by landlord consent (REQ-20). REQ-01 to REQ-04, REQ-06, REQ-07, REQ-10, REQ-15, REQ-16 and NFR-02, NFR-03, NFR-05, NFR-06, NFR-08, NFR-09, NFR-11 restated to match the built behavior. Added REQ-17 to REQ-29, NFR-12, CON-09. REQ-05 and NFR-04 (Fair Housing screening) are kept as requirements that are not built yet. User_Stories moves to v2.0. | Jovan Jose Asker Fredy |
| 2.1 | _pending_ | Edits from the advisor review of these drafts. | _TBD_ |

**ID rules.** IDs are never renumbered or reused. A dropped requirement stays in its table marked WITHDRAWN, and the change is logged above. Story IDs (US, UC, AC) come from User_Stories.md v2.0.

## 2. Purpose and Scope

**Purpose.** This document states what Roost must do and for whom. Each requirement is a unit that the Week 10 test plan verifies. Each traces back to a user story and forward to a design element and a test case ([Technical_Specification.md](Technical_Specification.md) §6).

**Product goal.** Help UC students, faculty and staff fill or find term-length subleases safely. Only people with a UC email can use Roost. Listings are filtered by whole-term dates and distance from campus, and ranked by roommate fit. Subletting needs the landlord's consent, and contact details stay private until shared.

**In scope for release 1.0** (class test in spring, demo Apr 16, 2027):

- The web app and the Expo phone app.
- Sign-in by an emailed link to a UC address.
- Posting listings with photos, landlord consent and the sublet-fee split.
- Swipe, list and map browsing, with date, distance, rent, bedroom and furnished filters.
- Roommate-fit ranking; nearest shuttle and bus stop; property-company Google rating.
- Saved listings and side-by-side compare.
- Real-time chat with opt-in contact sharing and 30-day deletion.
- Reporting a listing.
- Fair Housing screening of listings.

**Out of scope:** see the Won't list (§7.3).

## 3. Stakeholders and User Goals (Week 4, revised v2.0)

| Category | Stakeholder | User goal | Stories |
|---|---|---|---|
| Primary | UC student leaving for a co-op (host) | Fill an empty room fast with someone trustworthy | US-01, US-08 |
| Primary | Student relocating for one term (seeker) | Housing that covers the whole term, close to campus, with compatible roommates | US-02, US-06, US-07, US-10 |
| Primary | UC faculty, staff, grad students (`@uc.edu`) | The same marketplace for short stays | US-01 |
| Secondary | Property manager / landlord | Subletting only with their consent | US-08 |
| Secondary | Parent or guarantor | The other party is a real UC person | US-01 |
| Hidden (accessibility) | Screen-reader user | Search and contact without sighted help | US-04 |
| Hidden (compliance) | Fair Housing reviewer | No discriminatory preference language published | US-05, US-09 |
| Hidden (downstream) | UC Mail; Google Maps Platform; OpenStreetMap | Well-formed, rate-limited email; use within their terms | NFR-05, CON-08, CON-09 |

## 4. Glossary

Each term is defined once here and has this meaning everywhere in both documents.

| Term | Definition |
|---|---|
| Host (subleaser) | A signed-in user who posts a listing. "Owner" in a requirement means the host of that listing. |
| Seeker (sublessee) | A signed-in user looking for a sublease, who starts a chat with a host. |
| UC email | An address ending exactly in `@mail.uc.edu` or `@uc.edu`. |
| Allowlist | The `email_allowlist` table of non-UC addresses that staff let in (advisor, testers). The API cannot read it. |
| Review account | `reviewer@roost-demo.test`, an allowlisted account that signs in with a password for the advisor. To be retired after review. |
| Sign-in link | A one-time link that Supabase Auth emails to the address. It is used for both sign-up and sign-in. |
| Signed-in user | A request carrying a valid Supabase session token (JWT). Anonymous requests are refused by row-level security. |
| Row-level security (RLS) | Postgres rules on every table that decide which rows each signed-in user may read or write. |
| Listing | One offer for a room or a whole unit. Its status is active, rented or removed. Sample listings (`is_sample`) are made-up demo data, labelled "Sample". |
| Landlord consent | The host's statement that the landlord allows subletting. A database check requires it on every listing. |
| Transfer type | Sublease, assignment or re-let. |
| Sublet fee / fee split | The landlord's fee for subletting, and the percentage (0 to 100) the host covers. |
| Whole-range match | A listing matches dates [from, to] when its start ≤ from and its end ≥ to. Overlap alone is not a match. |
| Distance | Straight-line miles from the UC campus center (39.1329, -84.5150) to the listing's coordinates. |
| Roommate preferences | Six 4-to-5-level scales (cleanliness, noise, hanging out at home, overnight guests, sleep schedule, approachability) plus smoke-free and cat/dog checkboxes. Users rate themselves; room listings carry the household's ratings. |
| Fit score | 0 to 100% match between a seeker's preferences and a household. "Poor fit" is below 55%. Whole units rank as 75. |
| Shortlist | A user's saved listings. Compare shows 2 or 3 of them side by side. |
| Thread | A chat between one seeker and the host of one listing. |
| Contact sharing | Pressing Share in a thread, which lets the other participant read your email. |
| Report | A user's 3 to 200 character complaint about a listing. Staff act on reports. |
| Flagged phrase | Text that matches the Fair Housing phrase list. A listing with one is held for review (planned). |
| Freshness | Days since the host last confirmed "still available". After 10 days the listing is labelled "may be taken". |
| Cn, Gn, En, In | Component, glue module, external system and interface IDs from D0 to D2. TS §2 maps each to the prototype. |
| MoSCoW | Must (the release fails without it), Should (important, but the release works without it), Could (only if time remains), Won't (excluded from this release). |

## 5. Functional Requirements

Verification: **T** = automated test, **D** = demonstration, **I** = inspection, **A** = analysis. "Built" = present in the prototype at commit `71d351b`.

| ID | Requirement | Priority | Source story | Verification |
|---|---|---|---|---|
| REQ-01 | The system shall create an account only for a UC email or an allowlisted address. It shall reject any other address before an email is sent, with "Only UC email addresses can join Roost". | Must | US-01; AC-01.2 | T (rls-checks, auth API) |
| REQ-02 | The system shall sign a user in only through a one-time emailed link (or the password of the review account). An expired or already used link shall create no session. | Must | US-01; AC-01.2 | T |
| REQ-03 | The system shall refuse every read or write of listings, profiles, chats, saved listings and reports from an anonymous request, and shall refuse the three API routes without a valid session (401). | Must | US-01 | T |
| REQ-04 | The system shall reject a listing whose end date is not after its start date, whose rent is outside $1 to $20,000 per month, whose title is outside 3 to 120 characters, that has more than 8 photos, or that lacks landlord consent. Nothing shall be written. | Must | AC-01.4 | T |
| REQ-05 | The system shall screen every listing's title and description against the versioned Fair Housing phrase list before it becomes active. A listing with at least one flagged phrase shall be held (not active), the host shown each flagged phrase, and the listing return 0 results for other users. | Must | US-05; AC-01.3 | T |
| REQ-06 | The system shall show a valid listing to other signed-in users within 60 s of a successful post. | Must | US-01; AC-01.1 | T (timed) |
| REQ-07 | The system shall show only active listings that are a whole-range match for the chosen dates, and shall offer Spring, Summer and Fall term presets. | Must | US-02; AC-03.1 | T |
| REQ-08 | The system shall let a signed-in seeker start one thread per listing with the host of an active listing that is not their own. It shall deliver 1 to 2,000 character messages to the other participant in real time, and only the two participants may read the thread. | Must | US-01; US-04 | T |
| REQ-09 | Only staff shall release or remove a held listing, and each decision shall be recorded with who and when. | Should | US-05 | T |
| REQ-10 | The system shall show the host their own listings, whatever the status, and let them re-confirm "still available" or mark a listing rented. | Should | US-01 | T |
| REQ-11 | WITHDRAWN (v2.0): owner proposes a sublessee for manager approval. Replaced by REQ-20. | — | (US-03, withdrawn) | — |
| REQ-12 | WITHDRAWN (v2.0): manager approves or rejects. Replaced by REQ-20. | — | (US-03) | — |
| REQ-13 | WITHDRAWN (v2.0): reminder after 5 business days. | — | (AC-02.2) | — |
| REQ-14 | WITHDRAWN (v2.0): manager emailed when a listing is published. | — | (UC-01 step 10, v1) | — |
| REQ-15 | The system shall show an unread-message count that updates in real time. There are no email alerts for messages this release. | Could | US-01 | T |
| REQ-16 | The system shall filter by a rent range chosen between $300 and $2,000, by bedrooms (1, 2, 3, 4+) and by furnished. | Could | US-02 | T |
| REQ-17 | The system shall compute each listing's distance from its geocoded address (it is never typed in) and filter by 1, 3, 5, 10 or 20 miles, or any distance. | Should | US-02; US-07 | T |
| REQ-18 | The system shall show each listing's nearest UC shuttle stop and Metro bus stop with their distance. Tapping a distance shall open a map of the stop, the listing and campus. | Could | US-07 | T + D |
| REQ-19 | The system shall collect roommate preferences after the first sign-in (editable later), rank listings by fit score, and hide poor fits until Show all, displaying how many are hidden. | Should | US-06; AC-03.2 | T |
| REQ-20 | The system shall require landlord consent on every listing (a database check). After consent it shall collect the sublet fee ($0 to $20,000) and the host's share (0 to 100%), and show the dollar split on the listing and in compare. | Must | US-08 | T |
| REQ-21 | The system shall reveal a participant's email to the other participant only after that participant presses Share. Each share shall post a system message that users cannot forge. | Should | US-11; AC-03.3 | T |
| REQ-22 | The system shall delete chat messages 30 days after they are sent (nightly, 03:17 UTC) and say so in the chat screen. | Should | US-11; AC-03.4 | T |
| REQ-23 | The system shall let a signed-in user report a listing once, with a 3 to 200 character reason, and let staff remove the listing (status "removed"). | Should | US-09; AC-03.5 | T + I |
| REQ-24 | The system shall let a user save listings and compare 2 or 3 side by side, including rent, fees, distance and fit. | Could | US-10 | T |
| REQ-25 | The system shall accept up to 8 photos per listing, compress each to a 1,600 px long side plus a 480 px thumbnail before upload, and store them only in the host's own folder. | Should | US-08 | T |
| REQ-26 | The system shall present listings as a swipe deck (drag, buttons or arrow keys, with undo), as a list, and as a map, all sharing one set of filters. | Could | US-02 | D |
| REQ-27 | The system shall show the live Google star rating and review count of a listing's property company, fetched when the listing is viewed and never stored. | Could | US-02 | T |
| REQ-28 | The system shall label a listing "may be taken" when its host has not confirmed it as available for more than 10 days. | Could | US-02 | T |
| REQ-29 | The system shall offer suggested questions to ask a host, generated by a low-cost LLM with a daily spending cap. | Could | US-04; US-11 | D |

## 6. Non-Functional Requirements

| ID | Type | Requirement | Priority | Source | Verification |
|---|---|---|---|---|---|
| NFR-01 | Usability (accessibility) | Every route shall meet WCAG 2.1 AA with 0 serious or critical axe-core violations. Testers using NVDA and VoiceOver shall each complete search and message by keyboard only. Motion shall respect `prefers-reduced-motion`. | Must | US-04 | T (axe-core) + D |
| NFR-02 | Security (privacy) | No API response shall contain another user's email address unless that user shared it in the thread (REQ-21). A user shall read only their own profile, saved listings and reports. | Must | US-11; CON-02 | T (rls-checks) |
| NFR-03 | Security (access control) | Every table shall have RLS, and anonymous requests to every table, chat function and storage write shall be refused. All scripted RLS checks (28 at commit `71d351b`) shall pass on each release. | Must | US-01 | T |
| NFR-04 | Reliability (fail-closed) | 100% of listings posted while screening is unavailable or errors shall be held or rejected, and never made active. | Must | US-05; CON-03 | T (fault injection) |
| NFR-05 | Security (abuse) | Address lookups shall be limited to 30 per user per minute, company searches to 20 and ratings to 60 (429 beyond). A host shall have at most 20 active listings. Sign-up and sign-in email shall stay within the Supabase Auth rate limit, with CAPTCHA before the class announcement. | Should | CON-08 | T |
| NFR-06 | Reliability (integrity) | Host names, chat names and listing titles shall be set by database triggers, never taken from the client. A failed insert shall leave no partial thread, message or listing row. | Should | US-01 | T |
| NFR-07 | WITHDRAWN (v1.0) | The budget requirement is a constraint; see CON-01. | — | — | — |
| NFR-08 | Performance (load) | On a mid-range phone over 4G, Discover shall show its first card with Largest Contentful Paint ≤ 2.5 s at p75, and applying a filter shall update the results within 200 ms, with 200 active listings. | Should | US-02 | T (Lighthouse mobile) |
| NFR-09 | Performance (sign-in email) | 95% of sign-in emails shall arrive in a `@mail.uc.edu` inbox (not junk) within 60 s of the request, through custom SMTP. | Should | US-01 | T (inbox test) |
| NFR-10 | Usability (task) | At least 4 of 5 first-time UC testers shall, without help, find a listing that covers given dates and message its host within 3 minutes. | Should | US-02; US-04 | D (class test) |
| NFR-11 | Reliability (availability) | The live site shall return 200 on ≥ 99% of 5-minute checks over the 7 days before the class test, on a Supabase plan that does not pause when idle. | Should | US-01 | T (uptime monitor) |
| NFR-12 | Security (secrets) | The shipped JavaScript shall contain no Supabase secret or service-role key and no Google Places key. Any browser Maps key shall be restricted to the site's address and the Maps JavaScript API. | Should | CON-09 | I (bundle scan) |

## 7. MoSCoW Summary

There are 36 active requirements: **13 Must (36%)**, 15 Should, 8 Could; 4 REQs and 1 NFR are withdrawn. The Must set is the smallest release that still serves every stakeholder group:

- Only UC people can get in.
- A host can post a valid, consented, screened listing.
- A seeker can find it by dates and message the host privately.
- The whole path works with a screen reader.

### 7.1 Must
REQ-01, REQ-02, REQ-03 (UC-only access) · REQ-04, REQ-05, REQ-06, REQ-20 (valid, screened, consented listings reach users) · REQ-07 (whole-range date match) · REQ-08 (private real-time chat) · NFR-01 (accessibility) · NFR-02, NFR-03 (privacy, access control) · NFR-04 (never publish unscreened).

REQ-05, NFR-04 and NFR-01 are Must but **not built yet**. They are the gap between the prototype and release 1.0 (Tasklist T4, T8, T17).

### 7.2 Should and Could
**Should:** REQ-09, REQ-10, REQ-17, REQ-19, REQ-21, REQ-22, REQ-23, REQ-25, NFR-05, NFR-06, NFR-08, NFR-09, NFR-10, NFR-11, NFR-12.
**Could:** REQ-15, REQ-16, REQ-18, REQ-24, REQ-26, REQ-27, REQ-28, REQ-29.

Distance (REQ-17) and roommate fit (REQ-19) are Should, not Must: the advisor ranked them as first priorities, but a student can still find housing by dates without them. The swipe deck (REQ-26) is Could because the list view (REQ-07) already serves US-02.

### 7.3 Won't (this release)

These items are written down so they cannot creep back in. Reopening one needs a story and a change-log entry.

| Won't | Why |
|---|---|
| Property-manager approval workflow and reminders (REQ-11 to REQ-14) | Team decision: landlord consent (REQ-20), requested by the advisor, covers it; the lease already gives the landlord control. |
| End-to-end encrypted chat | Advisor decision 2026-10-25: TLS in transit, AES-256 at rest, 30-day retention. E2EE would block review of reported chats and LLM suggestions. |
| UC single sign-on | Needs UC IT approval (CON-06); last on the checklist. |
| Payments, escrow, deposits, lease e-signature | Out of scope by design; legal and financial exposure. |
| Filters on protected characteristics | Fair Housing (CON-03). |
| Publishing to the App Store or Google Play | The phone app is tested through Expo Go only. |
| Live shuttle arrivals | Needs UC's TripShot data feed. |
| Google review text (only the rating and count) | Per-review attribution and higher cost (CON-09). |
| Self-service landlord or manager accounts | No story; landlords are not users this release. |

## 8. Inherited Constraints

CON-01 to CON-05 come from the Week 3 constraint areas as D0 Part 6 records them. CON-06 to CON-08 come from the D0 decision log and the A8 plan. CON-09 is new in v2.0. TS §5 states what each one rules out or forces.

| ID | Area | Constraint | Source |
|---|---|---|---|
| CON-01 | Economic | $0 per month during development (free tiers). At launch, no more than Supabase Pro (about $25 per month). Google APIs capped by a daily quota and a budget alert. | Week 3; D0 Part 6; CHECKLIST (v2.0 restated; was about $7) |
| CON-02 | Security / privacy | UC email addresses are not exposed to other users without consent; each user reaches only the rows the rules allow. | Week 3; D0 Part 6 |
| CON-03 | Legal | The Fair Housing Act (42 U.S.C. §3604(c)) and Ohio R.C. 4112 forbid discriminatory preference language in listings and in roommate wording. | Week 3; US-05; advisor prep 2026-10-21 Q6 |
| CON-04 | Social / ethical | Usable with assistive technology (WCAG 2.1 AA). | Week 3; US-04 |
| CON-05 | Hosting | Managed services only (Vercel, Supabase), with no servers for the team to patch. | Week 3; D0 Part 6 |
| CON-06 | Identity | UC SSO is not available without IT approval. Eligibility is proven by owning a UC mailbox. | D0 D-02; CHECKLIST |
| CON-07 | Team / schedule | Three students, about 10 to 14 h per week, release by the Apr 16, 2027 expo. | A8 plan |
| CON-08 | Downstream | UC Mail must receive authenticated email. Supabase's built-in sender only reaches the project team, so custom SMTP is required. | Week 4 hidden stakeholder; SUPABASE.md |
| CON-09 | Third-party terms | Google Places: store only Place IDs, show Google attribution, no caching. OpenStreetMap Nominatim: at most 1 request per second, with an identifying User-Agent. | GOOGLE_REVIEWS.md (new v2.0) |

## 9. Assumptions and Open Questions

Owners marked † are proposed; the team confirms them at the next meeting.

| ID | Assumption or question | Owner | Due |
|---|---|---|---|
| A-01 | Campus-scale demand: low thousands of users and a few hundred active listings per term. NFR-08 is sized on this. | Jovan | Recheck at M8 (2027-03-12) |
| A-02 | Custom SMTP (a Gmail app password, about 500 emails per day) is enough for the class test until a domain exists. | Danvanth † | 2026-11-13 |
| A-03 | Straight-line distance is acceptable for release 1.0. | Jovan | GQ-11 |
| GQ-02 | Phrase list v1 content, and the Ohio protected classes (ancestry, military status). | Jovan | M4 (2026-12-04) |
| GQ-03 | (Closed v2.0.) Listings can now leave active: rented (host) or removed (staff). | — | — |
| GQ-04 | (Closed v2.0.) Manager approval withdrawn. | — | — |
| GQ-05 | (Closed v2.0.) The email provider is Supabase Auth with custom SMTP; setup is still open (T19). | — | — |
| GQ-09 | CON-01 to CON-05 come from D0's summary of the Week 3 essay; confirm against the essay. The budget change in CON-01 needs advisor agreement. | Jovan | 2026-11-04 |
| GQ-10 | The TC-### IDs in the TS §6 matrix are reserved; the Week 10 test plan keeps them. | Mohamed | Week 10 |
| GQ-11 | Distance: straight-line (current) or driving/transit time? Maximum radius? | Advisor | Next meeting |
| GQ-12 | Roommate categories and wording, the fairness check (CON-03), who sees a user's ratings, and whether hosts state preferences. | Advisor; Jovan | Next meeting |
| GQ-13 | Who at UC (IT security, General Counsel) sets the chat-retention rule and the student-data policy? | Advisor | 2026-11-13 |
| GQ-14 | Landlord consent: is a checkbox enough, or is proof needed (a lease clause upload)? | Advisor | Next meeting |
| GQ-15 | LLM suggestions (REQ-29): what text may be sent to the provider, and what is the monthly cap? | Advisor | Before T27 |
| GQ-16 | Hide listings that are not re-confirmed after N days? | Team | 2026-11-13 |
| GQ-17 | Metro (SORTA) GTFS stops to replace the sample bus stops. | Jovan † | 2027-01-15 |
| GQ-18 | The default rent filter ($300 to $2,000) hides listings the database accepts (rent up to $20,000). Should the top of the slider mean "no limit"? | Mohamed † | 2026-11-13 |
