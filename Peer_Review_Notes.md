# Peer Review Notes: Verified Student Sublease Marketplace (Design D2)

Team: Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja

Criterion: completeness, feasibility, clarity, risk. Priority: must-fix, worth considering, out of scope for now.

> **Status update (2026-10-28).** D2 has been superseded by the Roost prototype ([roost-uc-sublease](https://github.com/trivinity/roost-uc-sublease)); see [Technical_Specification.md](Technical_Specification.md) v2.0 §7. The open self-audit items now stand as follows:
> - **PR-S05**: moot. Supabase's emailed link replaced the custom token; delivery testing is Tasklist T19.
> - **PR-S07**: closed. Listings can be marked rented (host) or removed (staff).
> - **PR-S08**: closed. Email goes through Supabase Auth with custom SMTP (T19).
> - **PR-S10**: still open as GQ-02 / T4.
> - **PR-S12**: moot. There is no ACCOUNT_VERIFIED audit row in the prototype.
>
> The tables below are the D2 record and are unchanged.

## 1. Self-audit action items (pre-review, not peer feedback)

| ID | Criterion | Issue | Raised by | Action | Owner | Priority | Due | Status |
|---|---|---|---|---|---|---|---|---|
| PR-S01 | Feasibility | D1 outbox poll is 30 s; D0 says 5 s; 30 s misses AC-01.1. | Own team (D0 walk) | Adopt 5 s; recompute budgets (Part 2.11, R-02). | Jovan | Must-fix | Oct 14 | Done in D2 |
| PR-S02 | Completeness | D1 outbox drain skips I16 (C6) and I9 (C7). | Own team | Per-consumer outbox rows (Part 2.8, Fig. 6, R-01). | Jovan | Must-fix | Oct 14 | Done in D2 |
| PR-S03 | Clarity | Same validation failure is 422 in D0 (I3, I5, I6) and 400 in D1. | Own team | One error-code rule (Part 1.1, R-08); revisions in Part 2.10. | Jovan, Mohamed | Must-fix | Oct 14 | Done in D2 |
| PR-S04 | Clarity | D1 cites AC-01.4 for the review 409 and AC-01.1 for invalid input; D0 maps invalid input to AC-01.4. | Own team | Traceability follows D0's mapping; note in Part 4. | Jovan | Must-fix | Oct 14 | Done in D2 |
| PR-S05 | Risk | UC Mail link scanning may consume the one-time token. | Own team | Click-to-confirm page (R-03); test with a real @mail.uc.edu inbox. | Danvanth | Must-fix | Week 8 | Design done; test open |
| PR-S06 | Risk | D0 worst cases (41 s, 3.6 min) omit send timeouts and poll lag. | Own team | Recompute (Part 2.11). | Danvanth | Worth considering | Oct 14 | Done in D2 |
| PR-S07 | Feasibility | No way for a listing to leave PUBLISHED (withdraw, filled, expired). | Own team | Ask instructor whether to add a story; if yes, add LISTING_WITHDRAWN event. | Jovan | Worth considering | Week 8 | Open (GQ-03) |
| PR-S08 | Feasibility | Email provider not chosen; quota, webhook signing, and idempotency support unknown. | Own team | Pick provider against EC-C8-02, 04, 06 needs. | Danvanth | Must-fix | Week 8 | Open (GQ-05) |
| PR-S09 | Completeness | senderFirstName (D0 I11) has no source field. | Own team | Collect firstName at first confirmation (Part 2.3, EC-C2-06). | Danvanth | Must-fix | Oct 14 | Done in D2 |
| PR-S10 | Risk | Phrase list v1 has no content; protected classes under Ohio law not confirmed. | Own team | Draft list v1 with the reviewer; confirm categories. | Jovan | Must-fix | Week 8 | Open (GQ-02) |
| PR-S11 | Completeness | No endpoint returns one listing or an owner's own listings. | Own team | Add GET /listings/{id} and /listings/mine (Part 2.8). | Jovan | Must-fix | Oct 14 | Done in D2 |
| PR-S12 | Clarity | ACCOUNT_VERIFIED audit rows have no requirement behind them. | Own team | Keep or cut at next team meeting (Part 4.2). | Mohamed | Out of scope for now | Week 8 | Open |

## 2. Feedback received

### Reviewed by Team ____ (items PR-Axx)

| ID | Criterion | Issue (as raised) | Action | Owner | Priority | Due |
|---|---|---|---|---|---|---|
| PR-A01 |  |  |  |  |  |  |
| PR-A02 |  |  |  |  |  |  |
| PR-A03 |  |  |  |  |  |  |

### Reviewed by Team ____ (items PR-Bxx)

| ID | Criterion | Issue (as raised) | Action | Owner | Priority | Due |
|---|---|---|---|---|---|---|
| PR-B01 |  |  |  |  |  |  |
| PR-B02 |  |  |  |  |  |  |
| PR-B03 |  |  |  |  |  |  |

## 3. Summary

- Criterion with the most feedback: ____
- Must-fix items applied to D2 before submission: ____

## 4. Top two issues we raised while reviewing other teams

| # | Team reviewed | Issue we raised | Criterion | Why it mattered |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
