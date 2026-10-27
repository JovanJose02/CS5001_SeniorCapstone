"""Single source of truth for the Assignment 8 plan.
Verified Student Sublease Marketplace - CS5001 Senior Design I.
Every table in the PDF, Tasklist.md, and the CSV files is generated from this file,
so IDs, names, and owners stay the same everywhere.
"""
from datetime import date as D

TEAM = {
    "J": "Jovan Jose Asker Fredy",
    "D": "Danvanth Vanganuri",
    "M": "Mohamed Aidja",
}
SHORT = {"J": "Jovan", "D": "Danvanth", "M": "Mohamed"}
ORDER = ["J", "D", "M"]

# Hours per member per week spent on senior design outside class
AVAIL = {"fall": 10, "spring": 14}
TASK_BUFFER = 0.20  # 20% added to every task

# Task: id, verb-first statement (no owner), module, owner, O, M, P,
#       start, end, deps, phase, risks, review hours by the other members
TASKS = [
    dict(id="T1", text="Develop the project skeleton, the CI pipeline, the G2 Configuration module, and the E3 database schema migrations.",
         module="G2 Configuration; E3 Managed SQL DB", owner="J", O=6, M=12, P=20,
         start=D(2026, 11, 2), end=D(2026, 11, 11), deps=[], phase=1, risks=["RK4"], review={"D": 1.5, "M": 1.5}),
    dict(id="T2", text="Research and obtain the E1 Email Delivery API account, and confirm its free-tier limit, webhook signing, and idempotency keys.",
         module="E1 Email Delivery API (for C8)", owner="D", O=3, M=5, P=10,
         start=D(2026, 11, 2), end=D(2026, 11, 6), deps=[], phase=1, risks=["RK1", "RK5"], review={"J": 0.5, "M": 0.5}),
    dict(id="T3", text="Design the C1 Web Client wireframes and the accessibility checklist for every user story screen.",
         module="C1 Web Client", owner="M", O=6, M=10, P=16,
         start=D(2026, 11, 2), end=D(2026, 11, 11), deps=[], phase=1, risks=["RK10"], review={"J": 1.5, "D": 1.5}),
    dict(id="T4", text="Specify the C4 Compliance Screener phrase list v1, including the Ohio R.C. 4112 protected classes.",
         module="C4 Compliance Screener", owner="J", O=4, M=8, P=14,
         start=D(2026, 11, 16), end=D(2026, 11, 20), deps=[], phase=1, risks=["RK7"], review={"D": 1.0, "M": 1.0}),
    dict(id="T5", text="Develop the G3 Logging and audit module (log, audit record, and the /healthz check).",
         module="G3 Logging and audit", owner="M", O=4, M=8, P=12,
         start=D(2026, 11, 16), end=D(2026, 11, 20), deps=["T1"], phase=1, risks=[], review={"J": 1.0, "D": 1.0}),
    dict(id="T6", text="Develop the G1 Authentication middleware and the signed session token.",
         module="G1 Authentication middleware", owner="D", O=6, M=10, P=16,
         start=D(2026, 11, 16), end=D(2026, 12, 2), deps=["T1"], phase=1, risks=["RK3"], review={"J": 1.5, "M": 1.5}),
    dict(id="T7", text="Develop the C2 Identity Service for @mail.uc.edu login links, the 24-hour link expiry, and rate limits (I2, I10).",
         module="C2 Identity Service", owner="D", O=12, M=18, P=30,
         start=D(2027, 1, 11), end=D(2027, 1, 22), deps=["T2", "T6"], phase=2, risks=["RK1", "RK2"], review={"J": 1.5, "M": 2.0}),
    dict(id="T8", text="Develop the C4 Compliance Screener screen() function (I7) with unit tests for every phrase category.",
         module="C4 Compliance Screener", owner="J", O=6, M=10, P=18,
         start=D(2027, 1, 11), end=D(2027, 1, 15), deps=["T1", "T4"], phase=2, risks=["RK7"], review={"D": 1.0, "M": 0.5}),
    dict(id="T9", text="Develop the C3 Listing Service create, validate, hold, publish, and review endpoints (I3).",
         module="C3 Listing Service", owner="J", O=12, M=20, P=32,
         start=D(2027, 1, 19), end=D(2027, 1, 29), deps=["T6", "T8"], phase=2, risks=[], review={"D": 1.5, "M": 2.0}),
    dict(id="T11", text="Develop the C8 Notification Service queue, the E1 send with retries, the status webhook, and the suppression list (I10 to I13).",
         module="C8 Notification Service", owner="D", O=10, M=18, P=28,
         start=D(2027, 1, 25), end=D(2027, 2, 3), deps=["T2", "T7"], phase=2, risks=["RK1", "RK5"], review={"J": 1.5, "M": 1.0}),
    dict(id="T12", text="Develop the C1 Web Client screens for sign-in, create listing, and search (I1 to I4).",
         module="C1 Web Client", owner="M", O=12, M=20, P=34,
         start=D(2027, 1, 11), end=D(2027, 1, 22), deps=["T3", "T6"], phase=2, risks=["RK8", "RK10"], review={"J": 2.0, "D": 2.0}),
    dict(id="T13", text="Develop the C6 Messaging Service threads, messages, and alert limits (I5, I11).",
         module="C6 Messaging Service", owner="M", O=10, M=16, P=26,
         start=D(2027, 1, 25), end=D(2027, 2, 3), deps=["T5", "T6"], phase=2, risks=[], review={"J": 1.5, "D": 1.5}),
    dict(id="T10", text="Develop the C3 outbox relay and the C5 Search & Match index and date-coverage search (I8, I4).",
         module="C3 Listing Service; C5 Search & Match", owner="J", O=14, M=20, P=32,
         start=D(2027, 2, 8), end=D(2027, 2, 19), deps=["T9"], phase=3, risks=["RK4"], review={"D": 1.5, "M": 2.0}),
    dict(id="T14", text="Develop the C7 Approval Service proposals, decisions, unit registry seed, and daily reminder job (I6, I9, I12).",
         module="C7 Approval Service", owner="D", O=12, M=20, P=32,
         start=D(2027, 2, 8), end=D(2027, 2, 23), deps=["T9", "T11"], phase=3, risks=["RK6"], review={"J": 2.0, "M": 2.0}),
    dict(id="T15", text="Develop the C1 Web Client screens for messages, approval requests, and the review queue (I5, I6).",
         module="C1 Web Client", owner="M", O=12, M=18, P=30,
         start=D(2027, 2, 8), end=D(2027, 2, 23), deps=["T12", "T13"], phase=3, risks=["RK8"], review={"J": 1.5, "D": 2.0}),
    dict(id="T16", text="Test the timing budgets and error paths for AC-01.1, AC-02.1, and AC-02.2 with automated end-to-end tests.",
         module="C3, C7, C8 (outbox and email path)", owner="D", O=8, M=14, P=24,
         start=D(2027, 3, 1), end=D(2027, 3, 10), deps=["T10", "T11", "T14"], phase=4, risks=["RK3", "RK4"], review={"J": 3.0, "M": 1.5}),
    dict(id="T17", text="Validate US-04 accessibility with axe-core in CI and a manual NVDA and VoiceOver pass.",
         module="C1 Web Client", owner="M", O=6, M=10, P=18,
         start=D(2027, 3, 1), end=D(2027, 3, 10), deps=["T12", "T15"], phase=4, risks=["RK10"], review={"J": 1.5, "D": 1.5}),
    dict(id="T18", text="Validate the release candidate with a five-student user test, and document the results and the user guide.",
         module="Whole system (C1 to C8)", owner="J", O=8, M=14, P=22,
         start=D(2027, 3, 22), end=D(2027, 4, 2), deps=["M8"], phase=4, risks=["RK6", "RK7"], review={"D": 3.0, "M": 3.0}),
]
TASKS.sort(key=lambda t: int(t["id"][1:]))

PHASES = {
    1: ("Phase 1: Foundation", "Fall 2026, Nov 2 to Dec 4", "Shared setup, sign-in base, design inputs for spring."),
    2: ("Phase 2: Core services", "Spring 2027, Jan 11 to Feb 5", "Sign-in, listings, screening, email, first screens."),
    3: ("Phase 3: Workflows", "Spring 2027, Feb 8 to Feb 26", "Search, messaging, approval, and their screens."),
    4: ("Phase 4: Test and release", "Spring 2027, Mar 1 to Apr 16", "Timing tests, accessibility, user test, release."),
}

# Critical path (zero float except the protected buffer blocks)
CRITICAL = ["T1", "T6", "T7", "T11", "T14", "T16", "T18"]

# Milestones: id, name, what it shows, date (or text), verify, verifier, status, kind, buffer block
MILESTONES = [
    dict(id="M0a", name="Project description and Week 3 constraints", kind="Course",
         shows="The problem, the goal, the users, and the budget, hosting, privacy, and accessibility limits are written down.",
         date="Week 3 (Sep 2026)", verify="Project-Description.md is in the repository and was graded.", by="Instructor", status="Complete"),
    dict(id="M0b", name="User Stories (US-01 to US-05, UC-01, UC-02, AC-01.1 to AC-02.2)", kind="Course",
         shows="Every feature has a user story, a use case, and acceptance criteria we can test.",
         date="Week 5 (Sep 2026)", verify="User_Stories document is in the repository and was graded.", by="Instructor", status="Complete"),
    dict(id="M0c", name="Design D0: High-Level Design", kind="Course",
         shows="The system is split into C1 to C8 with 15 interfaces, two data flows, and a decision log.",
         date="Oct 2, 2026", verify="D0 document and .drawio files are in Design_Diagrams.", by="Instructor", status="Complete"),
    dict(id="M0d", name="Design D1: Detailed Design of C3 and C5", kind="Course",
         shows="Data model, algorithms, and API for the Listing Service and Search & Match.",
         date="Week 7 (Oct 2026)", verify="D1 document is in Design_Diagrams.", by="Instructor", status="Complete"),
    dict(id="M0e", name="Design D2 and peer review (consolidated Assignment #4 PDF)", kind="Course",
         shows="All components, glue modules G1 to G3, state machines, edge cases, and traceability are designed. Peer review found no issues.",
         date="Oct 14, 2026", verify="Consolidated PDF submitted on Canvas by each member; D2 in Design_Diagrams.", by="Instructor and peer teams", status="Complete"),
    dict(id="M1", name="Assignment 8: Task list, milestones, timeline, effort matrix", kind="Course",
         shows="The design is turned into 18 owned tasks with dates, effort, and risks.",
         date=D(2026, 10, 28), verify="This PDF on Canvas; Tasklist.md in the repository root; sources in Planning/.", by="Instructor and advisor", status="Planned"),
    dict(id="M2", name="Development environment ready", kind="Internal", major=True, block=(D(2026, 11, 12), D(2026, 11, 13)),
         shows="Code builds and deploys. A real email reaches a @mail.uc.edu inbox (not junk). The search date index works on our database.",
         date=D(2026, 11, 13), verify="Demo at the weekly meeting: CI is green on main, /healthz answers on Render, migrations run on Supabase, test email screenshot, btree_gist query runs.",
         by="Mohamed checks T1; Jovan checks T2 and T3", status="Planned"),
    dict(id="M3", name="Week 14 report (reproduces these tables)", kind="Course", block=(D(2026, 11, 23), D(2026, 11, 24)),
         shows="Progress against this plan is reported, with updated Table 1 and Table 2.",
         date=D(2026, 11, 25), verify="Report submitted on Canvas by each member.", by="Instructor and advisor", status="Planned"),
    dict(id="M4", name="Phase 1 done: sign-in base and screening rules", kind="Internal", major=True, block=(D(2026, 12, 3), D(2026, 12, 4)),
         shows="G1 accepts a valid signed token and rejects a bad one. G3 writes log and audit rows. Phrase list v1 is approved.",
         date=D(2026, 12, 4), verify="G1 and G3 unit tests pass in CI; advisor signs off on the phrase list.", by="Advisor (phrase list); Jovan (tests)", status="Planned"),
    dict(id="M5", name="Spring re-kickoff and re-baseline", kind="Internal",
         shows="Every member's spring schedule and co-op status is confirmed. CS 5002 dates are added to the plan.",
         date=D(2027, 1, 15), verify="Updated Table 1 committed to Planning/; meeting notes list each member's status.", by="Whole team; advisor informed", status="Planned"),
    dict(id="M6", name="Walking skeleton", kind="Internal", major=True, block=(D(2027, 2, 4), D(2027, 2, 5)),
         shows="A student signs in with an emailed link, creates a listing, and a listing with a flagged phrase is held for review.",
         date=D(2027, 2, 5), verify="Live demo on the deployed site, plus an automated end-to-end test in CI.", by="Advisor at the weekly check-in", status="Planned"),
    dict(id="M7", name="Core flows work end to end", kind="Internal", major=True, block=(D(2027, 2, 24), D(2027, 2, 26)),
         shows="Search by co-op dates, messaging, and property-manager approval all work, with real emails.",
         date=D(2027, 2, 26), verify="Demo of Data Flow A and Data Flow B from D0 on the deployed site.", by="Advisor", status="Planned"),
    dict(id="M8", name="Feature complete", kind="Internal", major=True, block=(D(2027, 3, 11), D(2027, 3, 12)),
         shows="All five user stories work and every acceptance criterion has a passing automated test.",
         date=D(2027, 3, 12), verify="CI report: all AC tests pass, zero axe-core violations, timing tests inside budget.", by="Advisor; Danvanth runs the report", status="Planned"),
    dict(id="M9", name="User test sessions done", kind="Internal",
         shows="Five UC students used the system and their problems are logged.",
         date=D(2027, 3, 26), verify="Signed-off test notes and an issue list in the repository.", by="Mohamed and Danvanth (session helpers)", status="Planned"),
    dict(id="M10", name="Release candidate v1.0", kind="Internal", major=True, block=(D(2027, 4, 5), D(2027, 4, 8)),
         shows="User test issues are fixed, v1.0 is tagged and deployed, and the user guide is written.",
         date=D(2027, 4, 9), verify="Git tag v1.0; the deployed site passes the full test suite; user guide in the repository.", by="Advisor", status="Planned"),
    dict(id="M11", name="Final demo (CS 5002 expo)", kind="Course",
         shows="The finished product is shown to the instructor, advisor, and visitors.",
         date=D(2027, 4, 16), verify="Demo given on the expo day. Date to be fixed at M5 from the CS 5002 calendar.", by="Instructor and advisor", status="Planned"),
]

# Calendar periods with no planned work
BLOCKED = [
    ("Thanksgiving", D(2026, 11, 26), D(2026, 11, 27)),
    ("Fall last week + exam week", D(2026, 12, 7), D(2026, 12, 18)),
    ("Winter break", D(2026, 12, 19), D(2027, 1, 10)),
    ("MLK Day", D(2027, 1, 18), D(2027, 1, 18)),
    ("Spring break", D(2027, 3, 15), D(2027, 3, 19)),
]

# Risk register
RISKS = [
    dict(id="RK1", cat="Technical", risk="UC Mail (Microsoft 365) puts our login emails in junk or blocks them, so students cannot sign in.",
         L="Medium", I="High", strat="Reduce",
         mit="T2 sends a real test email to a @mail.uc.edu inbox in week 1. We set SPF and DKIM on the sending domain. We keep a second provider as a backup.",
         owner="D", trigger="A test email lands in junk or bounces.", where="T2, T7, T11; checked at M2"),
    dict(id="RK2", cat="Team", risk="A member goes on co-op in Spring 2027 and has less time or works off campus.",
         L="Medium", I="High", strat="Avoid",
         mit="Each member confirms spring status by M5 (Jan 15). If someone is on co-op, we move their spring tasks to the others and they take review work. All work is in the repository, so it can be done remotely.",
         owner="J", trigger="Any member accepts a Spring 2027 co-op.", where="M5 re-baseline; T7"),
    dict(id="RK3", cat="Team", risk="Exams, Thanksgiving, and other courses slow us down.",
         L="High", I="Medium", strat="Reduce",
         mit="No tasks during fall exam week or winter break. Every task has 20% buffer. Each major milestone has a protected buffer block.",
         owner="M", trigger="A task is more than 25% behind at the weekly check.", where="Blocked rows and buffer rows in Table 1; T6, T16"),
    dict(id="RK4", cat="Technical", risk="The free hosting tier is missing the btree_gist extension, or the Render instance sleeps and the outbox relay stops. Search and email then miss AC-01.1.",
         L="Medium", I="High", strat="Reduce",
         mit="T1 tests both before M2. If the instance sleeps, we pay for the always-on tier (inside the about $7 per month budget, NFR-07).",
         owner="J", trigger="Extension not available, or a gap over 60 s between relay polls in the logs.", where="T1, T10, T16; checked at M2"),
    dict(id="RK5", cat="External", risk="The E1 email provider changes its free limit or price.",
         L="Low", I="Medium", strat="Transfer",
         mit="The provider is responsible for delivery under its terms. C8 keeps the provider behind one interface (I13), so we can switch providers in about a day.",
         owner="D", trigger="Monthly use goes over 70% of the free limit, or the terms change.", where="T2, T11"),
    dict(id="RK6", cat="External", risk="We cannot find a real property manager to test US-03 (approval).",
         L="Medium", I="Medium", strat="Accept",
         mit="We seed test property-manager accounts that the team controls (D-09, GQ-04). We ask the advisor for a real contact before M7.",
         owner="D", trigger="No property-manager contact by Feb 26, 2027.", where="T14, T18"),
    dict(id="RK7", cat="Technical", risk="The Fair Housing phrase list misses a phrase or flags too many fair listings.",
         L="Medium", I="Medium", strat="Reduce",
         mit="Advisor reviews phrase list v1 at M4. Flagged listings go to a person for review, never straight out. The user test checks false flags.",
         owner="J", trigger="More than 10% false flags in the user test, or a missed phrase is found.", where="T4, T8, T18; checked at M4"),
    dict(id="RK8", cat="Technical", risk="The C1 screens and the backend APIs stop matching, because screens are built against mock data first.",
         L="Medium", I="High", strat="Reduce",
         mit="Shared zod schemas are the contract. Contract tests run in CI. The protected blocks before M6 and M7 are used for joining the parts.",
         owner="M", trigger="A contract test fails in CI.", where="T12, T15; buffer before M6 and M7"),
    dict(id="RK9", cat="External", risk="The CS 5002 calendar and spring break dates are not published yet, so spring dates may move.",
         L="High", I="Low", strat="Accept",
         mit="We re-baseline Table 1 at M5 when the calendar is posted.", owner="J", trigger="The CS 5002 calendar is posted.", where="M5, M11"),
    dict(id="RK10", cat="Technical", risk="Accessibility problems (US-04) are found late.",
         L="Medium", I="Medium", strat="Reduce",
         mit="The accessibility checklist is part of T3. axe-core runs in CI from T12, not only in T17.",
         owner="M", trigger="axe-core reports any violation on main.", where="T3, T12, T17"),
]


def pert(t):
    return round((t["O"] + 4 * t["M"] + t["P"]) / 6, 1)


def effort_row(t):
    row = {k: 0.0 for k in ORDER}
    row[t["owner"]] = pert(t)
    for k, h in t["review"].items():
        row[k] += h
    return row
