# Technical Specification

| Item | Detail |
|---|---|
| Project | Roost, a verified student sublease marketplace for UC |
| Course | CS5001 Senior Design I, Assignment 9 (Week 9) |
| Team members | Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja |
| Document version | 2.0 (2026-10-28) |
| Traces to | [Requirements_Document.md](Requirements_Document.md) **v2.0 (2026-10-28)**. All REQ, NFR, CON and glossary terms have the meanings given there. |
| Describes | the Roost prototype, [roost-uc-sublease](https://github.com/trivinity/roost-uc-sublease) commit `71d351b` (2026-10-26), plus the designed-but-unbuilt items marked **Designed**. |

---

## 1. Version and Change Log

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | 2026-10-28 | First issue, consolidated from D0, D1 and D2 against RD v1.0 (Node/Express backend, outbox, Render). Not submitted. | Jovan Jose Asker Fredy |
| 2.0 | 2026-10-28 | Rewritten to describe the prototype that the team built and the advisor reviewed: Next.js on Vercel, Supabase (Auth, Postgres with RLS, Realtime, Storage, pg_cron), an Expo phone app. Traces to RD v2.0. The D0 to D2 components are mapped to the prototype in §2.1. Fair Housing screening is re-hosted from the C4 module to a database trigger (§3.6). All design changes since the Week 7 review are logged in §7. | Jovan Jose Asker Fredy |
| 2.1 | _pending_ | Edits from the advisor review of these drafts (§8). | _TBD_ |

## 2. Architecture Summary

Roost is a **client-server web application on a backend-as-a-service**. There is no custom application server. Components:

- **Web client:** Next.js 16 (App Router, React 19, TypeScript, Tailwind), hosted on **Vercel**. It talks directly to **Supabase** with the public publishable key and the user's session token.
- **Supabase** holds all state and enforces all rules inside the database:
    - **Auth**: emailed sign-in links, and a trigger that rejects non-UC addresses.
    - **Postgres**: 8 tables, each with **row-level security**, plus triggers that fill in names, cap listings and block self-messaging.
    - **Realtime**: chat delivery.
    - **Storage**: the `listing-photos` bucket.
    - **pg_cron**: the nightly 30-day chat deletion.
- **Three Next.js API routes** run on Vercel serverless functions. They keep third-party keys and rate limits off the client: `/api/geocode` calls OpenStreetMap Nominatim; `/api/places/search` and `/api/places/rating` call Google Places API (New).
- **Phone app:** an Expo / React Native app that shares the web app's logic through a sync script. It still runs on local demo data; moving it onto Supabase is T20.

**Deployment model.** There is one Vercel project (root `uc-sublease/`, live at https://roost-uc-sublease.vercel.app) and one Supabase project (`roost-uc-sublease`, us-east-2, Free plan, Pro before launch). Schema changes are SQL migrations `001` to `007`, applied in order. Secrets live only in Vercel and Supabase settings (`GOOGLE_PLACES_API_KEY`, SMTP credentials); the shipped JavaScript carries only the publishable key.

**Data flow.**

- Sign-in: the browser asks Supabase Auth to email a link. The `handle_new_user` trigger rejects non-UC addresses before any email is sent and creates the profile. The link returns a JWT session.
- Reads and writes go from the browser to Supabase (PostgREST over HTTPS, with the JWT). RLS decides which rows each user sees; BEFORE INSERT triggers set server-owned fields.
- Posting: the address goes through `/api/geocode` to coordinates. Photos are compressed in the browser and uploaded to the host's own Storage folder. Then the listing row is inserted.
- Search, ranking and filtering run in the browser over the active listings RLS returns (no server search index at campus scale, A-01).
- Chat: rows are inserted into `threads` and `messages`, and Realtime pushes them to the other participant. `share_contact` and `get_contact` (SECURITY DEFINER functions) control email disclosure.

**Diagrams.** The prototype has no new diagrams. The D0 to D2 figures stay valid for the parts mapped below; they are linked, not duplicated: [D0_High_Level_Design.pdf](D0_High_Level_Design.pdf) (block diagram, Data Flows 1 to 4), [D1_Detailed_Design.pdf](D1_Detailed_Design.pdf), [D2_Detailed_Design.pdf](D2_Detailed_Design.pdf) and [D2_figures/](D2_figures/).

### 2.1 Design components mapped to the prototype

| D0/D2 element | In the prototype | Status |
|---|---|---|
| C1 Web Client | Next.js app `uc-sublease/app/*` + Expo app `roost-mobile/` | Built (web); phone on local data |
| C2 Identity, G1 Auth | Supabase Auth email link; `handle_new_user` trigger; `email_allowlist`; JWT checked by PostgREST and `requireUser()` | Built |
| C3 Listing | `listings` table, RLS, `listings_before_insert` trigger; statuses active, rented, removed | Built (no hold state yet) |
| C4 Compliance Screener | D2 Algorithm D re-hosted as a database trigger (§3.6) | Designed, not built |
| C5 Search & Match | `filterListings()` and `rankByFit()` in the browser (D1 GiST index not used) | Built |
| C6 Messaging | `threads`, `messages`, Realtime, `share_contact`, `get_contact`, `mark_thread_read` | Built |
| C7 Approval | Withdrawn; replaced by `landlord_consent` CHECK and the fee split | Withdrawn |
| C8 Notification, E1 | Supabase Auth email only (custom SMTP pending, T19); no other email | Partly built |
| G2 Configuration | Vercel/Supabase environment variables; `lib/config.ts`; migrations | Built |
| G3 Logging and audit | Supabase and Vercel platform logs; `reports` table; no staff audit log yet (T23) | Partly built |
| E3 Managed SQL | Supabase Postgres | Built |
| New: E4 Google Maps Platform, E5 OpenStreetMap | Places API (New), Maps JS; Nominatim geocoding and Leaflet tiles | Built |

## 3. Interfaces and Data Formats

### 3.1 Conventions

- **Types:** dates are ISO `yyyy-mm-dd`; timestamps are `timestamptz` (UTC); rent and fees are integer US dollars; user ids are UUIDs; listing ids are text (UUID strings).
- **Authentication:** every Supabase call carries `Authorization: Bearer <Supabase JWT>` and `apikey: <publishable key>`. Calls to the three API routes carry the same Bearer token.
- **Supabase (PostgREST) error behavior:**
    - Invalid or expired JWT: **401**.
    - An RLS-filtered SELECT returns **200 with no rows** (it never reveals that the row exists).
    - An insert or update that RLS refuses: **403**, code `42501`.
    - A CHECK violation: **400**, code `23514`.
    - A unique violation: **409**, code `23505`.
    - A trigger `raise exception`: **400**, code `P0001`, with its message.
    - The client maps each case to one message from `lib/copy.ts`.
- **API route errors:** `{"error": "<code>"}`, where the code is one of `sign_in_required` (401), `bad_id` (400), `slow_down` (429), `not_found` (404), `lookup_failed` (502) or `not_configured` (503).
- **Security headers** (`next.config.ts`): `X-Frame-Options: DENY`, `frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, a strict `Referrer-Policy`, a `Permissions-Policy` that disables camera, microphone, location and payments, and `Cross-Origin-Opener-Policy`.

### 3.2 Component boundaries

| Boundary | Inputs → outputs | Format | Protocol | Error behavior |
|---|---|---|---|---|
| User ↔ web client (I1) | Taps, swipes, keys, forms → pages, toasts, live counts | HTML, ARIA | HTTPS (browser) | Field errors shown inline from `lib/copy.ts`; motion off under reduced-motion; draft kept on the post form |
| Web client → Supabase Auth (I2) | `signInWithOtp({email})` (link); `signInWithPassword` (review account only) → session JWT | JSON | HTTPS | Non-UC address: trigger error "Only UC email addresses…", no email sent. Expired or used link: no session. Rate limit: 429 |
| Web client ↔ Supabase DB (I3 to I6, I15) | Table reads and writes, RPC → rows | JSON | PostgREST over HTTPS | §3.1 codes; RLS hides others' rows; triggers override client-set names |
| Web client ↔ Realtime | Subscribe to `messages`, `threads` → inserted rows | JSON | WebSocket (TLS) | Only rows the user may read are delivered; on reconnect the client re-fetches the thread |
| Web client → Storage | `upload(<uid>/<file>)` JPEG/WebP/PNG ≤ 2 MB → public URL | Binary | HTTPS | Another user's folder: 403; type or size refused: 400; the listing is saved without the failed photo |
| Web client → `/api/*` | Query string + Bearer → JSON (§3.3) | JSON | HTTPS GET | 401, 400, 429 (per-user, in memory), 502 upstream, 503 key missing |
| `/api/*` → E4/E5 | Nominatim search; Places Text Search; Place Details (field mask) | JSON | HTTPS | Upstream failure → `lookup_failed`; ratings never cached (`no-store`); geocode cached 24 h |
| Supabase Auth → SMTP → UC Mail (I13, I14) | Sign-in link email | RFC 5322 MIME | SMTP over TLS | Built-in sender reaches only team members until custom SMTP (T19); bounces are visible in the SMTP provider |
| pg_cron → DB | `roost-delete-old-chats` at 03:17 UTC | SQL | In-database | A failed run is logged in `cron.job_run_details`; the next night catches up |
| Phone app ↔ device store | Listings, shortlist, chats (demo) | JSON | AsyncStorage | Local only, to be replaced by the Supabase data layer (T20) |

### 3.3 Endpoint table

**Next.js API routes** (Vercel, Bearer token required):

| Method and path | Request | Success | Errors | Limit | Req |
|---|---|---|---|---|---|
| GET /api/geocode | `q` 4 to 120 chars | 200 `{results:[{label, area, lat, lng}]}` (at most 5; `[]` if q is short) | 401; 429; 200 with `error:"lookup_failed"` | 30/min/user | REQ-17, CON-09 |
| GET /api/places/search | `q` 3 to 80 chars | 200 `{results:[{id, name, address}]}` | 401; 429; 502; 503 | 20/min/user | REQ-27 |
| GET /api/places/rating | `id` = Place ID `[A-Za-z0-9_-]{10,200}` | 200 `{name, rating, count, url}` | 400 bad_id; 401; 404; 429; 502; 503 | 60/min/user | REQ-27, CON-09 |

**Supabase data API** (PostgREST `/rest/v1`, Bearer token required, RLS on every row):

| Operation | Who may | Request / result | Errors | Req |
|---|---|---|---|---|
| SELECT listings | Signed in | Active listings, plus the caller's own in any status | 401 (anon) | REQ-03, REQ-07, REQ-10 |
| INSERT listings | Owner = caller, not sample | Listing row (§3.5) → row; trigger sets host_name and confirmed_at | 400 (23514 checks; P0001 "20 active listings"); 403 | REQ-04, REQ-06, REQ-20 |
| UPDATE / DELETE listings | Owner | status rented, confirmed_at, fields | 403 | REQ-10 |
| SELECT, UPDATE profiles | Self only; columns display_name, prefs, prefs_asked, onboarded | prefs JSON (§3.4) | 403 for other columns | REQ-19, NFR-02 |
| SELECT, INSERT, DELETE shortlist | Self | `{user_id, listing_id}` | 409 duplicate | REQ-24 |
| INSERT threads | Seeker = caller | `{listing_id}` → thread; trigger sets host, names, shared flags | P0001 "no longer available" / "your own listing"; 409 one thread per pair | REQ-08 |
| SELECT, INSERT messages | Thread participants; `kind='user'` | `{thread_id, body 1-2000}` | 403; 400 | REQ-08, REQ-22 |
| RPC share_contact(p_thread) | Participant | Sets the caller's shared flag and posts a system message | "Chat not found." | REQ-21 |
| RPC get_contact(p_thread) | Participant | The other person's email, or null until they share | — | REQ-21, NFR-02 |
| RPC mark_thread_read(p_thread) | Participant | Updates the caller's read_at | — | REQ-15 |
| INSERT, SELECT reports | Reporter = caller | `{listing_id, reason 3-200}` | 409 one per listing; 400 | REQ-23 |
| SELECT property_groups | Signed in | 12 quick-pick companies `{name, kind, google_place_id}` | 401 | REQ-27 |
| Storage `listing-photos` | Owner folder `<uid>/` write; public read | JPEG/WebP/PNG ≤ 2 MB | 403; 400 | REQ-25 |

### 3.4 Data formats

```jsonc
// profiles.prefs and listings.household (roommate ratings; household only on room listings)
{ "cleanliness": 4, "noise": 2, "social": 2, "guests": 1, "sleep": 3, "approachability": 4,
  "smokeFree": true, "cats": false, "dogs": true }

// Listing insert (client → PostgREST); server sets id, host_name, host_detail, confirmed_at, created_at
{ "owner_id": "<auth.uid()>", "title": "Sunny room near campus", "address": "…", "area": "Clifton",
  "lat": 39.13, "lng": -84.52, "rent": 650, "utilities_included": false, "utilities_estimate": 60,
  "start_date": "2027-01-04", "end_date": "2027-04-30", "bedrooms": 3, "furnished": true,
  "unit_type": "room", "transfer_type": "sublease", "amenities": ["wifi", "laundry"],
  "sublet_fee": 150, "fee_split_pct": 50, "landlord_consent": true,
  "google_place_id": "ChIJP3LeqIezQYgRs8U5H0Yrlxo", "photos": ["<uid>/a.jpg"], "thumbs": ["<uid>/a_t.jpg"] }
```

### 3.5 Database schema (Supabase Postgres, `public` schema)

| Table | Key columns | Constraints that enforce requirements |
|---|---|---|
| profiles | id PK → auth.users, email, display_name, prefs JSONB, prefs_asked, onboarded | Created by trigger only; update limited to 4 columns; RLS self-only (NFR-02, REQ-19) |
| listings | id PK, owner_id (null = sample), is_sample, title, address, lat, lng, rent, dates, bedrooms, furnished, unit_type, transfer_type, amenities[], sublet_fee, fee_split_pct, household, landlord_consent, photos[], thumbs[], google_place_id, status, confirmed_at | CHECK end_date > start_date; rent 1 to 20000; title 3 to 120; ≤ 8 photos; `landlord_consent` must be true; status ∈ {active, rented, removed}; trigger caps 20 active per owner (REQ-04, REQ-20, NFR-05) |
| shortlist | (user_id, listing_id) PK | RLS self (REQ-24) |
| threads | id PK, listing_id, seeker_id, host_id, names, seeker_shared, host_shared, read_at × 2 | UQ (listing_id, seeker_id); no UPDATE/DELETE grant; trigger blocks inactive and own listings (REQ-08, NFR-06) |
| messages | id PK, thread_id, sender_id, kind ∈ {user, system, sample_host}, body 1 to 2000 | Insert only as self with kind 'user' in own thread; cron deletes after 30 days (REQ-22) |
| reports | id PK, listing_id, reporter_id, reason 3 to 200 | UQ (listing_id, reporter_id) (REQ-23) |
| email_allowlist | email PK | RLS on, no policies: invisible to the API (REQ-01) |
| property_groups | id PK, name, kind, google_place_id UQ | Read-only to signed-in users (REQ-27) |

### 3.6 Designed, not built: Fair Housing screening (REQ-05, REQ-09, NFR-04)

- **Algorithm:** D2 Algorithm D, unchanged: normalize, fold common substitutions, match whole words, flag mixed-script tokens.
- **Where it runs:** instead of an in-process C4 module, it runs inside the `listings` BEFORE INSERT/UPDATE trigger. It reads a new staff-only `phrase_list` table, with the version stored on the row.
- **What changes:**
    - Status gains `held`.
    - The RLS read policy already hides non-active rows from other users (AC-01.3).
    - New columns: `flagged_phrases text[]`, `reviewed_by`, `reviewed_at`.
- **Fail-closed by construction:** if the trigger errors, the insert fails and no active row can exist (NFR-04).
- **Staff release or removal** (REQ-09) goes through a staff-only RPC that writes `reviewed_by` and `reviewed_at`. Tasks T4, T8 and T23.

## 4. Technology Stack

| Layer | Choice | Justification (requirement or constraint IDs) |
|---|---|---|
| Web front end | Next.js 16.4 (App Router), React 19, TypeScript 5, Tailwind 4, shadcn button, Base UI dialog | Native elements and a reduced-motion setting: NFR-01. Thumbnails and lazy loading: NFR-08. One language for web and phone: CON-07 |
| Phone app | Expo SDK 57 / React Native, Expo Router; shared `lib/` via `npm run sync` | Most seekers browse on phones (US-02); one TypeScript codebase: CON-07; Expo Go needs no store release (§7.3 of the RD) |
| Data and rules | Supabase Postgres with RLS, CHECK constraints, triggers, SECURITY DEFINER functions | Rules are enforced server-side, so the client cannot bypass them: REQ-03, REQ-04, REQ-20, NFR-02, NFR-03, NFR-06 |
| Authentication | Supabase Auth email link plus the domain trigger; one password review account | REQ-01, REQ-02; no SSO available: CON-06 |
| Real-time | Supabase Realtime on `messages` and `threads` | REQ-08, REQ-15 |
| File storage | Supabase Storage `listing-photos` (public read, owner-folder write, 2 MB, images only); browser compression to 1,600 px and 480 px | REQ-25; keeps storage within the free tier: CON-01 |
| Scheduled jobs | pg_cron | REQ-22, with no extra service: CON-01, CON-05 |
| Server routes | Next.js route handlers on Vercel; `requireUser()`; in-memory per-user limiter | Keys stay off the client: NFR-12; abuse limits: NFR-05; third-party terms: CON-09 |
| Hosting | Vercel (Hobby) + Supabase Free, then Supabase Pro before launch | Managed only: CON-05; $0 now and about $25 per month at launch: CON-01; no idle pause: NFR-11 |
| Maps and geocoding | Leaflet + OpenStreetMap tiles (Browse map); Google Maps JS (stop map); Nominatim (geocode, cached 24 h) | REQ-17, REQ-18; no key for most maps: CON-01; 1 request per second policy: CON-09 |
| Ratings | Google Places API (New): Text Search + Place Details (rating fields only) | REQ-27; free monthly calls under CON-01; Place-ID-only storage: CON-09 |
| Email | Supabase Auth through custom SMTP (a Gmail app password for the class test, a domain sender later) | NFR-09; deliverability to UC Mail: CON-08 |
| Verification | `supabase/tests/rls-checks.sql` (28 checks, exists); planned: GitHub Actions, Vitest (ranking, distance and fee math), Playwright end-to-end, axe-core, Lighthouse, an uptime monitor | NFR-03; REQ tests TC-0nn; NFR-01, NFR-08, NFR-11 (T25) |

**Removed since v1.0** (§7): Express, Render, jose, the Postgres outbox and relay, the server search index (GiST), and the C8 notification queue.

## 5. Known Constraints

| ID | Constraint (RD §8) | Rules out | Forces |
|---|---|---|---|
| CON-01 | $0 now, about $25 per month at launch | Paid search or moderation services, a message broker, extra servers | Free tiers; client-side search; pg_cron; Google quota caps and a budget alert; Supabase Pro only at launch |
| CON-02 | Contact privacy; row-level access | Showing emails in listings or chats; client-side-only access checks | RLS on every table; `get_contact` only after Share; trigger-set names |
| CON-03 | Fair Housing Act / Ohio R.C. 4112 | Protected-characteristic filters; unscreened publishing; roommate questions that mirror protected classes | Screening trigger (§3.6); report button (REQ-23); fairness review of roommate wording (GQ-12) |
| CON-04 | WCAG 2.1 AA | Colour-only status; gestures as the only control | Buttons and arrow keys as alternatives to swiping; icon tags with text labels; reduced motion; axe-core gate (T17) |
| CON-05 | Managed services only | Self-hosted servers or SMTP | Vercel + Supabase; config in environment variables and migrations |
| CON-06 | No UC SSO | SAML/Shibboleth | UC-domain email link plus the trigger; allowlist for staff |
| CON-07 | Three students, Apr 16, 2027 | Separate native codebases; manager onboarding | Expo with shared `lib/`; the MoSCoW cut in RD §7 |
| CON-08 | Authenticated email to UC Mail | Supabase's built-in sender for real users | Custom SMTP (T19); Auth rate limits; CAPTCHA (T22) |
| CON-09 | Google and OpenStreetMap terms | Caching ratings; storing Places content other than Place IDs; unthrottled Nominatim | `no-store` rating route; Place-ID column only; server-side geocode with a User-Agent and 24 h cache |

## 6. Traceability Matrix

Status: **In progress** = built in the prototype at `71d351b`, with Week 10 verification pending. **Designed** = specified (D0 to D2 or §3.6) but not built. **Planned** = not yet designed. Test IDs are reserved for the Week 10 plan: REQ-nn → TC-0nn, NFR-nn → TC-1nn, CON-nn → TC-2nn (GQ-10).

| Req ID | Description | Design Component (D0/D1/D2) | Status | Test Case |
|---|---|---|---|---|
| REQ-01 | UC email or allowlist only, rejected before any email | D0 C2, D-02; D2 Algorithm C (EC-C2-05) → prototype `handle_new_user` trigger, `email_allowlist` | In progress | TC-001 |
| REQ-02 | One-time link sign-in; expired or used link fails | D0 I2, D-09; D2 Fig. 8 → Supabase Auth link; review-account password | In progress | TC-002 |
| REQ-03 | Anonymous requests refused | D2 G1 (I18) → RLS on all tables; `requireUser()` | In progress | TC-003 |
| REQ-04 | Invalid listing rejected, nothing written | D1 §5 POST /listings; D2 EC-C3-01 → `listings` CHECKs | In progress | TC-004 |
| REQ-05 | Screen listings; hold flagged ones | D0 C4, I7; D2 Algorithm D → §3.6 trigger | Designed (list content: T4) | TC-005 |
| REQ-06 | Listing visible to others within 60 s | D1 Algorithm B (outbox removed) → direct insert + RLS read policy | In progress | TC-006 |
| REQ-07 | Whole-range date match, term presets | D0 D-06; D1 Algorithm A → `filterListings()`, `TERMS` | In progress | TC-007 |
| REQ-08 | Private real-time chat, one thread per listing per seeker | D0 C6, I5; D2 Part 2.5, Fig. 3 → `threads`, `messages`, Realtime | In progress | TC-008 |
| REQ-09 | Staff release or remove held listings, audited | D1 §5 review endpoints; D2 R-10 → §3.6 staff RPC | Designed | TC-009 |
| REQ-10 | Host sees own listings; re-confirm or mark rented | D2 GET /listings/mine (Part 2.8) → `/mine`, RLS owner read | In progress | TC-010 |
| REQ-15 | Real-time unread count | D2 C6 read marks → `mark_thread_read`, notification bell | In progress | TC-015 |
| REQ-16 | Rent, bedroom, furnished filters | D1 Algorithm A (maxRentCents) → `filterListings()` | In progress | TC-016 |
| REQ-17 | Distance from geocoded address; mile filter | D0 C5 (search) → `/api/geocode`, `lib/geo.ts`, `DISTANCE_OPTIONS` | In progress | TC-017 |
| REQ-18 | Nearest shuttle and bus stop; stop map | D0 C1/C5 → `lib/transit.ts` (53 real shuttle stops; sample bus stops), stop-map sheet | In progress | TC-018 |
| REQ-19 | Roommate preferences; fit ranking; Show all | D0 C5 (ranking) → `lib/roommates.ts`, `rankByFit()`, MATCH_MIN 55 | In progress | TC-019 |
| REQ-20 | Landlord consent required; fee split | D0 C3 (replaces C7, D-11) → `landlord_consent` CHECK, `sublet_fee`, `fee_split_pct` | In progress | TC-020 |
| REQ-21 | Email revealed only after Share | D2 R-05, NFR-02 → `share_contact`, `get_contact` | In progress | TC-021 |
| REQ-22 | Messages deleted after 30 days | D2 C6 data model → pg_cron `roost-delete-old-chats` | In progress | TC-022 |
| REQ-23 | Report a listing once; staff remove | D2 GQ-02 (no report feature) → `reports` table, report dialog, SQL removal | In progress | TC-023 |
| REQ-24 | Save and compare 2 or 3 listings | D0 C1 → `shortlist`, compare table | In progress | TC-024 |
| REQ-25 | Up to 8 photos, compressed, owner folder | D0 C1, C3 → `lib/images.ts`, Storage policies | In progress (web) | TC-025 |
| REQ-26 | Swipe deck, list and map with shared filters | D0 C1 (D-08) → `swipe-deck.tsx`, `/list`, Leaflet map | In progress | TC-026 |
| REQ-27 | Live Google rating of the property company | D0 C1 → `/api/places/*`, `property_groups` | In progress | TC-027 |
| REQ-28 | "May be taken" after 10 days unconfirmed | D2 GQ-03 (listing lifecycle) → `confirmed_at`, `freshness()` | In progress | TC-028 |
| REQ-29 | LLM suggested questions with a spending cap | **ORPHANED**: no D0 to D2 element; design waits for the advisor's policy and cap (GQ-15), then T27 | Planned | TC-029 |
| NFR-01 | WCAG 2.1 AA, 0 axe violations, screen-reader pass | D0 I1; D2 Part 2.2 → reduced-motion support; full pass is T17 | In progress | TC-101 |
| NFR-02 | No email exposed without Share | D2 R-05, EC-G3-03 → RLS, `get_contact` | In progress | TC-102 |
| NFR-03 | RLS everywhere; anonymous refused; 28 checks pass | D2 G1 → RLS policies, `rls-checks.sql` | In progress | TC-103 |
| NFR-04 | Screening failure never publishes | D0 I7 fail-closed; D2 Fig. 7 → §3.6 trigger | Designed | TC-104 |
| NFR-05 | Lookup limits; 20-listing cap; Auth limits; CAPTCHA | D2 Algorithm C step 3 → `allow()` limits, listing trigger; CAPTCHA is T22 | In progress | TC-105 |
| NFR-06 | Server-set names; no partial rows | D2 NFR-06, R-06 → BEFORE INSERT triggers, single-statement inserts | In progress | TC-106 |
| NFR-08 | LCP ≤ 2.5 s p75; filter update ≤ 200 ms | D1 Algorithm A (complexity) → thumbnails, client-side filtering | In progress | TC-108 |
| NFR-09 | 95% of sign-in emails within 60 s, not junk | D0 E1, I13, I14 → custom SMTP (T19) | Designed | TC-109 |
| NFR-10 | 4 of 5 testers find and message within 3 min | D2 Part 2.2 screen table → class test (T18) | In progress | TC-110 |
| NFR-11 | ≥ 99% uptime over 7 days; no idle pause | D2 G3 /healthz → Vercel + Supabase Pro (T26) | Designed | TC-111 |
| NFR-12 | No secrets in the bundle; Maps key restricted | D2 G2 (secrets in environment) → server-only Places key; restricted browser key is T24 | In progress | TC-112 |
| CON-01 | $0 now, about $25 per month at launch | D0 D-01 (budget) → free tiers, Google quota caps | In progress | TC-201 (cost analysis) |
| CON-02 | Contact privacy, row-level access | D0 Part 6 → RLS, `get_contact` | In progress | TC-202 (inspection) |
| CON-03 | Fair Housing Act / Ohio R.C. 4112 | D0 C4, D-04 → §3.6, reports, wording review | Designed | TC-203 |
| CON-04 | WCAG 2.1 AA | D0 I1, D-08 → C1 alternatives to gestures | In progress | TC-204 |
| CON-05 | Managed services only | D0 E3, D-01 → Vercel + Supabase | In progress | TC-205 (inspection) |
| CON-06 | No UC SSO | D0 D-02, D-09 → email link + trigger | In progress | TC-206 |
| CON-07 | Team and schedule | A8 plan → [Tasklist.md](Tasklist.md) v2 | In progress | TC-207 (tracking) |
| CON-08 | Authenticated email to UC Mail | D0 E2, I14 → custom SMTP, CAPTCHA (T19, T22) | Designed | TC-208 |
| CON-09 | Google and OSM terms | D0 C1 (new external E4/E5) → `no-store` routes, Place-ID-only column | In progress | TC-209 (inspection) |

REQ-11 to REQ-14 and NFR-07 are withdrawn (RD v2.0) and have no rows. **Orphaned: 1 (REQ-29)**, explained above.

## 7. Design Changes Since the Week 7 Review (D2, 2026-10-14)

| Change | Why | Effect |
|---|---|---|
| Custom Node/Express modular monolith on Render → Supabase backend-as-a-service + Next.js on Vercel | Advisor meeting 1 asked to move to Supabase; rules enforced in the database cover D2's G1, C2, C3 and C6 with far less code (CON-07) | D-01, D-05 (outbox), D-03 (own JWT) superseded; §2.1 mapping |
| Property-manager approval (C7, US-03, REQ-11 to REQ-14) withdrawn | Team decision built on the advisor's meeting-1 request for landlord consent and a fee split; no real manager to test with (RK6) | REQ-20 added; UC-02, AC-02.x withdrawn |
| C4 screener not built; re-hosted as a trigger | Prototype time went to the advisor's first priorities (distance, form, preferences) | REQ-05, NFR-04 stay Must; §3.6; T4, T8 |
| Server search index (D1 GiST) → client-side filtering and fit ranking | A few hundred listings (A-01); ranking needs per-user preferences in the browser | D1 Algorithm A superseded |
| Added distance, map, stops, roommate fit, fee split, Google ratings, compare, reports, photo upload, swipe deck | Advisor meeting 1 requests | REQ-17 to REQ-28 |
| `@uc.edu` admitted, not only `@mail.uc.edu` | Advisor meeting 1: faculty, staff and grad students | REQ-01 |
| Chat privacy: TLS + at-rest encryption + 30-day deletion, no E2EE | Advisor decision 2026-10-25 | REQ-22; RD §7.3 Won't |
| Error-code rule (D2 R-08) → PostgREST codes (§3.1) | No custom API layer to apply R-08 | §3.1 |

## 8. Advisor Review Record

| Date | Form | What was discussed | Changes it produced |
|---|---|---|---|
| Meeting 1 (date: _____, before 2026-10-21) | Meeting | Replace neighborhoods with distance from UC and a map; nearest shuttle and bus stop; a fuller listing form; sublet fee after landlord consent with a split; icon amenities; property Google reviews; open to faculty, staff and grad students; roommate rating scales and fit ranking with Show all; photo compression; 30-day chats; move to Supabase; a weekly checklist | REQ-01 (`@uc.edu`), REQ-17 to REQ-20, REQ-22, REQ-24 to REQ-27; US-06 to US-08; the backend change in §7 |
| 2026-10-21 | Meeting (demo and the prep questions in roost-uc-sublease `docs/archive/`) | Demo of the prototype; backend ownership; sign-in without SSO; the chat privacy model; transit data; distance meaning; roommate wording and fairness; LLM cap; landlord-consent proof; test plan; timeline. Priorities agreed: distance search, listing form, user preferences, then encryption and image size | Priority order in RD §7.2; open questions GQ-11 to GQ-15 |
| 2026-10-22 | Written progress update (roost `docs/roost-advisor-update-2026-10-22.pdf`) | Status after the move to Supabase; the email-setup blocker; next steps 1 to 8 | Tasklist T19 to T27 |
| 2026-10-25 | Decision | Chat privacy: encryption in transit and at rest with 30-day retention is enough; no end-to-end encryption; server access limited to authorized staff | REQ-22; E2EE on the Won't list; GQ-13 narrowed to UC's retention rule |
| _____ | Review of RD v2.0 and TS v2.0 drafts (bring the §6 matrix) | _____ | _Log as v2.1_ |

Suggested agenda for the draft review: (1) Are REQ-05 and NFR-04 (screening) right as Must even though they are not built yet? (2) The CON-01 budget change ($7 → about $25 per month at launch). (3) GQ-11 to GQ-15 and GQ-18. (4) The orphaned REQ-29.
