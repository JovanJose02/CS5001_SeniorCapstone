"""Builds D2_Detailed_Design.html -> PDF, and Peer_Review_Notes.md."""
import html, re, os, subprocess
from content_tables import EDGE, TRACE, REVERSE, RATIONALE, AUDIT

HERE = os.path.dirname(os.path.abspath(__file__))


def fmt(s):
    s = html.escape(str(s))
    s = s.replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>").replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;")
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def table(headers, rows, widths=None, cls=""):
    cols = "".join(f'<col style="width:{w}">' for w in widths) if widths else ""
    h = "".join(f"<th>{fmt(x)}</th>" for x in headers)
    body = "".join("<tr>" + "".join(f"<td>{c if isinstance(c, Raw) else fmt(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><colgroup>{cols}</colgroup><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


class Raw(str):
    pass


ROTATE = {"D2_Fig4_State_Account_Listing", "D2_Fig6_State_Notification_Outbox",
          "D2_Fig7_Error_Paths_Publish", "D2_Fig8_Error_Paths_SignIn"}
FIGPAGES = {}


def fig(name, caption, width="100%"):
    if name in ROTATE:  # placed later by stamp.py as a landscape page
        FIGPAGES[name] = re.sub(r"<[^>]+>", "", caption)
        return f'<div class="pb" style="page-break-after: always"><p>FIGPAGE:{name}</p></div>'
    return (f'<div class="fig"><img src="figs/{name}.png" style="width:{width}"/>'
            f'<p class="cap">{caption}</p></div>')


def kv(rows):  # two-column part/detail table like D1's algorithm entries
    return table(["Part", "Detail"], rows, ["17%", "83%"], "kv")


CSS = """
@font-face { font-family: 'Inter'; }
body { font-family: 'Inter', 'DejaVu Sans', sans-serif; font-size: 9.6pt; line-height: 1.38; color: #111; }
h1 { text-align: center; font-size: 21pt; margin: 0 0 2px 0; }
.sub { text-align:center; font-style: italic; font-weight: 600; font-size: 12pt; margin: 0 0 10px 0; }
h2 { font-size: 14pt; margin: 20px 0 6px 0; border-bottom: 1px solid #bbb; padding-bottom: 2px; page-break-after: avoid; }
h3 { font-size: 11.2pt; margin: 14px 0 4px 0; page-break-after: avoid; }
h4 { font-size: 10pt; margin: 10px 0 3px 0; page-break-after: avoid; }
p { margin: 4px 0 6px 0; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px 0; font-size: 8.1pt; line-height: 1.3; }
th { background: #E9EEF5; text-align: left; font-weight: 700; }
th, td { border: 1px solid #9aa; padding: 3px 4px; vertical-align: top; }
tr { page-break-inside: avoid; }
thead { display: table-header-group; }
table.kv td:first-child { font-weight: 700; background: #F6F7F9; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 0.88em; background: #F1F1F1; padding: 0 2px; }
.fig { text-align: center; margin: 8px 0 12px 0; page-break-inside: avoid; }
.cap { font-style: italic; font-size: 8.8pt; text-align: left; margin-top: 3px; }
.meta td:first-child { font-weight: 700; width: 20%; background:#F6F7F9; }
.meta { font-size: 9pt; }
.note { background: #FFF8E1; border: 1px solid #E0C46C; padding: 6px 8px; font-size: 9pt; margin: 6px 0 10px 0; }
.pb { page-break-before: always; }
ul, ol { margin: 3px 0 6px 18px; padding: 0; }
li { margin: 1px 0; }
.small { font-size: 8.4pt; }
pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 7.8pt; background: #F6F6F6; border: 1px solid #ddd; padding: 5px; white-space: pre-wrap; page-break-inside: avoid; }
"""

parts = []
A = parts.append

# ============================================================================ Title block
A("""<h1>D2 Detailed Design</h1><p class="sub">Verified Student Sublease Marketplace</p>""")
A(table(["Item", "Detail"], [
    ("Course", "CS5001 Senior Design I"),
    ("Assignment", "Assignment 7: Detailed System Design, Part 2 (Design D2) and Peer Review Notes"),
    ("Team members", "Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja"),
    ("Goal", "Let UC students fill or find term-length subleases safely by limiting the marketplace to verified @mail.uc.edu students, matching listings to exact co-op dates, holding discriminatory listings for review, and giving property managers an approve/reject step before move-in."),
    ("Repository location", "Design_Diagrams/D2_Detailed_Design.pdf (this document); Design_Diagrams/D2_Fig1 to D2_Fig8 (.dot sources, render with Graphviz); Design_Diagrams/Peer_Review_Notes.md"),
    ("Inputs to this design", "User_Stories (US-01 to US-05, UC-01, UC-02, AC-01.1 to AC-02.2); D0 High-Level Design (decision log D-01 to D-12); D1 Detailed Design (C3, C5)"),
], ["20%", "80%"], "meta"))

# ============================================================================ Part 1
A("<h2>1. Header, Conventions, and D2 Overview</h2>")
A("<h3>1.1 Conventions</h3>")
A("<p>Every D2 figure carries the project title, the goal statement, and its own conventions block drawn on the figure. "
  "The table below collects them. Figures 2 and 3 keep D1's data-model notation, with one addition: a dotted line for a reference across component schemas, because D0 forbids one component from reading another's tables.</p>")
A(table(["Figure type", "Symbol", "Meaning"], [
    ("Component map (Fig. 1)", "Blue rounded box / gray rounded box / gray dashed box / ellipse", "Component we build (Cn) / glue module (Gn) used by every backend component / external system (En) / actor"),
    ("", "Dotted outline", "One deployable backend (D-01)"),
    ("", "Arrow labelled Ix; red label", "Interface from caller to callee, reply on the same interface; red = revised in D2 (Part 2.10)"),
    ("Data model (Fig. 2, 3)", "Rounded box; dashed box", "Entity in the schema of the component in its title; transient object never stored"),
    ("", "Solid line; dotted line", "Foreign key within one schema; logical reference by ID across schemas (no database FK, kept current by events or I17a/I17b)"),
    ("", "1, 0..1, 0..*, 1..* at both ends; [PK] [FK] [UQ] [UQ*] ?", "Cardinality read from the box next to the label; keys, partial unique index, nullable"),
    ("State machine (Fig. 4, 5, 6)", "Rounded box; filled dot; ringed dot", "State stored in the named column; initial; final"),
    ("", "event [guard] / action; red arrow or note", "Transition; error outcome that refuses the request and leaves the state unchanged"),
    ("Activity with error paths (Fig. 7, 8)", "Box; diamond; black arrow; red arrow and box; dashed arrow", "Step (owner in brackets); decision; happy path; error path ending in its outcome (R recoverable, N needs a person); asynchronous hand-off through an outbox or queue row"),
], ["20%", "30%", "50%"]))
A("<p><b>Data conventions</b> (unchanged from D1): dates ISO 8601 yyyy-mm-dd; datetimes UTC; business days and \"today\" in America/New_York; money in integer cents; all paths under <code>/api/v1</code>.</p>")
A("<p><b>Error envelope and code rule</b> (new in D2, R-08). Every error body is "
  "<code>{\"error\": {\"code\": \"INVALID_INPUT\", \"message\": \"...\", \"field\": \"endDate\"?, \"requestId\": \"...\"}}</code>, and 429/503 add a Retry-After header. "
  "400 = the request fails schema or range validation (shared zod schemas). 401 = no valid session. 403 = valid session, not allowed. 404 = not found or not visible to the caller. "
  "409 = conflicts with current state. 410 = expired. 422 = well-formed but refused by a business rule. 429 = rate limited. 503 = a dependency is down; retry.</p>")

A("<h3>1.2 Two-minute overview</h3>")
A("<p><b>The system.</b> A web marketplace where UC students sublease apartments for a co-op term. Only people who prove they own an @mail.uc.edu mailbox can list, search, or message. "
  "Search returns only listings whose availability covers the whole co-op term. Every listing description is screened for Fair Housing preference language and held for a human reviewer if anything matches. "
  "When an owner picks a subleaser, the unit's property manager approves or rejects before move-in. D0 split this into eight components (C1 to C8) inside one deployable backend on PostgreSQL.</p>")
A("<p><b>What D1 covered.</b> C3 Listing Service (listing lifecycle, Fair Housing hold and review, transactional outbox) and C5 Search & Match (derived search index, GiST date-coverage query), with their data model, algorithms, API, and technology choices.</p>")
A("<p><b>What D2 adds.</b> (1) Data model, behavior, and interface for C1, C2, C4, C6, C7, C8 and the glue modules G1 Authentication, G2 Configuration, G3 Logging and audit (Part 2). "
  "(2) Four state machines (Account, Listing, ApprovalRequest, Notification plus outbox rows) and two error-path diagrams for the riskiest flows (Fig. 4 to 8). "
  "(3) Corrections to D1 found by checking it against D0, and revisions to D0 interfaces that leaked data or had loose types (Parts 2.8, 2.10). "
  f"(4) {len(EDGE)} edge cases across all four categories for every component (Part 3), a forward and reverse traceability check (Part 4), ten rationale entries (Part 5), and the peer review notes (Part 6).</p>")

A("<h3>1.3 Component status</h3>")
A(table(["Component", "Owner (D0)", "Detailed in", "Data model", "Behavior", "Interface"], [
    ("C1 Web Client", "Mohamed Aidja", "D2 Part 2.2", "No persistent data", "Session states, screen table", "Consumes I2 to I6; error table"),
    ("C2 Identity Service", "Danvanth Vanganuri", "D2 Part 2.3", "Fig. 2", "Algorithm C; Fig. 4, 8", "Endpoints + I17a/I17b"),
    ("C3 Listing Service", "Jovan Jose Asker Fredy", "D1; D2 Part 2.8 changes", "D1 Fig. 1 + D2 changes", "D1 Algorithm B; Fig. 4, 6, 7", "D1 §5 + 2 GET endpoints"),
    ("C4 Compliance Screener", "Jovan Jose Asker Fredy", "D2 Part 2.4", "No persistent data (versioned file)", "Algorithm D", "screen() (I7)"),
    ("C5 Search & Match", "Jovan Jose Asker Fredy", "D1; D2 Part 2.8", "D1 Fig. 1", "D1 Algorithm A", "D1 §5"),
    ("C6 Messaging Service", "Mohamed Aidja", "D2 Part 2.5", "Fig. 3", "Step lists", "Endpoints"),
    ("C7 Approval Service", "Danvanth Vanganuri", "D2 Part 2.6", "Fig. 3", "Fig. 5; Algorithm E", "Endpoints"),
    ("C8 Notification Service", "Danvanth Vanganuri", "D2 Part 2.7", "Fig. 2", "Fig. 6; Algorithm F", "enqueue(); webhook"),
    ("G1 Authentication middleware", "Danvanth Vanganuri (proposed)", "D2 Part 2.9", "No persistent data", "Step list", "requireAuth(), verifyToken() (I18)"),
    ("G2 Configuration", "Jovan Jose Asker Fredy (proposed)", "D2 Part 2.9", "No persistent data (env + files)", "Step list", "getConfig() (I20)"),
    ("G3 Logging and audit", "Mohamed Aidja (proposed)", "D2 Part 2.9", "AuditLog (Fig. 2)", "Step list", "log(), audit.record() (I19), /healthz"),
], ["20%", "17%", "15%", "17%", "15%", "16%"]))

A("<h3>1.4 Known gaps and open questions</h3>")
A(table(["ID", "Gap or question", "Current handling", "Owner"], [
    ("GQ-01", "Peer review feedback from the reviewing teams has not been merged into this draft.", "Part 6.2 is the template; Part 5's \"Changed by review\" column to be updated after class.", "All"),
    ("GQ-02", "Phrase list v1 content is not written. Ohio law (R.C. 4112) appears to add ancestry and military status to the federal protected classes; to confirm. Look-alike spellings outside the substitution map publish unflagged, and there is no report-a-listing feature.", "Categories in Part 2.4 include both pending confirmation; residual risk accepted (R-04).", "Jovan"),
    ("GQ-03", "A listing can never leave PUBLISHED: no withdraw, no filled-after-approval, no removal after its end date. No user story asks for it.", "Not designed (reverse check, Part 4.2). Ask instructor whether to add a story.", "Jovan"),
    ("GQ-04", "Managers and the unit registry are seeded by the team; a unit with no registered manager cannot complete US-03.", "422 UNIT_NOT_REGISTERED with guidance (EC-C7-08). Self-service registration deferred (D-09).", "Danvanth"),
    ("GQ-05", "Email provider (E1) not chosen: free-tier quota, webhook signing, and idempotency-key support unconfirmed.", "Design needs all three (EC-C8-02, 04, 06); choose in Week 8.", "Danvanth"),
    ("GQ-06", "Address normalization is rule-based, so unusual spellings can bypass the duplicate-listing 409.", "Accepted (EC-C3-05); geocoding API rejected for cost.", "Jovan"),
    ("GQ-07", "User_Stories did not number non-functional requirements; NFR-01 to NFR-07 are numbered here from D0 constraints. Priorities in Part 4 are the team's reading.", "Align with User_Stories if it states other priorities.", "All"),
    ("GQ-08", "A revoked verification or role change lasts until the 24 h token expires.", "Accepted in D-03 (EC-G1-04).", "Danvanth"),
], ["7%", "45%", "38%", "10%"]))

# ============================================================================ Part 2
A('<h2 class="pb">2. Finished Components, the D2 Diagrams</h2>')
A("<p>Figure 1 shows every component D2 finishes, the glue modules, and the interfaces revised in Part 2.10.</p>")
A(fig("D2_Fig1_Component_Map", "Figure 1. D2 component map. Glue modules G1 to G3 are called by every backend component; red labels are interfaces revised in D2."))
A("<h3>2.1 Data models for the components finished in D2</h3>")
A(fig("D2_Fig2_Data_Model_Identity_Notify", "Figure 2. Data model for C2 Identity, C8 Notification, and G3 audit. Requirement trace: US-01, US-03, US-05; AC-01.2; NFR-02, NFR-03, NFR-05, NFR-06.", "100%"))
A(fig("D2_Fig3_Data_Model_Messaging_Approval", "Figure 3. Data model for C6 Messaging and C7 Approval. Requirement trace: US-01, US-03, US-04; UC-02; AC-02.1, AC-02.2; NFR-05."))
A(table(["Decision", "Choice and reason", "Req."], [
    ("Hash, not token", "LoginLink stores SHA-256 of a 32-byte random token. A database read cannot be turned into a sign-in.", "NFR-03"),
    ("Status vs freshness", "Account.status records whether the mailbox was ever proven; the 12-month rule is computed from verified_at at request time (G1), so no nightly job has to flip rows.", "UC-01 A1"),
    ("Copies, not cross-reads", "C6 and C7 keep their own ListingCopy from I16 and I9, upserted only when source_version is newer (D1's guard), so neither reads C3's tables (D-11, D-12).", "D-12"),
    ("One thread per pair", "Unique (listing_id, sublessee_user_id) makes the first message from a student create exactly one thread, even under concurrent sends.", "US-01"),
    ("Approval uniqueness", "Partial unique index on listing_id WHERE status IN (PENDING, APPROVED): one live request per listing; after a rejection the owner may propose someone else.", "US-03"),
    ("Exactly one reminder", "reminder_sent_at is both the record and the guard (Algorithm E).", "AC-02.2"),
    ("to_email on Notification", "Resolved once at enqueue through I17a, so the worker needs no C2 call and the suppression check happens before the caller commits.", "NFR-06"),
    ("Append-only audit", "AuditLog has INSERT only for the app role; detail never contains email or message text.", "NFR-02, US-05"),
], ["18%", "70%", "12%"]))

# ---- C1
A("<h3>2.2 C1 Web Client</h3>")
A("<p><b>Data model: no persistent data.</b> The browser keeps only the session token and its expiry in sessionStorage, and unsent form drafts in sessionStorage keyed by route (cleared on successful submit). All state lives in the backend.</p>")
A("<p><b>Behavior: session states.</b> Signed out → (link requested) Link sent → (Confirm pressed, 200) Signed in → (401 or token expiry) Signed out, draft kept → (sign in again) draft restored. "
  "403 VERIFICATION_REQUIRED moves a signed-in student back to Link sent without losing the draft.</p>")
A(table(["Screen (route)", "Roles", "Calls", "Accessibility behavior"], [
    ("Sign in (/signin)", "Anyone", "POST /auth/link-requests", "Single labelled email field; 429 shows a countdown announced politely"),
    ("Confirm (/verify#token)", "Anyone", "POST /auth/link-confirmations", "Token read from the URL fragment (never sent to logs); Confirm button is the first focus"),
    ("New listing (/listings/new)", "Verified student", "POST /listings", "Native date inputs with yyyy-mm-dd hint; character counter; flagged phrases listed in text, not colour"),
    ("My listings (/listings/mine)", "Verified student", "GET /listings/mine", "Status as text (Published, In review, Rejected)"),
    ("Search (/search)", "Verified student", "GET /listings/search", "Result count announced (\"3 listings cover Jan 11 to Apr 30\"); results are a list of headings"),
    ("Listing (/listings/:id)", "Verified student", "GET /listings/{id}, POST /listings/{id}/messages", "Message box labelled; send result announced"),
    ("Messages (/threads, /threads/:id)", "Verified student", "GET /threads, GET and POST /threads/{id}/messages", "New messages announced; \"Propose as subleaser\" button for owners"),
    ("Approvals (/approvals)", "Owner, sublessee, manager", "GET, POST /approval-requests, POST /decision", "Reason field required and labelled when Reject is chosen"),
    ("Review queue (/review)", "Reviewer", "GET /review-queue, POST /listings/{id}/review", "Flagged phrases listed beside the description"),
], ["20%", "14%", "27%", "39%"]))
A("<p><b>Interface.</b> C1 offers I1 to users (HTML with ARIA landmarks, WCAG 2.1 AA) and consumes I2 to I6. It maps every error code to exactly one behavior:</p>")
A(table(["Code", "C1 behavior"], [
    ("400 INVALID_INPUT", "Mark the field named in error.field, announce in the ARIA live region, move focus to the first invalid field"),
    ("401 UNAUTHENTICATED", "Save draft, route to /signin, restore draft and focus after sign-in (EC-C1-03)"),
    ("403 VERIFICATION_REQUIRED / FORBIDDEN", "Start re-verification / show \"not allowed for your role\" page"),
    ("404", "Not-found page with a link back to search"),
    ("409", "Inline message with the current state from the response and a Refresh action"),
    ("410 EXPIRED", "\"This link has expired\" with a Send new link button (AC-01.2)"),
    ("422", "Message next to the action naming the rule (for example UNIT_NOT_REGISTERED explains who to contact)"),
    ("429, 503", "Disable the action until Retry-After passes; GETs retry once after 2 s; POSTs never auto-retry (EC-C1-04)"),
], ["26%", "74%"]))
A("<p><b>Accessibility rules</b> (US-04, NFR-01): every control is a native element with a visible label; every route change moves focus to the page heading; nothing is conveyed by colour alone; text contrast at least 4.5:1; all actions reachable by keyboard in visual order. Checked with axe-core in CI and a manual NVDA and VoiceOver pass on the search-and-message path.</p>")

# ---- C2
A("<h3>2.3 C2 Identity Service</h3>")
A("<p><b>Data model:</b> Account, LoginLink, SessionClaims (Fig. 2). <b>State machine:</b> Fig. 4. <b>Error paths:</b> Fig. 8.</p>")
A(fig("D2_Fig4_State_Account_Listing", "Figure 4. Account (C2) and Listing (C3) state machines, with error outcomes. Requirement trace: US-01, US-05; UC-01 A1; AC-01.2, AC-01.3, AC-01.4."))
A("<h4>Algorithm C: one-time link request and confirmation</h4>")
A(kv([
    ("What and why", "Prove mailbox ownership for sign-up and every sign-in with one mechanism (D-02, D-09), and issue a 24 h session token carrying role and verification (D-03)."),
    ("Inputs / outputs", "Request in: email (3 to 254 chars). Out: 202 {status: PENDING}. Confirm in: token (43-char base64url), firstName? (1 to 50, required when the account has none). Out: 200 {status: VERIFIED, verifiedAt, role, sessionToken, expiresAt}."),
    ("Method (request)", "1. Trim, lowercase, NFKC. 2. Eligible if the domain after the last @ is exactly mail.uc.edu with no + in the local part, or the address is a seeded account; else 422 NOT_ELIGIBLE. "
     "3. If 3 LoginLink rows for this account were issued in the last 60 min: 429 with Retry-After. 4. BEGIN; upsert Account (new students start PENDING); set superseded_at on unused, unexpired links; insert LoginLink with SHA-256 of a fresh 32-byte random token and expires_at = now + 24 h. "
     "5. enqueue(tx, LOGIN_LINK to the userId, link = APP_BASE_URL/verify#token). SUPPRESSED: ROLLBACK, 422 EMAIL_UNDELIVERABLE. Throws: ROLLBACK, 503. 6. COMMIT, 202."),
    ("Method (confirm)", "1. Hash the token, look up LoginLink; none: 400 INVALID_TOKEN. 2. superseded or now ≥ expires_at: 410 EXPIRED. 3. firstName missing when needed: 400 INVALID_INPUT. "
     "4. BEGIN; <code>UPDATE login_link SET used_at = now() WHERE link_id = $1 AND used_at IS NULL</code>; 0 rows: ROLLBACK, 400 INVALID_TOKEN. 5. Account status VERIFIED, verified_at = now (re-verification resets the 12-month clock), first_name if given; audit ACCOUNT_VERIFIED. COMMIT. "
     "6. Sign HS256 JWT {sub, role, verified, verifiedAt, iat, exp = iat + 24 h} with the current kid."),
    ("Complexity", "Constant work per call: one indexed count, a few row writes, one hash, one signature. Independent of account count."),
    ("Why this one", "Token hash rather than token: a leaked table gives no sign-ins. POST to confirm rather than GET: mail scanners open links (R-03). Superseding old links: only the newest email works, so a stale forwarded email cannot sign in. Alternatives (UC SSO, passwords) were rejected in D-02 and D-09."),
    ("Edge cases", "EC-C2-01 to EC-C2-08."),
]))
A(table(["Endpoint or signature", "Inputs", "Success", "Errors"], [
    ("POST /api/v1/auth/link-requests (no token)", "email: string, required, 3 to 254", "202 {status: \"PENDING\"}", "400 INVALID_INPUT; 422 NOT_ELIGIBLE; 422 EMAIL_UNDELIVERABLE; 429 RATE_LIMITED + Retry-After; 503 NOTIFY_UNAVAILABLE"),
    ("POST /api/v1/auth/link-confirmations (no token)", "token: string, required, 43 chars; firstName: string 1 to 50, required if none stored", "200 {status, verifiedAt, role, sessionToken, expiresAt}", "400 INVALID_INPUT; 400 INVALID_TOKEN; 410 EXPIRED; 503 DB_UNAVAILABLE"),
    ("getContacts(userIds: UUID[]) (I17a, C8 only)", "1 to 100 ids", "{userId, email, firstName}[]; unknown ids omitted", "throws DbUnavailableError"),
    ("getEligibility(userIds: UUID[]) (I17b, C7 only)", "1 to 100 ids", "{userId, role, verifiedFresh: bool}[]; unknown ids omitted", "throws DbUnavailableError"),
], ["28%", "24%", "22%", "26%"]))

# ---- C4
A("<h3>2.4 C4 Compliance Screener</h3>")
A("<p><b>Data model: no persistent data.</b> The phrase list is a versioned file in the repository, loaded once at startup by G2:</p>")
A('<pre>config/phrase_list.json\n{ "version": "2026.10-v1",\n  "entries": [ { "phrase": "no kids", "category": "FAMILIAL_STATUS" },\n               { "phrase": "adults only", "category": "FAMILIAL_STATUS" }, ... ] }\n'
  'category: RACE | COLOR | RELIGION | SEX | FAMILIAL_STATUS | NATIONAL_ORIGIN | DISABILITY\n          | ANCESTRY | MILITARY_STATUS   (Ohio, pending confirmation, GQ-02)\n          | OBFUSCATION                 (produced by the screener, never in the file)</pre>')
A("<h4>Algorithm D: Fair Housing phrase screen</h4>")
A(kv([
    ("What and why", "Flag preference language before a listing can publish (US-05, NFR-04) and say exactly which phrase matched (AC-01.3)."),
    ("Inputs / outputs", "In: text, 0 to 2000 chars. Out: ScreenResult {flagged: bool, matches: [{phrase, category, start, end}], listVersion: string}. Throws ScreenerUnavailableError when no list is loaded."),
    ("Method", "1. Build a normalized copy: NFKC, lowercase, curly quotes to straight, whitespace runs to one space, keeping an index map back to original offsets. "
     "2. Build a folded copy with common substitutions (0→o, 1→i, 3→e, 4→a, 5→s, 7→t, @→a, $→s). 3. For each entry (normalized at load), find every occurrence in both copies where the characters before and after are not letters or digits (text start and end count as boundaries). "
     "4. Any token mixing Latin with Cyrillic or Greek letters adds a match with category OBFUSCATION. 5. Map matches to original offsets, remove duplicates, sort by start. flagged = matches is not empty."),
    ("Complexity", "Literal search: at most 2000 characters x about 300 entries, under 5 ms in Node. No regular expression is built from data, so there is no backtracking blow-up and the 2 s I7 budget cannot be reached by input."),
    ("Why this one", "See R-04. A regex list risks ReDoS; a hosted moderation API sends listing text to a third party and adds cost; an ML classifier needs labelled data and cannot explain a miss (D-04)."),
    ("Edge cases", "EC-C4-01 to EC-C4-05; caller behavior EC-C3-06."),
]))
A("<p><b>Interface (I7, revised):</b> <code>screen(text: string): ScreenResult</code>, throws <code>ScreenerUnavailableError</code>. C3 wraps the call with a 2 s timer and treats a throw or timeout as SCREENER_UNAVAILABLE. D0's single <code>offset</code> becomes <code>start</code>/<code>end</code> so C1 can highlight the phrase.</p>")

# ---- C6
A("<h3>2.5 C6 Messaging Service</h3>")
A("<p><b>Data model:</b> ListingCopy, Thread, Message (Fig. 3).</p>")
A("<h4>Behavior: step lists</h4>")
A("<p><b>Start or continue a thread</b> (POST /listings/{id}/messages): 1. G1 requires a verified, fresh caller. 2. Validate body (trim, 1 to 2000) and clientMessageId. 3. Load ListingCopy; missing: 403 LISTING_UNAVAILABLE. "
  "4. Caller is the owner: 422 SELF_MESSAGE. 5. BEGIN; insert Thread ON CONFLICT (listing_id, sublessee_user_id) DO NOTHING, then select it; insert Message ON CONFLICT (sender_user_id, client_message_id) DO NOTHING (a retry returns the original); update last_message_at; COMMIT. "
  "6. After commit, if the recipient's alerted_at is null or older than 15 min: enqueue NEW_MESSAGE {listingId, threadId, senderFirstName} and set alerted_at; enqueue failure logs WARN (EC-C6-06). 7. 201.</p>")
A("<p><b>Reply</b> (POST /threads/{id}/messages): same steps, but step 3 loads the thread and returns 404 THREAD_NOT_FOUND if the caller is not a participant. "
  "<b>Consume I16:</b> upsert ListingCopy by listing_id when source_version is newer; otherwise ignore and ack.</p>")
A(table(["Endpoint", "Inputs", "Success", "Errors"], [
    ("POST /api/v1/listings/{id}/messages", "id: UUID path; body: string 1 to 2000; clientMessageId: UUID", "201 {threadId, messageId, sentAt}", "400 INVALID_INPUT; 401; 403 VERIFICATION_REQUIRED; 403 LISTING_UNAVAILABLE + Retry-After; 422 SELF_MESSAGE; 503"),
    ("POST /api/v1/threads/{id}/messages", "id: UUID path; body; clientMessageId", "201 {threadId, messageId, sentAt}", "400; 401; 403 VERIFICATION_REQUIRED; 404 THREAD_NOT_FOUND; 503"),
    ("GET /api/v1/threads", "none", "200 {threads: [{threadId, listingId, addressSummary, otherFirstName, role: OWNER|SUBLESSEE, lastMessageAt}]}", "401; 403 VERIFICATION_REQUIRED; 503"),
    ("GET /api/v1/threads/{id}/messages", "before?: datetime; limit?: 1 to 50 (default 50)", "200 {messages: [{messageId, senderFirstName, mine: bool, body, sentAt}]}", "400; 401; 403; 404 THREAD_NOT_FOUND; 503"),
], ["26%", "26%", "26%", "22%"]))

# ---- C7
A("<h3>2.6 C7 Approval Service</h3>")
A("<p><b>Data model:</b> UnitRegistry, ListingCopy, ApprovalRequest (Fig. 3). <b>State machine:</b> Fig. 5.</p>")
A(fig("D2_Fig5_State_Approval", "Figure 5. ApprovalRequest state machine. Requirement trace: US-03; UC-02; AC-02.1, AC-02.2."))
A("<p><b>Consume I9:</b> upsert ListingCopy if source_version is newer; look up UnitRegistry by address_norm; set unit_status. If REGISTERED and this is the first copy for the listing, enqueue NEW_LISTING to the manager (key <code>NEW_LISTING:{listingId}</code>) in the same transaction; if UNREGISTERED_UNIT, ack without a notice (D0 I9).</p>")
A("<p><b>Proposal:</b> 1. G1 verified caller. 2. Load ListingCopy (missing: 409 LISTING_NOT_READY); caller must be owner_user_id (403 NOT_LISTING_OWNER). 3. sublessee ≠ owner (422 SELF_PROPOSAL). 4. unit_status REGISTERED (422 UNIT_NOT_REGISTERED). "
  "5. getEligibility([sublesseeUserId]) must return verifiedFresh (422 SUBLESSEE_NOT_VERIFIED). 6. BEGIN; insert PENDING (partial unique index: 409 PENDING_EXISTS or ALREADY_APPROVED); enqueue SUBLEASE_PROPOSED to the manager; COMMIT; 201.</p>")
A("<p><b>Decision:</b> 1. G1 verified caller with role MANAGER. 2. BEGIN; <code>SELECT ... FOR UPDATE</code>; caller must be manager_user_id (403 NOT_UNIT_MANAGER). 3. <code>UPDATE ... SET status, reason, decided_at = now() WHERE request_id = $1 AND status = 'PENDING'</code>; 0 rows: 409 ALREADY_DECIDED. "
  "4. enqueue DECISION to owner and sublessee (keys <code>DECISION:{requestId}:{userId}</code>); audit APPROVAL_DECIDED. 5. COMMIT; 200. Any failure in 3 or 4 rolls back (503).</p>")
A("<h4>Algorithm E: exactly-one reminder (AC-02.2)</h4>")
A(kv([
    ("What and why", "Send one reminder to the manager when a request has been PENDING for 5 business days, never two (AC-02.2)."),
    ("Inputs / outputs", "In: clock, holidays.json. Out: REMINDER notices; reminder_sent_at set on each reminded request."),
    ("Method", "Runs daily at REMINDER_RUN_AT (09:00 America/New_York) inside the Node process. 1. <code>pg_try_advisory_lock(7001)</code>; not acquired: exit (another instance runs it). "
     "2. Select PENDING requests with reminder_sent_at null. 3. For each where businessDaysBetween(created_at, now) ≥ 5 (Mon to Fri, holidays skipped, counting from the next business day): BEGIN; "
     "<code>UPDATE ... SET reminder_sent_at = now() WHERE request_id = $1 AND status = 'PENDING' AND reminder_sent_at IS NULL</code>; if 1 row, enqueue REMINDER (key <code>REMINDER:{requestId}</code>); COMMIT. 4. Unlock."),
    ("Complexity", "O(p) for p pending requests, a few dozen at campus scale; the date arithmetic is O(days) per request with a 1-year cap."),
    ("Why this one", "See R-07. Three independent guards make a second reminder impossible: the advisory lock, the conditional UPDATE, and the idempotency key."),
    ("Edge cases", "EC-C7-01, 02, 04, 05."),
]))
A(table(["Endpoint", "Inputs", "Success", "Errors"], [
    ("POST /api/v1/approval-requests", "listingId: UUID; sublesseeUserId: UUID (taken from a C6 thread)", "201 {requestId, status: PENDING, createdAt}", "400; 401; 403 VERIFICATION_REQUIRED; 403 NOT_LISTING_OWNER; 409 LISTING_NOT_READY, PENDING_EXISTS, ALREADY_APPROVED; 422 SELF_PROPOSAL, UNIT_NOT_REGISTERED, SUBLESSEE_NOT_VERIFIED; 503"),
    ("POST /api/v1/approval-requests/{id}/decision", "decision: APPROVE | REJECT; reason: string 1 to 500, required for REJECT", "200 {requestId, status, decidedAt}", "400 INVALID_INPUT; 401; 403 NOT_UNIT_MANAGER; 404; 409 ALREADY_DECIDED; 503"),
    ("GET /api/v1/approval-requests", "none (results limited to requests where the caller is owner, sublessee, or manager)", "200 {requests: [{requestId, listingId, unitLabel, status, myRole, createdAt, decidedAt?}]}", "401; 403 VERIFICATION_REQUIRED; 503"),
], ["24%", "26%", "22%", "28%"]))

# ---- C8
A("<h3>2.7 C8 Notification Service</h3>")
A("<p><b>Data model:</b> Notification, Suppression, WebhookReceipt (Fig. 2). <b>State machine:</b> Fig. 6.</p>")
A(fig("D2_Fig6_State_Notification_Outbox", "Figure 6. Notification and outbox-row state machines, including every retry and failure transition. Requirement trace: AC-01.1, AC-02.1; NFR-05, NFR-06."))
A("<h4>Algorithm F: send worker</h4>")
A(kv([
    ("What and why", "Deliver every outbound email within the 5-minute budgets without sending duplicates or flooding UC Mail (AC-01.1, AC-02.1, NFR-05, NFR-06)."),
    ("Method", "Every NOTIFY_POLL_MS (5 s): 1. Reset rows SENDING for over 2 min to QUEUED (reaper). 2. Claim up to 20 rows <code>WHERE status = 'QUEUED' AND next_attempt_at &lt;= now() ORDER BY priority, created_at FOR UPDATE SKIP LOCKED</code>; set SENDING, attempts + 1. "
     "3. Render the template; POST to E1 with Idempotency-Key = idempotency_key and tag notificationId, 5 s timeout. 4. 2xx: SENT, provider_msg_id, clear params.link. 5xx, 429, timeout with attempts &lt; 4: QUEUED, next_attempt_at = now + [30, 60, 120] s (or Retry-After if longer). "
     "4xx or 4th attempt: FAILED, last_error, clear params.link, ERROR log."),
    ("Webhook", "POST /api/v1/webhooks/email: 1. Verify HMAC signature and timestamp within 5 min, else 401. 2. Insert WebhookReceipt; duplicate provider_event_id: 200 no-op. 3. Find the row by the notificationId tag; unknown: 200. 4. Advance status only forward (SENT &lt; DELIVERED &lt; BOUNCED); DEFERRED changes nothing; BOUNCED inserts Suppression(email). 5. 200."),
    ("Complexity", "One indexed claim query per cycle; at most 20 sends in flight. A few hundred emails a day is far below one worker's capacity."),
    ("Why this one", "Same SKIP LOCKED pattern as D1's outbox, so one technique for both queues and no broker (D-05, NFR-07)."),
    ("Edge cases", "EC-C8-01 to EC-C8-09."),
]))
A(table(["Interface", "Inputs", "Success", "Errors"], [
    ("enqueue(tx, req) (I10, I11, I12, revised)", "tx: caller's transaction; req: {templateId, toUserId, params (typed per template), idempotencyKey}", "{notificationId, state: QUEUED | SUPPRESSED}; existing row if the key was seen", "throws TemplateParamError; throws EnqueueError (database); caller decides (C2 503, C6 log, C7 503)"),
    ("POST /api/v1/webhooks/email (I13 in)", "headers: signature, timestamp; body: {eventId, messageId, tag, event: DELIVERED | DEFERRED | BOUNCED, timestamp}", "200 (also for duplicates and unknown tags)", "400 malformed; 401 bad signature or stale timestamp"),
], ["24%", "34%", "22%", "20%"]))
A(table(["templateId", "params (typed)", "Recipient", "idempotencyKey", "Priority"], [
    ("LOGIN_LINK", "{link: URL, expiresAt: datetime}", "the requesting account", "LOGIN_LINK:{linkId}", "1"),
    ("DECISION", "{requestId, decision, unitLabel}", "owner and sublessee", "DECISION:{requestId}:{userId}", "2"),
    ("SUBLEASE_PROPOSED", "{requestId, unitLabel}", "manager", "PROPOSED:{requestId}", "2"),
    ("REMINDER", "{requestId, unitLabel, businessDaysPending}", "manager", "REMINDER:{requestId}", "2"),
    ("NEW_LISTING", "{listingId, unitLabel, availableStart, availableEnd}", "manager", "NEW_LISTING:{listingId}", "3"),
    ("NEW_MESSAGE", "{listingId, threadId, senderFirstName}", "other participant", "NEW_MESSAGE:{threadId}:{userId}:{15-min window}", "3"),
], ["17%", "33%", "17%", "25%", "8%"]))

# ---- C3/C5 changes
A("<h3>2.8 Changes to C3 and C5 since D1</h3>")
A("<p>D1 is not edited. These items supersede the named D1 parts; each traces to a self-audit item in Part 6.1 and a rationale entry.</p>")
A(table(["#", "Change", "Supersedes", "Why", "Ref"], [
    ("1", "ListingEvent gains consumer {C5_INDEX, C6_COPY, C7_APPROVAL}, status {PENDING, DISPATCHED, FAILED}, attempts, next_attempt_at, last_error. Each publish or release writes three rows; each is retried at +5 s, +30 s, +2 min, then FAILED (Fig. 6).", "D1 Fig. 1 ListingEvent; Algorithm B outbox drain", "D1's drain skipped I16 and I9; per-row isolation", "R-01, PR-S02"),
    ("2", "Relay polls every 5 s (OUTBOX_POLL_MS), not 30 s.", "D1 Algorithm B", "30 s plus one retry misses the 60 s budget", "R-02, PR-S01"),
    ("3", "Listing gains hold_reason {FLAGGED, SCREENER_UNAVAILABLE}? and screen_list_version.", "D1 Fig. 1 Listing", "Reviewer sees why a listing is held; verdict tied to a list version", "EC-C4-02"),
    ("4", "New GET /api/v1/listings/{id} (PUBLISHED listings to verified callers; any status to the owner; else 404) and GET /api/v1/listings/mine.", "D1 §5", "No read endpoint existed for the listing page or owner status", "PR-S11"),
    ("5", "endDate must be after today (America/New_York).", "D1 §5 POST /listings", "A listing that ended can never match", "EC-C3-02"),
    ("6", "Review RELEASE and REJECT write an AuditLog row in the same transaction.", "D1 Algorithm B review", "Who decided is recorded", "R-10"),
    ("7", "C5 unchanged; its I8 handler is the C5_INDEX consumer above.", "none", "", ""),
], ["4%", "44%", "18%", "24%", "10%"]))

# ---- Glue
A("<h3>2.9 Glue components</h3>")
A("<h4>G1 Authentication middleware</h4>")
A("<p><b>Data model: no persistent data</b> (signing keys come from G2). <b>Behavior:</b> 1. Read <code>Authorization: Bearer &lt;jwt&gt;</code>; missing or malformed: 401. "
  "2. <code>jwtVerify</code> (jose) with algorithms [HS256] and the key for the header kid (current or previous); any failure: 401 with no detail. 3. Build claims. "
  "4. verifiedFresh = verified and (role ≠ STUDENT or verifiedAt + 12 months &gt; now). 5. Route requires verified and not verifiedFresh: 403 VERIFICATION_REQUIRED; route requires a role the claims lack: 403 FORBIDDEN. 6. Attach claims to the request. "
  "Applied to every route except link-requests, link-confirmations, webhooks, and /healthz.</p>")
A("<p><b>Interface (I18):</b> <code>requireAuth(opts?: {verified?: boolean; roles?: Role[]}): RequestHandler</code>; <code>verifyToken(jwt: string): Claims</code> throws <code>AuthError{code: UNAUTHENTICATED}</code>. Edge cases EC-G1-01 to 05.</p>")
A("<h4>G2 Configuration</h4>")
A("<p><b>Data model: no persistent data in the database.</b> Secrets come from host environment variables; everything else is a versioned file in <code>config/</code>, so a change is a reviewed commit and a deploy. "
  "<b>Behavior:</b> at process start, parse all sources with one zod schema; on any failure log FATAL with the key names only and exit 1, so the host keeps the previous deploy serving. The result is frozen; there is no runtime reload. Seeds are applied by a migration script, not at startup.</p>")
A(table(["Key", "Type and range", "Used by"], [
    ("DATABASE_URL", "postgres URL, required", "all (I15)"),
    ("JWT_KEYS, JWT_CURRENT_KID", "JSON {kid: secret ≥ 32 bytes}, 1 or 2 keys; kid present in JWT_KEYS", "C2, G1"),
    ("EMAIL_API_KEY, EMAIL_WEBHOOK_SECRET, EMAIL_FROM", "strings, required", "C8"),
    ("APP_BASE_URL", "https URL", "C2 (link), C8 (templates)"),
    ("OUTBOX_POLL_MS, NOTIFY_POLL_MS", "int 1000 to 10000, default 5000", "C3 relay, C8 worker"),
    ("SEND_TIMEOUT_MS / SCREEN_TIMEOUT_MS", "int 1000 to 10000, default 5000 / int 500 to 2000, default 2000", "C8 / C3"),
    ("REMINDER_RUN_AT", "HH:MM in America/New_York, default 09:00", "C7"),
    ("LOG_LEVEL", "debug | info | warn | error", "G3"),
    ("config/phrase_list.json, holidays.json, seed_accounts.json, seed_units.json", "schemas in Part 2.4; [date]; [{email, role, firstName}]; [{addressNorm, managerEmail, unitLabel}]", "C4; C7; C2 and C7 migrations"),
], ["32%", "44%", "24%"]))
A("<p><b>Interface (I20):</b> <code>getConfig(): Readonly&lt;Config&gt;</code>; <code>loadConfig(env, dir): Config</code> throws <code>ConfigError{keys: string[]}</code>. Edge cases EC-G2-01 to 04.</p>")
A("<h4>G3 Logging and audit</h4>")
A("<p><b>Data model:</b> AuditLog (Fig. 2). Operational logs are not stored by us: JSON lines to stdout, kept by the host's log stream. "
  "<b>Behavior:</b> request middleware assigns requestId (also returned in every error body) and writes one line per request {at, level, requestId, method, route, status, ms, userId?}. "
  "Components log named events with allow-listed fields only; email becomes a short hash; tokens, links, message bodies, and descriptions are never logged. "
  "audit.record inserts in the caller's transaction. GET /healthz runs <code>SELECT 1</code> and returns 200 {db: \"ok\"} or 503.</p>")
A("<p><b>Interface (I19):</b> <code>log.info|warn|error(event: string, fields: Partial&lt;Record&lt;AllowedKey, string | number | boolean&gt;&gt;): void</code> (never throws); "
  "<code>audit.record(tx, {actorUserId, action, entityType, entityId, detail}): Promise&lt;void&gt;</code> throws on failure so the caller rolls back. Operations: <code>npm run redrive -- --outbox|--notification &lt;id&gt;</code> resets a FAILED row and writes NOTIFICATION_REDRIVEN. Edge cases EC-G3-01 to 04.</p>")

# ---- D0 interface revisions
A("<h3>2.10 Revisions to D0 interfaces</h3>")
A(table(["Interface", "Problem in D0", "Revision in D2"], [
    ("I2", "No field supplied the first name that I11 sends; link-requests returned the verification status of any address, which reveals whether an account exists.", "link-confirmations takes firstName when none is stored; link-requests always returns 202 PENDING for eligible addresses."),
    ("I3", "One interface mixed student create and reviewer decisions; invalid input was 422 while D1 used 400.", "Split into I3a (create, read, mine) and I3b (review queue, review). Validation failures are 400 (R-08)."),
    ("I5", "Empty or oversized body was 422; no idempotency; no reply path for the owner.", "400 for body; clientMessageId for safe retries; POST /threads/{id}/messages for replies."),
    ("I6", "REJECT without reason was 422.", "400 INVALID_INPUT (schema rule); 422 kept for business refusals."),
    ("I7", "Single offset; unavailability was implicit.", "start and end offsets; explicit ScreenerUnavailableError."),
    ("I8, I9, I16", "One event, with fan-out by the relay; eventId-based upsert; I9 sent the raw address, which C7 cannot match against its registry.", "One outbox row per consumer; upsert by listing_id with source_version (D1 guard); I9 carries addressNorm and addressSummary."),
    ("I10, I11, I12", "Three signatures; I10 passed a raw email; I12 params were an untyped object.", "One enqueue(tx, NotificationRequest) addressed by toUserId, params typed per template (R-06)."),
    ("I13", "Webhook matched rows by provider messageId, which may not be saved yet.", "Rows matched by the notificationId tag; signature plus 5-minute timestamp window; event-id dedupe."),
    ("I17", "One lookup returned email, role, verified, firstName to both C7 and C8, so C7 received emails it never uses.", "I17a getContacts (C8 only) and I17b getEligibility (C7 only, no email) (R-05)."),
    ("New I18, I19, I20", "Glue behavior was implicit in D0.", "verifyToken (G1), log and audit.record (G3), getConfig (G2)."),
], ["12%", "44%", "44%"]))

# ---- timing
A("<h3>2.11 Timing budgets rechecked</h3>")
A("<p>D0's worst cases left out the send timeout and the poll delay after each backoff. Recomputed with a 5 s poll, 5 s send timeout, and the retry schedules above:</p>")
A(table(["Requirement", "Budget", "Worst-case path", "D2 worst case"], [
    ("AC-01.1 search", "60 s", "relay poll 5 + C5 fails, wait 5 + poll 5 + fails, wait 30 + poll 5 + succeeds", "50 s (D0 said 41 s)"),
    ("AC-01.1 notice", "5 min", "relay 5 + C7 enqueue + worker poll 5 + three failed sends (5 s timeout each) with waits 30, 60, 120 and a poll after each + 4th send", "about 251 s = 4.2 min"),
    ("AC-01.1 notice, both chains retrying", "5 min", "as above plus C7 delivery failing twice (adds 45 s)", "about 296 s = 4.9 min; any further retry misses and is logged FAILED"),
    ("AC-02.1", "5 min", "enqueue in decision TX + worker poll 5 + the send chain", "about 246 s = 4.1 min (D0 said 3.5 min)"),
    ("AC-02.2", "1 reminder after 5 business days", "first daily run after day 5", "same day or next business morning"),
], ["22%", "12%", "44%", "22%"]))


# ============================================================================ Part 3
A('<h2 class="pb">3. Edge Cases and Error Handling</h2>')
A("<p>Every component and glue module has at least one row in each of the four categories. <b>Behavior</b> is one of retry, degrade, fall back, or surface an error (or n/a where the design makes the case impossible or idempotent). "
  "Figures 6, 7, and 8 draw the error paths; Fig. 7 is the riskiest flow (legal exposure plus two timing budgets).</p>")
A(table(["ID", "Comp.", "Category", "Edge case", "Design decision", "Behavior", "Handler", "Recov."],
        EDGE, ["7%", "4.5%", "8%", "19%", "36%", "8.5%", "10%", "7%"], "edge"))
A(fig("D2_Fig7_Error_Paths_Publish", "Figure 7. Publish flow with every decision and failure outcome. Requirement trace: US-01, US-05; AC-01.1, AC-01.3, AC-01.4; NFR-04, NFR-06. Edge cases EC-C3-01 to 08, EC-C4-05, EC-C7-08, EC-C8-01 to 08.", "78%"))
A(fig("D2_Fig8_Error_Paths_SignIn", "Figure 8. Sign-in and verification flow with error paths. Requirement trace: US-01; UC-01 steps 2 to 6; AC-01.2; NFR-03, NFR-05. Edge cases EC-C2-01 to 08.", "68%"))

# ============================================================================ Part 4
A('<h2 class="pb">4. Requirements Traceability</h2>')
A("<h3>4.1 Forward check: requirement to design element</h3>")
A("<p>Story and criterion text is paraphrased from User_Stories and D0. Every row names an entity, endpoint, algorithm, or figure and cites edge-case IDs; the last column explains each gap.</p>")
A(table(["ID", "Requirement (short)", "Priority", "Design elements", "How", "Gap"],
        TRACE, ["6.5%", "18%", "6.5%", "26%", "26%", "17%"]))
A("<h3>4.2 Reverse check: design element to requirement</h3>")
A("<p>Every component C1 to C8 traces to a story (D0 Part 3). The check below covers what D1 and D2 added beyond D0, which is where scope creep would appear.</p>")
A(table(["Design element", "Requirement behind it", "Verdict"], REVERSE, ["32%", "38%", "30%"]))

# ============================================================================ Part 5
A('<h2 class="pb">5. Design Rationale</h2>')
A("<p>Entries cover D1 and D2 decisions; D0 decisions D-01 to D-12 are referenced, not repeated. \"Changed by review\" marks entries the peer review altered; it will be updated after class (GQ-01). Entries marked self-audit come from checking D1 against D0 before the review.</p>")
A(table(["ID", "Decision", "Trade-off accepted", "Builds on", "Changed by review"],
        RATIONALE, ["5%", "40%", "33%", "12%", "10%"]))

# ============================================================================ Part 6
A('<h2 class="pb">6. Peer Design Review Notes</h2>')
A('<div class="note"><b>To complete in class.</b> Parts 6.2 to 6.4 are templates: record each reviewing team\'s feedback as action items, apply the must-fix items to D2 before submitting, then update Part 5\'s last column. Part 6.1 lists items the team found itself while walking D0 box by box before the review; they are not peer feedback.</div>')
A("<h3>6.1 Self-audit action items (pre-review)</h3>")
A(table(["ID", "Criterion", "Issue", "Raised by", "Action", "Owner", "Priority", "Due", "Status"],
        AUDIT, ["6%", "9%", "22%", "8%", "22%", "8%", "9%", "6%", "10%"]))
A("<h3>6.2 Feedback received</h3>")
A("<p>One block per reviewing team. Criterion is one of completeness, feasibility, clarity, risk. Priority is must-fix, worth considering, or out of scope for now.</p>")
for letter in ("A", "B"):
    team = "Team ____"
    A(f"<h4>Reviewed by {team} (items PR-{letter}xx)</h4>")
    A(table(["ID", "Criterion", "Issue (as raised)", "Action", "Owner", "Priority", "Due"],
            [(f"PR-{letter}0{i}", "", "", "", "", "", "") for i in range(1, 4)],
            ["7%", "11%", "30%", "26%", "10%", "9%", "7%"]))
A("<h3>6.3 Summary</h3>")
A(table(["Item", "Notes"], [
    ("Criterion with the most feedback", "____ (count by criterion across 6.2)"),
    ("Must-fix items applied before submission", "____ (list IDs and the D2 part changed)"),
], ["30%", "70%"]))
A("<h3>6.4 Top two issues we raised while reviewing other teams</h3>")
A(table(["#", "Team reviewed", "Issue we raised", "Criterion", "Why it mattered"], [("1", "", "", "", ""), ("2", "", "", "", "")],
        ["4%", "16%", "40%", "12%", "28%"]))

BODY = "\n".join(parts)
HTML = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{BODY}</body></html>"
with open(os.path.join(HERE, "D2_Detailed_Design.html"), "w") as f:
    f.write(HTML)

# ============================================================================ Peer_Review_Notes.md
md = ["# Peer Review Notes: Verified Student Sublease Marketplace (Design D2)", "",
      "Team: Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja", "",
      "Criterion: completeness, feasibility, clarity, risk. Priority: must-fix, worth considering, out of scope for now.", "",
      "## 1. Self-audit action items (pre-review, not peer feedback)", "",
      "| ID | Criterion | Issue | Raised by | Action | Owner | Priority | Due | Status |", "|---|---|---|---|---|---|---|---|---|"]
md += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in AUDIT]
md += ["", "## 2. Feedback received", ""]
for n in ("A", "B"):
    md += [f"### Reviewed by Team ____ (items PR-{n}xx)", "", "| ID | Criterion | Issue (as raised) | Action | Owner | Priority | Due |", "|---|---|---|---|---|---|---|"]
    md += [f"| PR-{n}0{i} |  |  |  |  |  |  |" for i in range(1, 4)] + [""]
md += ["## 3. Summary", "", "- Criterion with the most feedback: ____", "- Must-fix items applied to D2 before submission: ____", "",
       "## 4. Top two issues we raised while reviewing other teams", "", "| # | Team reviewed | Issue we raised | Criterion | Why it mattered |", "|---|---|---|---|---|",
       "| 1 |  |  |  |  |", "| 2 |  |  |  |  |", ""]
with open(os.path.join(HERE, "Peer_Review_Notes.md"), "w") as f:
    f.write("\n".join(md))

subprocess.run(["wkhtmltopdf", "--enable-local-file-access", "-q", "--page-size", "Letter",
                "--margin-top", "16mm", "--margin-bottom", "14mm", "--margin-left", "13mm", "--margin-right", "13mm",
                "--header-font-name", "Inter", "--header-font-size", "7", "--header-spacing", "4",
                "--header-left", "D2_Detailed_Design | Verified Student Sublease Marketplace",
                "--footer-font-name", "Inter", "--footer-font-size", "7", "--footer-right", "page [page] of [topage]",
                "D2_Detailed_Design.html", "D2_Detailed_Design.pdf"], cwd=HERE)
import json
json.dump(FIGPAGES, open(os.path.join(HERE, "figpages.json"), "w"), indent=1)
print("built")
