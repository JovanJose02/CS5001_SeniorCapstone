"""Graphviz sources for the D2 figures. Run: python3 diagrams.py  -> figs/*.dot, figs/*.png"""
import os, subprocess, html

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)

TITLE = "Verified Student Sublease Marketplace"
GOAL = ("Goal: Let UC students fill or find term-length subleases safely by limiting the marketplace to verified "
        "@mail.uc.edu students, matching listings to exact co-op dates, holding discriminatory listings for review, "
        "and giving property managers an approve/reject step before move-in.")

FONT = "Inter"
MONO = "DejaVu Sans Mono"

COL = {  # owner colours (same family as D1)
    "C2": "#E3EAF6", "C3": "#E6F2E6", "C5": "#ECE6F5", "C6": "#E0F2F1", "C7": "#FFF6DC",
    "C8": "#F8EADF", "G": "#EEEEEE", "T": "#F5F5F5",
}
RED = "#B3261E"
GREEN = "#2E7D32"


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines


def header(fig, legend_lines, width=100):
    goal = "".join(html.escape(l) + '<BR ALIGN="LEFT"/>' for l in wrap(GOAL, width))
    leg = "".join(html.escape(l) + '<BR ALIGN="LEFT"/>' for l in wrap(" ".join(legend_lines), 112))
    return (f'<<TABLE BORDER="0" CELLPADDING="1" CELLSPACING="0">'
            f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="14"><B>{html.escape(TITLE)}</B></FONT></TD></TR>'
            f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="12.5"><B>{html.escape(fig)}</B></FONT></TD></TR>'
            f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">{goal}</FONT></TD></TR>'
            f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10" COLOR="#444444"><B>Conventions: </B>{leg}</FONT></TD></TR>'
            f'<TR><TD> </TD></TR></TABLE>>')


def graph_open(name, fig, legend, rankdir="LR", extra=""):
    return (f'digraph {name} {{\n'
            f'  graph [fontname="{FONT}", rankdir={rankdir}, labelloc=t, labeljust=l, nodesep=0.3, ranksep=0.5, '
            f'pad=0.2, label={header(fig, legend)} {extra}];\n'
            f'  node [fontname="{FONT}", fontsize=11];\n'
            f'  edge [fontname="{FONT}", fontsize=10, color="#333333"];\n')


def entity(nid, title, fields, color, dashed=False, note=None):
    """fields: list of (name, type). Two cells per row, proportional font, so boxes stay narrow."""
    style = 'STYLE="rounded,dashed"' if dashed else 'STYLE="rounded"'
    rows = "".join(
        f'<TR><TD ALIGN="LEFT"><FONT FACE="{MONO}" POINT-SIZE="10">{html.escape(n) or " "}</FONT></TD>'
        f'<TD ALIGN="LEFT"><FONT POINT-SIZE="10.5">{html.escape(t)}</FONT></TD></TR>'
        for n, t in fields)
    nrow = (f'<TR><TD ALIGN="LEFT" COLSPAN="2"><FONT POINT-SIZE="9.5" COLOR="#555555"><I>{html.escape(note)}</I></FONT></TD></TR>'
            if note else "")
    return (f'  {nid} [shape=plaintext, label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2" '
            f'{style} BGCOLOR="{color}" COLOR="#555555">'
            f'<TR><TD ALIGN="LEFT" COLSPAN="2" BGCOLOR="{color}"><B>{html.escape(title)}</B></TD></TR>'
            f'<HR/>{rows}{nrow}</TABLE>>];\n')


def render(name, src):
    p = os.path.join(OUT, name + ".dot")
    with open(p, "w") as f:
        f.write(src)
    subprocess.run(["dot", "-Tpng", "-Gdpi=170", p, "-o", os.path.join(OUT, name + ".png")], check=True)


DM_LEGEND = ["Rounded box = entity in the schema of the component named in its title. Dashed box = transient object, never stored.",
             "Solid line = foreign key inside one component's schema. Dotted line = logical reference by ID to another component's data",
             "(no cross-schema FK; kept current by events or the I17a/I17b lookups). Cardinality at both ends: 1, 0..1, 0..*, 1..*.",
             "[PK] primary key, [FK] foreign key, [UQ] unique, [UQ*] partial unique index, trailing ? = nullable. Datetimes UTC; money integer cents."]

# ---------------------------------------------------------------- Figure 1: component map
def fig1():
    s = graph_open("D2_Fig1_Component_Map", "D2 Figure 1: component map with glue components and revised interfaces",
                   ["Blue rounded box = component we build (Cn). Gray rounded box = glue module (Gn) used by every backend component.",
                    "Gray dashed box = external system (En). Ellipse = actor. Dotted outline = one deployable backend (D-01).",
                    "Arrow Ix = interface from caller to callee (reply returns on it). Red label = interface revised in D2 (Part 2.10).",
                    "Arrows from the G-band mean every backend component calls that glue module."], rankdir="TB")
    s += '  node [shape=box, style="rounded,filled", fillcolor="#DCE6F5", color="#3B5B92"];\n'
    s += '  users [shape=ellipse, style=filled, fillcolor="#FFF3B0", color="#8A7A20", label="Students, managers,\\nreviewer"];\n'
    s += '  C1 [label="C1 Web Client"];\n'
    s += '  subgraph cluster_be { label="Backend: one modular monolith"; style="dotted"; color="#555555"; fontsize=11;\n'
    for c, l in [("C2", "C2 Identity"), ("C3", "C3 Listing"), ("C4", "C4 Compliance\\nScreener"), ("C5", "C5 Search & Match"),
                 ("C6", "C6 Messaging"), ("C7", "C7 Approval"), ("C8", "C8 Notification")]:
        s += f'    {c} [label="{l}"];\n'
    s += '    subgraph cluster_g { label="Glue (used by every backend component)"; style="rounded,filled"; fillcolor="#F4F4F4"; color="#999999";\n'
    s += '      node [fillcolor="#E6E6E6", color="#666666"];\n'
    s += '      G1 [label="G1 Auth middleware\\nverifyToken()"]; G2 [label="G2 Configuration\\ngetConfig()"]; G3 [label="G3 Logging & audit\\nlog(), audit.record()"];\n'
    s += '    }\n  }\n'
    s += '  node [style="dashed,rounded", fillcolor=white, color="#777777"];\n'
    s += '  E1 [label="E1 Email\\nDelivery API"]; E2 [label="E2 Recipient\\nMailboxes"]; E3 [label="E3 Managed\\nPostgreSQL"];\n'
    e = [("users", "C1", "I1 UI", False), ("C1", "C2", "I2 auth", False), ("C1", "C3", "I3a listings\\nI3b review", True),
         ("C1", "C5", "I4 search", False), ("C1", "C6", "I5 messages", True), ("C1", "C7", "I6 approvals", False),
         ("C3", "C4", "I7 screen()", False), ("C3", "C5", "I8 outbox row", True), ("C3", "C6", "I16 outbox row", True),
         ("C3", "C7", "I9 outbox row", True), ("C2", "C8", "I10 enqueue()", True), ("C6", "C8", "I11 enqueue()", True),
         ("C7", "C8", "I12 enqueue()", True), ("C8", "C2", "I17a getContacts()", True), ("C7", "C2", "I17b getEligibility()", True),
         ("C8", "E1", "I13 send", False), ("E1", "E2", "I14 SMTP", False)]
    for a, b, l, rev in e:
        col = RED if rev else "#333333"
        s += f'  {a} -> {b} [label="{l}", fontcolor="{col}"];\n'
    s += f'  E1 -> C8 [label="I13 status webhook", fontcolor="{RED}", style=dashed];\n'
    s += f'  G3 -> E3 [label="I15 SQL/TLS (all)", ltail=cluster_g];\n'
    s += f'  G1 -> C3 [label="I18 verifyToken()", fontcolor="{RED}", style=dotted, constraint=false];\n'
    s += '}\n'
    render("D2_Fig1_Component_Map", s.replace("digraph D2_Fig1_Component_Map {", "digraph D2_Fig1_Component_Map {\n  compound=true;"))


# ---------------------------------------------------------------- Figure 2: data model C2/C8/G3
def fig2():
    s = graph_open("D2_Fig2_Data_Model_Identity_Notify", "D2 Figure 2: data model for C2 Identity, C8 Notification, and G3 audit",
                   DM_LEGEND, rankdir="LR")
    s += entity("acct", "Account (C2-owned)", [("user_id", "UUID [PK]"), ("email", "string [UQ], lowercased"),
                ("role", "enum {STUDENT, MANAGER, REVIEWER}"), ("status", "enum {UNVERIFIED, PENDING, VERIFIED}"),
                ("verified_at", "datetime?"), ("first_name", "string?"), ("seeded", "bool"), ("created_at", "datetime")], COL["C2"])
    s += entity("link", "LoginLink (C2-owned)", [("link_id", "UUID [PK]"), ("user_id", "UUID [FK]"), ("token_hash", "bytea [UQ], SHA-256"),
                ("issued_at", "datetime"), ("expires_at", "datetime (issued+24h)"), ("used_at", "datetime?"), ("superseded_at", "datetime?")], COL["C2"])
    s += entity("claims", "SessionClaims (C2 -> G1, transient)", [("sub", "UUID (user_id)"), ("role", "enum"), ("verified", "bool"),
                ("verifiedAt", "datetime?"), ("iat, exp", "int (exp = iat+24h)"), ("kid", "string (JWT header)")], COL["T"], dashed=True,
                note="Signed HS256 JWT; never stored server-side.")
    s += entity("notif", "Notification (C8-owned)", [("notification_id", "UUID [PK]"), ("idempotency_key", "string [UQ]"),
                ("template_id", "enum {LOGIN_LINK, NEW_MESSAGE,"), ("", "  NEW_LISTING, SUBLEASE_PROPOSED,"), ("", "  DECISION, REMINDER}"),
                ("priority", "smallint (1 = LOGIN_LINK)"), ("to_user_id", "UUID"), ("to_email", "string"), ("params", "JSONB (typed per template)"),
                ("status", "enum {QUEUED, SENDING, SENT,"), ("", "  DELIVERED, BOUNCED, FAILED, SUPPRESSED}"), ("attempts", "int (0..4)"),
                ("next_attempt_at", "datetime"), ("provider_msg_id", "string? [UQ]"), ("last_error", "string?"), ("created_at", "datetime"),
                ("updated_at", "datetime")], COL["C8"])
    s += entity("supp", "Suppression (C8-owned)", [("email", "string [PK]"), ("reason", "enum {BOUNCED, COMPLAINT}"), ("created_at", "datetime")], COL["C8"])
    s += entity("hook", "WebhookReceipt (C8-owned)", [("provider_event_id", "string [PK]"), ("notification_id", "UUID [FK]"),
                ("event", "enum {DELIVERED, DEFERRED, BOUNCED}"), ("received_at", "datetime")], COL["C8"])
    s += entity("req", "NotificationRequest (I10/I11/I12, transient)", [("templateId", "enum"), ("toUserId", "UUID"),
                ("params", "typed per templateId"), ("idempotencyKey", "string")], COL["T"], dashed=True)
    s += entity("audit", "AuditLog (G3-owned, append-only)", [("audit_id", "bigint [PK]"), ("at", "datetime"), ("actor_user_id", "UUID"),
                ("action", "enum {ACCOUNT_VERIFIED, LISTING_RELEASED,"), ("", "  LISTING_REJECTED, APPROVAL_DECIDED,"), ("", "  NOTIFICATION_REDRIVEN}"),
                ("entity_type", "string"), ("entity_id", "UUID"), ("request_id", "string"), ("detail", "JSONB (no PII)")], COL["G"])
    s += '  acct -> link [arrowhead=none, taillabel="1", headlabel="0..*", fontcolor="#B3261E"];\n'
    s += '  notif -> hook [arrowhead=none, taillabel="1", headlabel="0..*", fontcolor="#B3261E"];\n'
    s += '  notif -> acct [style=dotted, arrowhead=vee, label="to_user_id\\n(resolved via I17a)", taillabel="0..*", headlabel="1", fontcolor="#B3261E", constraint=false];\n'
    s += '  notif -> supp [style=dotted, arrowhead=vee, label="to_email checked\\nat enqueue", taillabel="0..*", headlabel="0..1", fontcolor="#B3261E"];\n'
    s += '  audit -> acct [style=dotted, arrowhead=vee, label="actor_user_id", taillabel="0..*", headlabel="1", fontcolor="#B3261E"];\n'
    s += '  acct -> claims [style=dashed, arrowhead=vee, label="issued on confirm", taillabel="1", headlabel="0..*", fontcolor="#B3261E"];\n'
    s += '  req -> notif [style=dashed, arrowhead=vee, label="enqueue() inserts\\n(ON CONFLICT key: existing row)", taillabel="1", headlabel="1", fontcolor="#B3261E"];\n'
    s += '  {rank=same; acct; audit}\n  {rank=same; req; notif}\n}\n'
    render("D2_Fig2_Data_Model_Identity_Notify", s)


# ---------------------------------------------------------------- Figure 3: data model C6/C7
def fig3():
    s = graph_open("D2_Fig3_Data_Model_Messaging_Approval", "D2 Figure 3: data model for C6 Messaging and C7 Approval", DM_LEGEND, rankdir="TB")
    s += entity("lc6", "ListingCopy (C6-owned, from I16)", [("listing_id", "UUID [PK]"), ("owner_user_id", "UUID"),
                ("address_summary", "string"), ("source_version", "int"), ("updated_at", "datetime")], COL["C6"])
    s += entity("thr", "Thread (C6-owned)", [("thread_id", "UUID [PK]"), ("listing_id", "UUID [FK]"), ("owner_user_id", "UUID"),
                ("sublessee_user_id", "UUID"), ("created_at", "datetime"), ("last_message_at", "datetime"),
                ("owner_alerted_at", "datetime?"), ("sublessee_alerted_at", "datetime?"), ("[UQ]", "(listing_id, sublessee_user_id)")], COL["C6"])
    s += entity("msg", "Message (C6-owned)", [("message_id", "UUID [PK]"), ("thread_id", "UUID [FK]"), ("sender_user_id", "UUID"),
                ("client_message_id", "UUID"), ("body", "string (1..2000)"), ("sent_at", "datetime"),
                ("[UQ]", "(sender_user_id, client_message_id)")], COL["C6"])
    s += entity("unit", "UnitRegistry (C7-owned, team-seeded)", [("address_norm", "string [PK]"), ("manager_user_id", "UUID"),
                ("unit_label", "string"), ("seeded_at", "datetime")], COL["C7"])
    s += entity("lc7", "ListingCopy (C7-owned, from I9)", [("listing_id", "UUID [PK]"), ("owner_user_id", "UUID"),
                ("address_norm", "string [FK]?"), ("available_start", "date"), ("available_end", "date"),
                ("unit_status", "enum {REGISTERED, UNREGISTERED_UNIT}"), ("source_version", "int")], COL["C7"])
    s += entity("apr", "ApprovalRequest (C7-owned)", [("request_id", "UUID [PK]"), ("listing_id", "UUID [FK]"), ("owner_user_id", "UUID"),
                ("sublessee_user_id", "UUID"), ("manager_user_id", "UUID"), ("status", "enum {PENDING, APPROVED, REJECTED}"),
                ("reason", "string? (1..500)"), ("created_at", "datetime"), ("decided_at", "datetime?"), ("reminder_sent_at", "datetime?"),
                ("[UQ*]", "(listing_id) WHERE status IN"), ("", "  (PENDING, APPROVED)")], COL["C7"])
    s += entity("acct", "Account (C2-owned, see Fig. 2)", [("user_id", "UUID [PK]"), ("role, verified", "read via token / I17b")], COL["C2"])
    s += entity("lst", "Listing (C3-owned, see D1 Fig. 1)", [("listing_id", "UUID [PK]"), ("version", "int")], COL["C3"])
    s += '  lc6 -> thr [arrowhead=none, taillabel="1", headlabel="0..*", fontcolor="#B3261E"];\n'
    s += '  thr -> msg [arrowhead=none, taillabel="1", headlabel="1..*", fontcolor="#B3261E"];\n'
    s += '  unit -> lc7 [arrowhead=none, taillabel="0..1", headlabel="0..*", fontcolor="#B3261E"];\n'
    s += '  lc7 -> apr [arrowhead=none, taillabel="1", headlabel="0..*", fontcolor="#B3261E"];\n'
    s += '  lst -> lc6 [style=dotted, arrowhead=vee, label="copied by I16\\n(upsert if version newer)", taillabel="1", headlabel="0..1", fontcolor="#B3261E"];\n'
    s += '  lst -> lc7 [style=dotted, arrowhead=vee, label="copied by I9", taillabel="1", headlabel="0..1", fontcolor="#B3261E"];\n'
    s += '  apr -> acct [style=dotted, arrowhead=vee, label="owner, sublessee,\\nmanager ids (I17b)", taillabel="0..*", headlabel="1", fontcolor="#B3261E"];\n'
    s += '  thr -> acct [style=dotted, arrowhead=vee, label="participant ids", taillabel="0..*", headlabel="1", fontcolor="#B3261E"];\n'
    s += '  {rank=same; lc6; lc7}\n  {rank=same; thr; apr}\n}\n'
    render("D2_Fig3_Data_Model_Messaging_Approval", s)


SM_LEGEND = ["Rounded box = state stored in the named column. Filled dot = initial state; ringed dot = final state.",
             "Arrow = transition, labelled  event [guard] / action. Red arrow or note = error outcome: the request is refused",
             "with the named code and the state does not change. Every transition commits in one SQL transaction with its outbox or audit row."]


def sm_open(name, fig):
    s = graph_open(name, fig, SM_LEGEND, rankdir="TB")
    s += '  node [shape=box, style="rounded,filled", fillcolor="#DCE6F5", color="#3B5B92", fontsize=12];\n'
    s += '  init [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    return s


# ---------------------------------------------------------------- Figure 4: Account + Listing state machines
def fig4():
    s = sm_open("D2_Fig4_State_Account_Listing", "D2 Figure 4: state machines for Account (C2) and Listing (C3)")
    s += '  subgraph cluster_a { label="Account.status (C2)"; style=rounded; color="#999999"; fontsize=12;\n'
    s += '    a0 [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    s += '    UNV [label="UNVERIFIED\\n(seeded manager or\\nreviewer only)"]; PEN [label="PENDING"]; VER [label="VERIFIED\\nverified_at set"];\n'
    s += '    a0 -> UNV [label="team seeds account"];\n'
    s += '    a0 -> PEN [label="first link request\\n[@mail.uc.edu] / create row,\\nLoginLink, enqueue LOGIN_LINK"];\n'
    s += '    UNV -> PEN [label="link request\\n/ LoginLink, enqueue"];\n'
    s += '    PEN -> PEN [label="link request [< 3 in 60 min]\\n/ supersede old links"];\n'
    s += '    PEN -> VER [label="confirm [token unused,\\nnow < expires_at]\\n/ used_at, issue JWT, audit"];\n'
    s += '    VER -> VER [label="confirm re-verification link\\n/ verified_at = now"];\n'
    s += f'    e1 [shape=note, style=filled, fillcolor="#FDECEA", color="{RED}", fontcolor="{RED}", label="Refused, no change:\\n410 EXPIRED (expired or superseded)\\n400 INVALID_TOKEN (unknown, used)\\n429 RATE_LIMITED (4th request/hour)\\n422 NOT_ELIGIBLE / EMAIL_UNDELIVERABLE"];\n'
    s += f'    PEN -> e1 [color="{RED}", style=dashed, arrowhead=none];\n'
    s += f'    stale [shape=note, style=filled, fillcolor="#FDECEA", color="{RED}", fontcolor="{RED}", label="Derived, not stored: STUDENT with\\nverified_at + 12 months <= now\\n-> G1 returns 403 VERIFICATION_REQUIRED"];\n'
    s += f'    VER -> stale [color="{RED}", style=dashed, arrowhead=none];\n'
    s += '  }\n'
    s += '  subgraph cluster_l { label="Listing.status (C3, refines D1 Algorithm B)"; style=rounded; color="#999999"; fontsize=12;\n'
    s += '    l0 [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    s += '    PUB [label="PUBLISHED", fillcolor="#E6F2E6", color="#2E7D32"]; HELD [label="HELD_FOR_REVIEW", fillcolor="#FFF6DC", color="#8A6D00"]; REJ [label="REJECTED", fillcolor="#EEEEEE", color="#666666"];\n'
    s += '    lend [shape=doublecircle, label="", width=0.15, style=filled, fillcolor=black];\n'
    s += '    l0 -> PUB [label="submit [valid, C4 clean]\\n/ version=1, 3 outbox rows\\n(C5, C6, C7)"];\n'
    s += '    l0 -> HELD [label="submit [valid, C4 flagged\\nor C4 unavailable]\\n/ flagged_phrases, no outbox"];\n'
    s += '    HELD -> PUB [label="review RELEASE [REVIEWER]\\n/ version+1, 3 outbox rows, audit"];\n'
    s += '    HELD -> REJ [label="review REJECT [REVIEWER]\\n/ review_note, audit"];\n'
    s += '    REJ -> lend;\n'
    s += f'    e2 [shape=note, style=filled, fillcolor="#FDECEA", color="{RED}", fontcolor="{RED}", label="Refused, no row or change:\\n400 INVALID_INPUT, 409 DUPLICATE_LISTING\\n409 NOT_HELD_FOR_REVIEW (review of\\nPUBLISHED or REJECTED), 503 on DB loss"];\n'
    s += f'    PUB -> e2 [color="{RED}", style=dashed, arrowhead=none];\n'
    s += f'    gap [shape=note, style=filled, fillcolor="#FFFFFF", color="#777777", label="No exit from PUBLISHED in D2:\\nno user story asks for withdraw\\nor filled (open question GQ-03)."];\n'
    s += '    PUB -> gap [style=dotted, arrowhead=none];\n'
    s += '  }\n'
    s = s.replace('  init [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n', '')
    s += '}\n'
    render("D2_Fig4_State_Account_Listing", s)


# ---------------------------------------------------------------- Figure 5: ApprovalRequest
def fig5():
    s = sm_open("D2_Fig5_State_Approval", "D2 Figure 5: state machine for ApprovalRequest (C7, US-03, UC-02)")
    s += '  PENDING [label="PENDING\\nreminder_sent_at = null"]; PENDR [label="PENDING\\nreminder_sent_at set"];\n'
    s += '  APP [label="APPROVED\\ndecided_at set", fillcolor="#E6F2E6", color="#2E7D32"]; REJ [label="REJECTED\\ndecided_at, reason", fillcolor="#EEEEEE", color="#666666"];\n'
    s += '  fin [shape=doublecircle, label="", width=0.15, style=filled, fillcolor=black];\n'
    s += ('  init -> PENDING [label="proposal [caller owns listing,\\nsublessee verified (I17b), unit REGISTERED,\\n'
          'no PENDING/APPROVED for listing]\\n/ enqueue SUBLEASE_PROPOSED to manager"];\n')
    s += ('  PENDING -> PENDR [label="daily job [>= 5 business days,\\nstatus PENDING] / conditional UPDATE\\n'
          'reminder_sent_at, enqueue REMINDER (AC-02.2)"];\n')
    s += '  PENDING -> APP [label="APPROVE [caller = unit manager]\\n/ decided_at, enqueue DECISION x2, audit"];\n'
    s += '  PENDR -> APP [label="APPROVE"];\n'
    s += '  PENDING -> REJ [label="REJECT [reason 1..500]\\n/ same actions"];\n'
    s += '  PENDR -> REJ [label="REJECT"];\n'
    s += '  APP -> fin; REJ -> fin;\n'
    s += (f'  err [shape=note, style=filled, fillcolor="#FDECEA", color="{RED}", fontcolor="{RED}", label="Refused, no change:\\n'
          '409 ALREADY_DECIDED (decision on APPROVED/REJECTED)\\n409 PENDING_EXISTS / ALREADY_APPROVED (proposal)\\n'
          '422 SUBLESSEE_NOT_VERIFIED, SELF_PROPOSAL, UNIT_NOT_REGISTERED\\n'
          '403 NOT_LISTING_OWNER / NOT_UNIT_MANAGER\\n503 if enqueue or I17b fails (whole TX rolled back)"];\n')
    s += f'  APP -> err [color="{RED}", style=dashed, arrowhead=none]; REJ -> err [color="{RED}", style=dashed, arrowhead=none];\n'
    s += (f'  rem [shape=note, style=filled, fillcolor="#FFFFFF", color="#777777", label="No PENDR -> PENDR edge: the guard\\n'
          'reminder_sent_at IS NULL makes a 2nd\\nreminder impossible, even if the job\\nruns twice (advisory lock + guard)."];\n')
    s += '  PENDR -> rem [style=dotted, arrowhead=none];\n'
    s += '}\n'
    render("D2_Fig5_State_Approval", s)


# ---------------------------------------------------------------- Figure 6: Notification + outbox row
def fig6():
    s = sm_open("D2_Fig6_State_Notification_Outbox", "D2 Figure 6: state machines for Notification (C8) and ListingEvent outbox rows (C3)")
    s += '  subgraph cluster_n { label="Notification.status (C8)"; style=rounded; color="#999999"; fontsize=12;\n'
    s += '    n0 [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    s += '    Q [label="QUEUED"]; SD [label="SENDING\\nattempts+1"]; ST [label="SENT"]; DL [label="DELIVERED", fillcolor="#E6F2E6", color="#2E7D32"];\n'
    s += f'    BO [label="BOUNCED", fillcolor="#FDECEA", color="{RED}"]; FA [label="FAILED", fillcolor="#FDECEA", color="{RED}"]; SU [label="SUPPRESSED", fillcolor="#EEEEEE", color="#666666"];\n'
    s += '    n0 -> Q [label="enqueue() [recipient ok]"];\n'
    s += '    n0 -> SU [label="enqueue() [email suppressed\\nor user unknown]"];\n'
    s += '    Q -> SD [label="worker claims\\n(SKIP LOCKED, every 5 s)"];\n'
    s += '    SD -> ST [label="E1 2xx accepted\\n/ provider_msg_id"];\n'
    s += f'    SD -> Q [color="{RED}", fontcolor="{RED}", label="5xx, 429, timeout 5 s\\n[attempts < 4] / next_attempt\\n+30 s, +60 s, +120 s"];\n'
    s += f'    SD -> FA [color="{RED}", fontcolor="{RED}", label="4xx, or attempts = 4\\n/ ERROR log"];\n'
    s += f'    SD -> Q [color="{RED}", fontcolor="{RED}", style=dashed, label="reaper: SENDING > 2 min\\n(crash after send)"];\n'
    s += '    ST -> DL [label="webhook DELIVERED"];\n'
    s += f'    ST -> BO [color="{RED}", fontcolor="{RED}", label="webhook BOUNCED\\n/ add Suppression"];\n'
    s += f'    DL -> BO [color="{RED}", fontcolor="{RED}", label="late bounce"];\n'
    s += '    FA -> Q [style=dashed, label="manual re-drive\\n/ audit"];\n'
    s += '  }\n'
    s += '  subgraph cluster_o { label="ListingEvent outbox row (C3, one row per consumer C5, C6, C7)"; style=rounded; color="#999999"; fontsize=12;\n'
    s += '    o0 [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    s += '    OP [label="PENDING\\ndispatched_at = null"]; OD [label="DISPATCHED\\ndispatched_at set", fillcolor="#E6F2E6", color="#2E7D32"];\n'
    s += f'    OF [label="FAILED", fillcolor="#FDECEA", color="{RED}"];\n'
    s += '    o0 -> OP [label="written in the same TX\\nas the listing change"];\n'
    s += '    OP -> OD [label="relay (every 5 s) calls\\nconsumer handler, ack"];\n'
    s += f'    OP -> OP [color="{RED}", fontcolor="{RED}", label="handler throws [attempts < 4]\\n/ next_attempt +5 s, +30 s, +2 min"];\n'
    s += f'    OP -> OF [color="{RED}", fontcolor="{RED}", label="4th failure / ERROR log"];\n'
    s += '    OF -> OP [style=dashed, label="redrive script / audit"];\n'
    s += '  }\n'
    s = s.replace('  init [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n', '')
    s += '}\n'
    render("D2_Fig6_State_Notification_Outbox", s)


# ---------------------------------------------------------------- activity diagrams with error paths
ACT_LEGEND = ["Rounded box = processing step (owning component in brackets). Diamond = decision. Black arrows = happy path.",
              "Red arrows and red boxes = error paths, each ending in the stated outcome; R = recoverable (user or system can retry), N = not recoverable",
              "without a person. Dashed arrow = asynchronous hand-off through an outbox or queue row. Codes are HTTP status + error code."]


def act_open(name, fig):
    s = graph_open(name, fig, ACT_LEGEND, rankdir="TB", extra=", nodesep=0.35, ranksep=0.35")
    s += '  node [shape=box, style="rounded,filled", fillcolor="#DCE6F5", color="#3B5B92", fontsize=11];\n'
    return s


def dec(n, l):
    return f'  {n} [shape=diamond, style=filled, fillcolor="#FFF6DC", color="#8A6D00", label="{l}", fontsize=10];\n'


def err(n, l):
    return f'  {n} [shape=box, style="rounded,filled", fillcolor="#FDECEA", color="{RED}", fontcolor="{RED}", label="{l}", fontsize=10];\n'


def ok(n, l):
    return f'  {n} [shape=box, style="rounded,filled", fillcolor="#E6F2E6", color="#2E7D32", label="{l}", fontsize=10];\n'


def eE(a, b, l=""):
    return f'  {a} -> {b} [color="{RED}", fontcolor="{RED}", label="{l}"];\n'


def fig7():
    s = act_open("D2_Fig7_Error_Paths_Publish", "D2 Figure 7: error paths in the riskiest flow, publish a listing and fan out its events (US-01, US-05, AC-01.1, AC-01.3, AC-01.4)")
    s += '  start [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    s += '  a1 [label="POST /api/v1/listings\\n[C1 -> C3, I3a]"];\n'
    s += dec("d1", "token valid?\\n[G1]") + err("x1", "401 UNAUTHENTICATED\\nC1 restarts sign-in, R")
    s += dec("d2", "verified and\\nfresh (12 mo)?") + err("x2", "403 VERIFICATION_REQUIRED\\nC1 starts I2, draft kept, R")
    s += dec("d3", "input valid?\\n[zod, C3]") + err("x3", "400 INVALID_INPUT\\nno row (AC-01.4), R")
    s += '  a2 [label="normalize address\\n[C3]"];\n  a3 [label="screen(text)\\n[C4, I7, 2 s budget]"];\n'
    s += dec("d4", "C4 result?") + f'  h1 [shape=box, style="rounded,filled", fillcolor="#FFF6DC", color="#8A6D00", label="HELD_FOR_REVIEW\\nno outbox rows\\n(flagged or SCREENER_UNAVAILABLE)", fontsize=10];\n'
    s += '  a4 [label="BEGIN TX: insert Listing PUBLISHED\\n+ 3 ListingEvent rows (C5, C6, C7)"];\n'
    s += dec("d5", "commit ok?") + err("x4", "409 DUPLICATE_LISTING\\n(partial unique index), R") + err("x5", "503 DB_UNAVAILABLE\\nTX rolled back, Retry-After 5, R")
    s += ok("r1", "201 {listingId, status,\\nflaggedPhrases}")
    s += '  a5 [label="outbox relay, every 5 s\\nSKIP LOCKED, per row [C3]"];\n'
    s += dec("d6", "consumer\\nhandler ok?") + '  a6 [label="retry +5 s, +30 s, +2 min\\nper row, others unaffected"];\n'
    s += err("x6", "FAILED after 4th attempt\\nERROR log + redrive script\\nAC-01.1 at risk, N")
    s += ok("r2", "C5 index row\\n(upsert if version newer)")
    s += ok("r2b", "C6 owner copy row\\n(upsert if version newer)")
    s += '  a7 [label="C7: upsert ListingCopy,\\nlookup UnitRegistry"];\n'
    s += dec("d7", "unit\\nregistered?") + f'  h2 [shape=box, style="rounded,filled", fillcolor="#EEEEEE", color="#666666", label="UNREGISTERED_UNIT, ack,\\nno notice; listing stays\\npublished (degrade), R", fontsize=10];\n'
    s += '  a8 [label="enqueue NEW_LISTING\\n[C8, I12]"];\n  a9 [label="C8 worker sends\\n[I13, 5 s timeout]"];\n'
    s += dec("d8", "E1 result?") + '  a10 [label="retry +30 s, +60 s, +120 s"];\n'
    s += err("x7", "FAILED (4xx or 4th attempt)\\nERROR log, R by redrive") + err("x8", "BOUNCED webhook\\nSuppression row, N")
    s += ok("r3", "manager email\\n<= 5 min (AC-01.1)")
    s += '  start -> a1 -> d1;\n' + eE("d1", "x1", "no") + '  d1 -> d2 [label="yes"];\n' + eE("d2", "x2", "no")
    s += '  d2 -> d3 [label="yes"];\n' + eE("d3", "x3", "no") + '  d3 -> a2 [label="yes"]; a2 -> a3 -> d4;\n'
    s += eE("d4", "h1", "flagged, throws,\\nor > 2 s") + '  d4 -> a4 [label="clean"]; a4 -> d5;\n'
    s += eE("d5", "x4", "unique\\nviolation") + eE("d5", "x5", "connection\\nlost") + '  d5 -> r1 [label="yes"];\n'
    s += '  r1 -> a5 [style=dashed, label="async", constraint=false]; a5 -> d6;\n' + eE("d6", "a6", "throws") + '  a6 -> a5 [style=dashed];\n'
    s += eE("a6", "x6", "4th failure") + '  d6 -> r2 [label="C5"]; d6 -> r2b [label="C6"]; d6 -> a7 [label="C7"];\n'
    s += '  a7 -> d7;\n' + eE("d7", "h2", "no") + '  d7 -> a8 [label="yes"]; a8 -> a9 [style=dashed]; a9 -> d8;\n'
    s += eE("d8", "a10", "5xx / 429 /\\ntimeout") + '  a10 -> a9 [style=dashed];\n' + eE("a10", "x7", "4th failure")
    s += eE("d8", "x7", "4xx") + '  d8 -> r3 [label="2xx"];\n' + eE("r3", "x8", "later bounce")
    s += '  {rank=same; d1; x1}\n  {rank=same; d2; x2}\n  {rank=same; d3; x3}\n  {rank=same; d4; h1}\n'
    s += '}\n'
    render("D2_Fig7_Error_Paths_Publish", s)


def fig8():
    s = act_open("D2_Fig8_Error_Paths_SignIn", "D2 Figure 8: error paths in sign-in and verification (US-01, UC-01 steps 2 to 6, AC-01.2)")
    s += '  start [shape=circle, label="", width=0.2, style=filled, fillcolor=black];\n'
    s += '  a1 [label="POST /api/v1/auth/link-requests {email}\\n[C1 -> C2, I2]"];\n  a2 [label="trim, lowercase, NFKC\\n[C2]"];\n'
    s += dec("d1", "@mail.uc.edu exact,\\nor seeded account?") + err("x1", "422 NOT_ELIGIBLE, R")
    s += dec("d2", "< 3 links in\\nlast 60 min?") + err("x2", "429 RATE_LIMITED\\nRetry-After, R")
    s += '  a3 [label="BEGIN TX: upsert Account,\\nsupersede unused links, insert LoginLink\\n(store SHA-256 of 32-byte token)"];\n'
    s += '  a4 [label="enqueue LOGIN_LINK\\n[C8, I10, same TX]"];\n'
    s += dec("d3", "enqueue\\nstate?") + err("x3", "422 EMAIL_UNDELIVERABLE\\nTX rolled back, N") + err("x4", "503 NOTIFY_UNAVAILABLE\\nTX rolled back, not PENDING, R")
    s += ok("r1", "202 {status: PENDING}")
    s += '  a5 [label="student opens emailed link\\nGET /verify#token (C1 page only;\\nGET never consumes the token)"];\n'
    s += '  a6 [label="student presses Confirm\\nPOST /api/v1/auth/link-confirmations"];\n'
    s += dec("d4", "token hash\\nfound?") + err("x5", "400 INVALID_TOKEN, R (new link)")
    s += dec("d5", "now < expires_at,\\nnot superseded?") + err("x6", "410 EXPIRED, stays PENDING\\nC1 offers new link (AC-01.2), R")
    s += dec("d6", "UPDATE used_at\\nWHERE used_at IS NULL\\n1 row?") + err("x7", "400 INVALID_TOKEN (double click)\\nC1 continues if it holds a session, R")
    s += ok("r2", "VERIFIED, verified_at = now,\\naudit; 200 {sessionToken,\\nexpiresAt = +24 h}")
    s += '  start -> a1 -> a2 -> d1;\n' + eE("d1", "x1", "no") + '  d1 -> d2 [label="yes"];\n' + eE("d2", "x2", "no")
    s += '  d2 -> a3 [label="yes"]; a3 -> a4 -> d3;\n' + eE("d3", "x3", "SUPPRESSED") + eE("d3", "x4", "throws")
    s += '  d3 -> r1 [label="QUEUED"];\n  r1 -> a5 [style=dashed, label="email via C8, E1, E2", constraint=false]; a5 -> a6 -> d4;\n'
    s += eE("d4", "x5", "no") + '  d4 -> d5 [label="yes"];\n' + eE("d5", "x6", "no") + '  d5 -> d6 [label="yes"];\n'
    s += eE("d6", "x7", "0 rows") + '  d6 -> r2 [label="1 row"];\n'
    s += '  {rank=same; d1; x1}\n  {rank=same; d2; x2}\n  {rank=same; d4; x5}\n  {rank=same; d5; x6}\n  {rank=same; d6; x7}\n'
    s += '}\n'
    render("D2_Fig8_Error_Paths_SignIn", s)


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        f()
    print("ok", sorted(os.listdir(OUT)))
