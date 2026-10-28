# User Stories and Use Cases

**Project:** Roost, a verified student sublease marketplace for UC
**Course:** CS5001 Senior Design I, Assignment 4 (Week 4), revised Week 9 to match the Roost prototype
**Team members:** Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja
**Version:** 2.0 (2026-10-28)

---

## 0. Change Log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-09 (Week 4) | Original stories US-01 to US-05, use cases UC-01 and UC-02, acceptance criteria AC-01.1 to AC-02.2. |
| 2.0 | 2026-10-28 | Aligned with the Roost prototype ([roost-uc-sublease](https://github.com/trivinity/roost-uc-sublease)) and the advisor meetings (meeting 1, 2026-10-21, decision 2026-10-25). **US-03, UC-02, AC-02.1, AC-02.2 withdrawn**: the team replaced property-manager approval with the required landlord-consent statement and sublet-fee split that the advisor asked for in meeting 1 (US-08). US-01 now also admits faculty, staff and grad students (`@uc.edu`). US-02 adds distance from UC. US-05 is kept but not yet built. Added US-06 to US-11 for features the advisor asked for. IDs are never reused. |

---

## 1. Stakeholder Map

| Category | Stakeholder | What they need from the system |
|---|---|---|
| Primary | UC student leaving for a co-op (subleaser, "host") | Fill an empty room fast with someone trustworthy |
| Primary | Student relocating to Cincinnati for one term (sublessee, "seeker") | Housing that covers a 3 to 4 month stay, close enough to campus |
| Primary (added v2.0) | UC faculty, staff and grad students (`@uc.edu`) | The same marketplace for short stays |
| Secondary | Property manager / landlord | Subletting happens only with their consent; lease terms enforced |
| Secondary | Parent or guarantor on the lease | Assurance the replacement tenant is a real UC person |
| Hidden (accessibility) | Blind or low-vision student using a screen reader | Search and contact listings without sighted help |
| Hidden (compliance) | Fair Housing compliance reviewer | Listings and roommate questions free of discriminatory preference language |
| Hidden (downstream system) | UC Mail (Microsoft 365) and email delivery | Well-formed, rate-limited sign-in email |
| Hidden (data providers) | Google Maps Platform, OpenStreetMap | Use within their terms and rate limits |

---

## 2. User Stories

**US-01 (Primary)**
As a UC student leaving Cincinnati for a one-semester co-op,
I want only people with a UC email address to be able to see and contact me about my room,
so that I stop paying rent on an empty room and know who is living in my unit.
*(v2.0: "UC email" means `@mail.uc.edu` or `@uc.edu`.)*

**US-02 (Primary)**
As a UC student relocating to Cincinnati for a single co-op term,
I want to find subleases whose available dates cover my whole term and that are within a distance of campus I choose,
so that I do not have to sign a 12-month lease for a 4-month stay or live too far away.

**US-03 (Secondary): WITHDRAWN in v2.0**
~~As a property manager, I want to approve or reject a proposed subleaser before move-in.~~
Replaced by US-08. The lease already gives the landlord this control, and the advisor asked for a consent statement and fee split, which the team adopted instead of an in-app approval workflow.

**US-04 (Hidden: accessibility)**
As a blind student who navigates with a screen reader,
I want to search listings and send a message to a host without sighted assistance,
so that I have the same access to housing as every other student.

**US-05 (Hidden: compliance)**
As a Fair Housing compliance reviewer for the platform,
I want listings containing discriminatory preference language to be held for review before they are published,
so that the platform and its users avoid Fair Housing Act violations.
*(v2.0: not yet in the prototype; planned. Students can already report a listing, see US-09.)*

**US-06 (Primary, added v2.0)**
As a student looking for a room in a shared unit,
I want to rate my own habits and see rooms ranked by how well I would fit with the people already living there,
so that I do not end up in a household I clash with.

**US-07 (Primary, added v2.0)**
As a student without a car,
I want to see each listing's distance from campus and its nearest UC shuttle and Metro bus stop,
so that I know how I would get to class.

**US-08 (Primary + Secondary, added v2.0)**
As a subleaser,
I want to confirm that my landlord allows subletting and state how much of the sublet fee I will cover,
so that seekers know the arrangement is allowed and what it will cost them.

**US-09 (Hidden: safety, added v2.0)**
As any student using the marketplace,
I want to report a listing that looks fake, unsafe or discriminatory,
so that staff can take it down.

**US-10 (Primary, added v2.0)**
As a sublessee comparing options,
I want to save listings and compare two or three side by side,
so that I can decide on rent, fees and fit without re-opening each one.

**US-11 (Primary, added v2.0)**
As either party in a chat,
I want my email address to stay hidden until I choose to share it, and old chats to be deleted,
so that I control who can contact me outside Roost.

---

## 3. INVEST Self-Check

| Story | I | N | V | E | S | T | Notes |
|---|---|---|---|---|---|---|---|
| US-01 | Y | Y | Y | Y | Y | Y | The domain rule is testable with fixed addresses |
| US-02 | Y | Y | Y | Y | Y | Y | Date coverage and distance are testable with fixed listings |
| US-04 | Y | Y | Y | Y | Y | Y | Scoped to search + message |
| US-05 | Y | Y | Y | Y | Y | Y | Testable with a fixed phrase list |
| US-06 | Y | Y | Y | Y | Y | Y | The fit score is deterministic for fixed ratings |
| US-07 | Y | Y | Y | Y | Y | Y | Distances are testable against known coordinates |
| US-08 | Y | Y | Y | Y | Y | Y | Consent is enforced by a database check |
| US-09 | Y | Y | Y | Y | Y | Y | One report per student per listing |
| US-10 | Y | Y | Y | Y | Y | Y | Independent of messaging |
| US-11 | Y | Y | Y | Y | Y | Y | Sharing and the 30-day deletion are testable |

**Rewrites made during the Week 4 check (unchanged):** US-01 was split from search (now US-02); US-02 was rewritten from "date picker" to the need; US-04 was narrowed to the search-and-contact path; the "map view" story was deleted. **In v2.0** a map view came back as part of US-07, because the advisor asked for distance and nearby stops, which makes the map a means to a stated need rather than a UI wish.

---

## 4. Use Cases

### UC-01: Sign In and Publish a Listing
**Expands:** US-01, US-05, US-08
**Primary actor:** Subleasing student
**Secondary actors:** Supabase Auth email (E1/E3), Fair Housing screening (US-05, planned)

**Preconditions:** The student has a `@mail.uc.edu` or `@uc.edu` address (or one on the staff allowlist), and fewer than 20 active listings.

**Main success flow**
1. Student enters their UC email on the sign-in page.
2. The system checks the domain (database trigger) and emails a one-time sign-in link.
3. Student opens the link; the system signs them in. On the first sign-in, a profile is created and the student sees the welcome slides and roommate questions (US-06).
4. Student opens Post and enters title, address (looked up to coordinates, giving distance from UC), rent, dates, utilities, furnished, room or whole unit, transfer type, amenities, and up to 8 photos (compressed automatically).
5. Student ticks "My landlord allows subletting"; the sublet fee and the split slider appear (US-08).
6. *(Planned, US-05)* The system screens the title and description against the Fair Housing phrase list.
7. The system validates and saves the listing as active, and it appears to other signed-in users.

**Alternate flow A1: Returning user.** At step 2 the account exists; the link signs them in and the flow skips the welcome slides.

**Exception flow E1: Non-UC email.** At step 2 the trigger rejects the address with "Only UC email addresses can join Roost"; no email is sent.

**Exception flow E2: Expired or used link.** At step 3 the link does not sign in; the student requests a new one.

**Exception flow E3: Discriminatory language (planned).** At step 6 the listing is held for review and the student sees the flagged phrase.

**Exception flow E4: Invalid fields or no consent.** At step 7 the database check rejects the row (end date not after start date, rent outside $1 to $20,000, consent not ticked); nothing is saved.

**Postcondition:** On success the listing is active and visible to signed-in users. On any exception, nothing is visible to others.

### UC-02: Approve Proposed Subleaser: WITHDRAWN in v2.0
Withdrawn with US-03. Consent is captured in UC-01 step 5.

### UC-03: Find a Sublease and Contact the Host (added v2.0)
**Expands:** US-02, US-04, US-06, US-07, US-10, US-11
**Primary actor:** Sublessee student

**Main success flow**
1. Signed-in student opens Discover (swipe deck) or Browse (list or map).
2. Student sets filters: dates (whole-range coverage, with Spring/Summer/Fall presets), distance from UC, rent range, bedrooms, furnished.
3. The system shows matching listings ranked by roommate fit; poor fits are hidden until **Show all**.
4. Student opens a listing: photos, fees, distance, nearest shuttle and bus stop, roommate fit, property company rating.
5. Student swipes right (or presses Message); the system opens a chat with a pre-drafted first message.
6. Host replies in real time. When both are ready, each presses Share to reveal their email.

**Alternate flow A1:** At step 5 the student saves the listing instead and compares 2 to 3 saved listings later.
**Exception flow E1:** The listing was rented or removed; starting a chat fails with "That listing is no longer available."
**Exception flow E2:** The student reports the listing (US-09) instead of contacting the host.
**Postcondition:** A thread exists that only the two participants can read. Each message is deleted 30 days after it was sent, and a thread older than 30 days is deleted once it has no messages left.

---

## 5. Acceptance Criteria (Given / When / Then)

**AC-01.1 (UC-01 main flow)**
Given a signed-in UC user with fewer than 20 active listings,
When they submit a valid listing with landlord consent,
Then the listing is active and appears for another signed-in user within 60 seconds.

**AC-01.2 (UC-01 E1, E2)**
Given an address that is not `@mail.uc.edu`, `@uc.edu` or allowlisted, or a sign-in link that is expired or already used,
When the person tries to sign in,
Then no account or session is created; a non-UC address receives no email.

**AC-01.3 (UC-01 E3, planned with US-05)**
Given a description containing a phrase on the Fair Housing flag list,
When the student submits the listing,
Then it is held for review, returns 0 results for any other user, and the student is shown the flagged phrase.

**AC-01.4 (UC-01 E4)**
Given a listing whose end date is not after its start date, whose rent is outside $1 to $20,000, or whose landlord-consent box is unticked,
When it is submitted,
Then the database rejects it and no listing row exists.

**AC-02.1, AC-02.2: WITHDRAWN in v2.0** (with UC-02).

**AC-03.1 (UC-03 step 2)**
Given listings available Jan 1 to May 1 and Jan 15 to May 1,
When a student filters for Jan 10 to Apr 30,
Then only the first listing is shown.

**AC-03.2 (UC-03 step 3, US-06)**
Given a student with roommate preferences,
When they open Discover without Show all,
Then rooms are ordered by fit score and rooms scoring below 55% are hidden, with a count of hidden listings.

**AC-03.3 (UC-03 step 6, US-11)**
Given a chat where the host has not pressed Share,
When the seeker asks for the host's contact,
Then no email is returned. After the host shares, the host's email is returned.

**AC-03.4 (US-11)**
Given a chat message older than 30 days,
When the nightly cleanup runs (03:17 UTC),
Then the message no longer exists.

**AC-03.5 (US-09)**
Given a signed-in student,
When they report a listing with a 3 to 200 character reason,
Then one report row is stored. A second report of the same listing by the same student is refused.
