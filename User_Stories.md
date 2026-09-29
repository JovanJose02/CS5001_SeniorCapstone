# User Stories and Use Cases

**Project:** Verified Student Sublease Marketplace
**Course:** CS5001 Senior Design I, Assignment 4 (Week 4)
**Team members:** Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja

---

## 1. Stakeholder Map

| Category | Stakeholder | What they need from the system |
|---|---|---|
| Primary | UC student leaving for an out-of-town co-op (subleaser) | Fill an empty room fast with someone trustworthy |
| Primary | Student relocating to Cincinnati for one term (sublessee) | Housing that matches a 3 to 4 month stay |
| Secondary | Property manager / landlord | Know who occupies the unit and enforce lease terms |
| Secondary | Parent or guarantor on the lease | Assurance the replacement tenant is a real, verified student |
| Hidden (accessibility) | Blind or low-vision student using a screen reader | Search and contact listings without sighted help |
| Hidden (compliance) | Fair Housing compliance reviewer | Listings free of discriminatory preference language |
| Hidden (downstream system) | UC email verification / identity service | Well-formed, rate-limited verification requests |

---

## 2. User Stories

**US-01 (Primary)**
As a UC student leaving Cincinnati for a one-semester co-op,
I want only verified UC students to be able to contact me about my room,
so that I stop paying rent on an empty room and know who is living in my unit.

**US-02 (Primary)**
As a UC student relocating to Cincinnati for a single co-op term,
I want to find subleases whose available dates cover my exact co-op start and end dates,
so that I do not have to sign a 12-month lease for a 4-month stay.

**US-03 (Secondary)**
As a property manager of a student apartment building,
I want to be notified of a proposed subleaser and approve or reject them before move-in,
so that my lease terms are enforced and I have a record of who occupies each unit.

**US-04 (Hidden: accessibility)**
As a blind student who navigates with a screen reader,
I want to search listings and send a message to a subleaser without sighted assistance,
so that I have the same access to housing as every other student.

**US-05 (Hidden: compliance)**
As a Fair Housing compliance reviewer for the platform,
I want listings containing discriminatory preference language to be held for review before they are published,
so that the platform and its users avoid Fair Housing Act violations.

---

## 3. INVEST Self-Check

| Story | I | N | V | E | S | T | Notes |
|---|---|---|---|---|---|---|---|
| US-01 | Y | Y | Y | Y | Y | Y | Verification is part of listing; search is a separate story (US-02) |
| US-02 | Y | Y | Y | Y | Y | Y | Date matching testable with fixed date ranges |
| US-03 | Partial | Y | Y | Y | Y | Y | Needs a listing to exist (US-01); built and tested against seeded listing data so it can ship independently |
| US-04 | Y | Y | Y | Y | Y | Y | Scoped to search + message only, not the whole app, to keep it Small |
| US-05 | Y | Y | Y | Y | Y | Y | Testable with a fixed list of flagged phrases |

**Rewrites made during the check**
- An early draft of US-01 combined listing, verification, and search in one story. Split: search became US-02.
- An early draft of US-02 said "filter listings with a date picker." Rewritten to state the need (dates cover my co-op term) instead of a UI element.
- An early draft of US-04 covered "the whole app is accessible." Too large to estimate; narrowed to the search-and-contact path.
- A story "As a user, I want a map view" was deleted: vague role, UI element, no benefit.

---

## 4. Use Cases

### UC-01: Publish Verified Sublease Listing
**Expands:** US-01
**Primary actor:** Subleasing student
**Secondary actors:** UC email verification service, compliance screening (US-05), property manager (notified)

**Preconditions**
1. The student has an account on the platform.
2. The student's account email ends in `@mail.uc.edu`.
3. The student has no other active listing for the same address.

**Main success flow**
1. Student starts a new listing.
2. System checks verification status and finds the account unverified.
3. Student requests verification.
4. System sends a one-time link to the student's `@mail.uc.edu` address, valid for 24 hours.
5. Student opens the link.
6. System marks the account verified and returns the student to the listing.
7. Student enters address, monthly rent, available start and end dates, and description.
8. System validates that the end date is after the start date and rent is greater than $0.
9. Student submits the listing.
10. System screens the description for discriminatory language, finds none, publishes the listing, and notifies the property manager on file for that address.

**Alternate flow A1: Student already verified**
- At step 2, the system finds the account verified within the last 12 months and skips to step 7.

**Exception flow E1: Verification link expired**
- At step 5, the link is more than 24 hours old.
- System rejects the link, shows that it expired, and offers to send a new one.
- Listing is not published. Use case resumes at step 3.

**Exception flow E2: Discriminatory language detected**
- At step 10, the description contains a flagged phrase (for example, a preference based on race, religion, or familial status).
- System does not publish the listing, marks it "Held for review," and tells the student which phrase triggered the hold.
- Use case ends; the listing enters the compliance review queue.

**Postcondition**
- On success: the listing is visible in search to verified UC students only, and the property manager has been notified.
- On exception: no listing is visible to other students.

---

### UC-02: Approve Proposed Subleaser
**Expands:** US-03
**Primary actor:** Property manager
**Secondary actors:** Subleasing student, sublessee student

**Preconditions**
1. A published listing exists for a unit the property manager is registered to.
2. The subleaser has marked a verified student as their proposed subleaser.

**Main success flow**
1. System notifies the property manager of the proposed subleaser.
2. Property manager opens the request.
3. System shows the sublessee's name, verified UC status, and requested dates.
4. Property manager approves the request.
5. System records the approval with a timestamp and notifies both students.

**Alternate flow A1: Property manager rejects**
- At step 4, the property manager rejects and enters a reason.
- System records the rejection and notifies the subleaser with the reason.

**Exception flow E1: No response**
- At step 2, the property manager does not respond within 5 business days.
- System sends one reminder and tells the subleaser the request is still pending.

**Postcondition**
- The request is in exactly one state: approved, rejected, or pending, and the state is visible to both students.

---

## 5. Acceptance Criteria (Given / When / Then)

**AC-01.1 (UC-01 main flow)**
Given a student with a verified `@mail.uc.edu` account and no active listing for the address,
When they submit a listing with valid dates, rent, and a description with no flagged phrases,
Then the listing appears in search results for a verified student within 60 seconds, and the property manager on file receives a notification within 5 minutes.

**AC-01.2 (UC-01 exception E1)**
Given a verification link that was issued more than 24 hours ago,
When the student opens it,
Then the account stays unverified, the student sees an "expired" message, and no listing is published.

**AC-01.3 (UC-01 exception E2)**
Given a listing description containing a phrase on the platform's Fair Housing flag list,
When the student submits the listing,
Then the listing has status "Held for review," returns 0 results in any other user's search, and the student is shown the exact flagged phrase.

**AC-01.4 (UC-01 validation)**
Given a listing with an end date earlier than or equal to the start date,
When the student submits it,
Then the system rejects the submission and no listing record is created.

**AC-02.1 (UC-02 main flow)**
Given a pending subleaser request for a unit registered to the property manager,
When the property manager approves it,
Then the request status is "Approved" with a timestamp, and both students receive a notification within 5 minutes.

**AC-02.2 (UC-02 exception E1)**
Given a pending request with no property manager response,
When 5 business days have passed,
Then exactly 1 reminder is sent to the property manager and the subleaser sees status "Pending."
