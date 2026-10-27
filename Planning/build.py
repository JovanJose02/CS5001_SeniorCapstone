"""Build the Assignment 8 PDF, Tasklist.md, CSVs, and Gantt figure from plan.py.
Run: python3 build.py   (needs matplotlib and wkhtmltopdf)
"""
import csv, html, os, subprocess
from datetime import date, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from plan import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
E = html.escape
TID = {t["id"]: t for t in TASKS}
MID = {m["id"]: m for m in MILESTONES}


def fd(d):
    return d.strftime("%a %b %-d, %Y") if isinstance(d, date) else d


def sd(d):
    return d.strftime("%b %-d, %Y") if isinstance(d, date) else d


def blocked(d):
    return d.weekday() >= 5 or any(a <= d <= b for _, a, b in BLOCKED)


def workdays(a, b):  # inclusive, a<=b
    n, d = 0, a
    while d <= b:
        n += 0 if blocked(d) else 1
        d += timedelta(1)
    return n


# milestone each task feeds (its gate)
GATE = {"T1": "M2", "T2": "M2", "T3": "M2", "T4": "M4", "T5": "M4", "T6": "M4",
        "T7": "M6", "T8": "M6", "T9": "M6", "T11": "M6", "T12": "M6", "T13": "M6",
        "T10": "M7", "T14": "M7", "T15": "M7", "T16": "M8", "T17": "M8", "T18": "M10"}


def gate_start(mid):
    m = MID[mid]
    return m["block"][0] if m.get("block") else m["date"]


def float_days(t):
    limits = [gate_start(GATE[t["id"]])]
    limits += [s["start"] for s in TASKS if t["id"] in s["deps"]]
    nxt = min(limits)
    return workdays(t["end"] + timedelta(1), nxt - timedelta(1)) if nxt > t["end"] + timedelta(1) else 0


for t in TASKS:
    t["E"] = pert(t)
    t["buf"] = round(t["E"] * TASK_BUFFER, 1)
    t["float"] = float_days(t)
    t["eff"] = effort_row(t)
assert all(TID[c]["float"] == 0 for c in CRITICAL), [(c, TID[c]["float"]) for c in CRITICAL]

# ---------------------------------------------------------------- Tasklist.md
md = ["# Tasklist.md", "",
      "Verified Student Sublease Marketplace. Team: Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja.", ""]
for t in TASKS:
    md += [f"{t['id']}. {t['text']} Module: {t['module']}. Owner: {TEAM[t['owner']]}.", ""]
open(os.path.join(OUT, "Tasklist.md"), "w").write("\n".join(md))

# ---------------------------------------------------------------- CSVs
with open(os.path.join(OUT, "Table1_Timeline.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Statement", "Owner", "Start", "Finish", "Dependencies", "PERT hours", "Buffer hours (20%)", "Float (work days)", "Critical", "Risks"])
    for t in sorted(TASKS, key=lambda x: (x["start"], int(x["id"][1:]))):
        w.writerow([t["id"], t["text"], TEAM[t["owner"]], t["start"], t["end"], " ".join(t["deps"]), t["E"], t["buf"], t["float"], t["id"] in CRITICAL, " ".join(t["risks"])])
    for m in MILESTONES:
        w.writerow([m["id"], m["name"], "", "", m["date"], "", "", "", "", "", ""])
with open(os.path.join(OUT, "Table2_Effort.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Primary"] + [TEAM[k] for k in ORDER] + ["Row total"])
    for t in TASKS:
        w.writerow([t["id"], TEAM[t["owner"]]] + [t["eff"][k] for k in ORDER] + [round(sum(t["eff"].values()), 1)])
with open(os.path.join(OUT, "Risk_Register.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Category", "Risk", "Likelihood", "Impact", "Strategy", "Mitigation", "Owner", "Trigger", "Where in Table 1"])
    for r in RISKS:
        w.writerow([r["id"], r["cat"], r["risk"], r["L"], r["I"], r["strat"], r["mit"], TEAM[r["owner"]], r["trigger"], r["where"]])
with open(os.path.join(OUT, "Estimates_PERT.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Owner", "Optimistic", "Most likely", "Pessimistic", "Expected (O+4M+P)/6"])
    for t in TASKS:
        w.writerow([t["id"], TEAM[t["owner"]], t["O"], t["M"], t["P"], t["E"]])

# ---------------------------------------------------------------- Gantt figure
COLORS = {"J": "#3B6EA8", "D": "#3E8E5A", "M": "#B5652B"}
rows = sorted(TASKS, key=lambda x: (x["phase"], x["start"], int(x["id"][1:])))
fig, ax = plt.subplots(figsize=(15, 7.6), dpi=170)
n = len(rows)
for i, t in enumerate(rows):
    y = n - i
    s = mdates.date2num(t["start"])
    e = mdates.date2num(t["end"] + timedelta(1))
    span = e - s
    main = span / (1 + TASK_BUFFER)
    crit = t["id"] in CRITICAL
    ax.barh(y, main, left=s, height=0.62, color=COLORS[t["owner"]], edgecolor="#B3261E" if crit else "none", linewidth=1.6 if crit else 0)
    ax.barh(y, span - main, left=s + main, height=0.62, color="white", hatch="////", edgecolor=COLORS[t["owner"]], linewidth=0.8)
    if crit:
        ax.barh(y, span, left=s, height=0.62, fill=False, edgecolor="#B3261E", linewidth=1.6)
    ax.text(e + 1.2, y, f"{t['id']}", va="center", fontsize=8.5)
for name, a, b in BLOCKED:
    if a == b:
        continue
    ax.axvspan(mdates.date2num(a), mdates.date2num(b + timedelta(1)), color="#BDBDBD", alpha=0.45, lw=0)
    ax.text(mdates.date2num(a) + (b - a).days / 2, n + 1.15, name, ha="center", fontsize=7.5, color="#555555")
for m in MILESTONES:
    if not isinstance(m["date"], date) or m["date"] < date(2026, 10, 26):
        continue
    if m.get("block"):
        a, b = m["block"]
        ax.axvspan(mdates.date2num(a), mdates.date2num(b + timedelta(1)), color="#F2B233", alpha=0.45, lw=0)
    x = mdates.date2num(m["date"]) + 0.5
    ax.plot(x, 0.2, marker="D", color="#222222", ms=6)
    ax.text(x, -0.45, m["id"], ha="center", fontsize=7.5)
ax.set_yticks([n - i for i in range(n)])
ax.set_yticklabels([f"{t['id']}  {SHORT[t['owner']]}  (Ph {t['phase']})" for t in rows], fontsize=8.5)
ax.set_ylim(-1, n + 1.6)
ax.set_xlim(mdates.date2num(date(2026, 10, 26)), mdates.date2num(date(2027, 4, 19)))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=0))
ax.grid(axis="x", which="minor", color="#EEEEEE", lw=0.6)
ax.grid(axis="x", which="major", color="#CCCCCC", lw=0.8)
ax.set_axisbelow(True)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
leg = [Patch(color=COLORS[k], label=f"{TEAM[k]}") for k in ORDER]
leg += [Patch(facecolor="white", hatch="////", edgecolor="#555555", label="20% task buffer (end of bar)"),
        Patch(facecolor="none", edgecolor="#B3261E", lw=1.6, label="Critical path"),
        Patch(color="#F2B233", alpha=0.45, label="Protected buffer block"),
        Patch(color="#BDBDBD", alpha=0.45, label="No planned work"),
        Line2D([], [], marker="D", color="#222222", lw=0, label="Milestone")]
ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=4, fontsize=8.5, frameon=False)
ax.set_title("Gantt view of Table 1 (Verified Student Sublease Marketplace)", fontsize=11, loc="left")
fig.tight_layout()
GANTT = os.path.join(OUT, "Gantt.png")
fig.savefig(GANTT)
plt.close(fig)

# ---------------------------------------------------------------- HTML
CSS = """
body { font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 9pt; color: #1d1d1d; }
h1 { font-size: 19pt; color: #1F4E79; margin: 0 0 2px 0; }
h2 { font-size: 13.5pt; color: #1F4E79; border-bottom: 2px solid #1F4E79; padding-bottom: 2px; margin: 4px 0 6px 0; }
h3 { font-size: 10.5pt; margin: 10px 0 4px 0; }
p { margin: 3px 0 6px 0; line-height: 1.35; }
table { border-collapse: collapse; width: 100%; margin: 4px 0 8px 0; page-break-inside: auto; }
tr { page-break-inside: avoid; }
thead { display: table-header-group; }
th { background: #1F4E79; color: white; text-align: left; padding: 3px 4px; font-size: 8.2pt; }
td { border: 1px solid #C8CED6; padding: 2.5px 4px; vertical-align: top; font-size: 8.2pt; }
tr:nth-child(even) td { background: #F5F8FC; }
.pb { page-break-before: always; }
.sub { font-size: 12pt; font-weight: bold; margin: 0 0 8px 0; }
.ms td { background: #FFF6DC !important; font-weight: bold; }
.buf td { background: #FDE9C4 !important; color: #6b4b00; }
.blk td { background: #ECECEC !important; color: #555; font-style: italic; }
.done td { background: #E7F3E9 !important; }
.crit { color: #B3261E; font-weight: bold; }
.own { font-weight: bold; background: #DCE8F7 !important; }
.tot td { font-weight: bold; background: #E3E8EF !important; }
.note { background: #FFF8E1; border: 1px solid #E0C46C; padding: 5px 7px; margin: 6px 0; }
.small { font-size: 7.8pt; color: #444; }
.r { text-align: right; }
.c { text-align: center; }
ul { margin: 2px 0 6px 16px; padding: 0; } li { margin: 1px 0; }
"""


def table(head, rows, widths=None, cls=None):
    h = "<table><thead><tr>" + "".join(
        f'<th style="width:{widths[i]}">{x}</th>' if widths else f"<th>{x}</th>" for i, x in enumerate(head)) + "</tr></thead><tbody>"
    for i, r in enumerate(rows):
        c = cls[i] if cls else ""
        h += f'<tr class="{c}">' + "".join(f"<td>{x}</td>" for x in r) + "</tr>"
    return h + "</tbody></table>"


P = []
A = P.append

# Title block
A("<h1>Assignment 8: Task List, Milestones, Timeline, and Effort Matrix</h1>")
A('<p class="sub">Verified Student Sublease Marketplace &nbsp;|&nbsp; CS5001 Senior Design I &nbsp;|&nbsp; Covers official Assignment #5 (Task Lists) and #6 (Milestones, Timeline, and Effort Matrix)</p>')
A(table(["Item", "Detail"], [
    ["Team members", "Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja"],
    ["Goal", "Let UC students fill or find term-length subleases safely. Only verified @mail.uc.edu students can use it. Listings match exact co-op dates. Discriminatory listings are held for review. Property managers approve or reject before move-in."],
    ["Built from", "Project-Description.md, User_Stories, D0 (C1 to C8, I1 to I15), D1 (C3, C5), D2 (C1 to C8, G1 to G3, open questions GQ-01 to GQ-08)."],
    ["Repository", "Tasklist.md in the repository root. Plan sources in Planning/ (plan.py, build.py, CSV tables, Gantt.png)."],
    ["Contents", "1. Task List &nbsp; 2. Milestones List &nbsp; 3. Table 1: Timeline (+ Gantt) &nbsp; 4. Table 2: Effort Matrix &nbsp; 5. Work Breakdown Structure &nbsp; 6. Risk Register &nbsp; 7. Consistency check"],
], ["14%", "86%"]))
A("<h3>How we made this plan</h3><ul>"
  "<li><b>Tasks</b> come from the modules in D0 to D2. Each task is one module (or one part of a module) and one owner.</li>"
  "<li><b>Owners</b> follow the D0/D2 component owners. Jovan: C3, C4, C5, G2. Danvanth: C2, C7, C8, G1, E1. Mohamed: C1, C6, G3.</li>"
  "<li><b>Estimates</b> use three numbers per task: optimistic (O), most likely (M), and pessimistic (P). Expected hours = (O + 4M + P) / 6.</li>"
  f"<li><b>Time per person</b>: about {AVAIL['fall']} hours a week in Fall 2026 and {AVAIL['spring']} hours a week in Spring 2027 (CS 5002).</li>"
  "<li><b>Buffer</b>: every task gets 20% more time. Each major milestone also has a protected buffer block. No new work starts in a block. It is only for fixing and joining parts.</li>"
  "<li><b>Calendar</b>: no work on Thanksgiving, in the last fall week, in fall exam week, in winter break, or in spring break. Spring dates assume classes start Jan 11, 2027 and spring break is Mar 15 to 19. We re-check them at M5.</li>"
  "</ul>")

# 1. Task list
A('<h2>1. Task List (Assignment #5)</h2>')
A(f"<p>{len(TASKS)} tasks. Six per member. Each task starts with a verb, names its Design Diagram module, and has one owner. Each fits in one or two weeks. The same list is in Tasklist.md.</p>")
A(table(["ID", "Task statement", "Design Diagram module", "Owner (primary)", "Weeks"],
        [[f"<b>{t['id']}</b>", E(t["text"]), E(t["module"]), TEAM[t["owner"]],
          f"{max(1, round(workdays(t['start'], t['end']) / 5))}"] for t in TASKS],
        ["5%", "56%", "19%", "15%", "5%"]))
counts = {k: sum(1 for t in TASKS if t["owner"] == k) for k in ORDER}
A("<p><b>Tasks per member:</b> " + ", ".join(f"{TEAM[k]} {counts[k]}" for k in ORDER) + ".</p>")

# 2. Milestones
A('<h2 class="pb">2. Milestones List (Assignment #6)</h2>')
A("<p>A milestone is a checked, dated result. Course deliverables are listed first. Completed ones are marked <b>Complete</b>. Internal milestones are every 1 to 3 weeks. The only longer gap is fall exams plus winter break, when no work is planned.</p>")
mrows, mcls = [], []
for m in MILESTONES:
    mrows.append([f"<b>{m['id']}</b>", E(m["name"]), m["kind"] + (" (major)" if m.get("major") else ""), E(m["shows"]), sd(m["date"]), E(m["verify"]), E(m["by"]),
                  f"<b>{m['status']}</b>"])
    mcls.append("done" if m["status"] == "Complete" else "")
A(table(["ID", "Milestone", "Type", "What it shows", "Date", "How it is checked", "Checked by", "Status"], mrows,
        ["4%", "15%", "7%", "22%", "8%", "24%", "12%", "8%"], mcls))

# 3. Table 1
A('<h2 class="pb">3. Table 1: Timeline (Assignment #6)</h2>')
A("<p>Rows are in date order. Gray rows are breaks with no work. Orange rows are protected buffer blocks. Yellow rows are milestones. "
  "<b>Hours</b> = expected (PERT) hours. <b>+20%</b> = task buffer already inside the start-to-finish dates. "
  "<b>Float</b> = spare work days before the next task or block needs it. "
  '<span class="crit">Red IDs (★)</span> are on the critical path: '
  + " → ".join(CRITICAL[:5]) + " → T16 → T18. They have zero float, so they only have their 20% buffer and the protected blocks. "
  + ", ".join(t["id"] for t in TASKS if t["float"] == 0 and t["id"] not in CRITICAL) + " also have zero float before their milestone block. <b>Risks</b> links each row to the Risk Register.</p>")
ev = []
for t in TASKS:
    ev.append((t["start"], 1, int(t["id"][1:]), "task", t))
for m in MILESTONES:
    if isinstance(m["date"], date):
        ev.append((m["date"], 3, 0, "ms", m))
        if m.get("block"):
            ev.append((m["block"][0], 2, 0, "buf", m))
for name, a, b in BLOCKED:
    ev.append((a, 0, 0, "blk", (name, a, b)))
ev.sort(key=lambda x: (x[0], x[1], x[2]))
trows, tcls = [], []
for _, _, _, kind, o in ev:
    if kind == "task":
        crit = o["id"] in CRITICAL
        idc = f'<span class="crit">{o["id"]} ★</span>' if crit else f"<b>{o['id']}</b>"
        trows.append([idc, E(o["text"]), SHORT[o["owner"]], sd(o["start"]), sd(o["end"]), ", ".join(o["deps"]) or "None",
                      f'{o["E"]}', f'+{o["buf"]}', str(o["float"]), ", ".join(o["risks"]) or "-"])
        tcls.append("")
    elif kind == "ms":
        trows.append([f"<b>{o['id']}</b>", "Milestone: " + E(o["name"]), "Team", "", sd(o["date"]), "", "", "", "", ""])
        tcls.append("ms")
    elif kind == "buf":
        a, b = o["block"]
        trows.append(["Buffer", f"Protected buffer block before {o['id']}. No new work. Fix, join parts, and test.", "Team", sd(a), sd(b), "", "", "", "",
                      "RK3" + (", RK8" if o["id"] in ("M6", "M7") else "")])
        tcls.append("buf")
    else:
        name, a, b = o
        trows.append(["Break", f"{name}: no planned work.", "", sd(a), sd(b), "", "", "", "", "RK3" if "exam" in name.lower() or "Thanks" in name else ("RK9" if "Spring" in name else "")])
        tcls.append("blk")
A(table(["ID", "Task statement / milestone", "Owner", "Start", "Finish", "Depends on", "Hours", "+20%", "Float", "Risks"], trows,
        ["6%", "45%", "6%", "8%", "8%", "8%", "4%", "4%", "4%", "7%"], tcls))
A("<p>Course milestones finished before this plan (M0a to M0e) are in Section 2.</p>")
A('<h3 class="pb">Gantt view (supporting figure)</h3>')
A(f'<img src="file://{GANTT}" style="width:100%">')

# 4. Table 2
A('<h2 class="pb">4. Table 2: Effort Matrix (Assignment #6)</h2>')
A("<p>Hours each member spends on each task. The owner's cell is shaded and marked ★. The owner's hours are the task's expected (PERT) hours. "
  "The other members' hours are code review, pairing, and helping join the parts. The owner always has the largest share.</p>")
erows, ecls = [], []
col = {k: 0.0 for k in ORDER}
for t in TASKS:
    rt = round(sum(t["eff"].values()), 1)
    cells = []
    for k in ORDER:
        v = t["eff"][k]
        col[k] += v
        cells.append(f'<span class="own">★ {v:.1f}</span>' if k == t["owner"] else f"{v:.1f}")
    assert t["eff"][t["owner"]] == max(t["eff"].values())
    erows.append([f"<b>{t['id']}</b>", E(t["module"]), SHORT[t["owner"]]] + cells + [f"<b>{rt:.1f}</b>", f"{100 * t['eff'][t['owner']] / rt:.0f}%"])
    ecls.append("")
grand = round(sum(col.values()), 1)
erows.append(["<b>Total</b>", "", ""] + [f"<b>{col[k]:.1f}</b>" for k in ORDER] + [f"<b>{grand:.1f}</b>", ""])
ecls.append("tot")
erows.append(["<b>Share</b>", "", ""] + [f"<b>{100 * col[k] / grand:.1f}%</b>" for k in ORDER] + ["100%", ""])
ecls.append("tot")
own_h = {k: round(sum(t["E"] for t in TASKS if t["owner"] == k), 1) for k in ORDER}
erows.append(["", "Of which: owned-task hours", ""] + [f"{own_h[k]:.1f}" for k in ORDER] + [f"{sum(own_h.values()):.1f}", ""])
ecls.append("")
fall = {k: round(sum(t["eff"][k] for t in TASKS if t["phase"] == 1), 1) for k in ORDER}
spr = {k: round(sum(t["eff"][k] for t in TASKS if t["phase"] > 1), 1) for k in ORDER}
erows.append(["", "Of which: Fall 2026 (Phase 1)", ""] + [f"{fall[k]:.1f}" for k in ORDER] + [f"{sum(fall.values()):.1f}", ""])
ecls.append("")
erows.append(["", "Of which: Spring 2027 (Phases 2 to 4)", ""] + [f"{spr[k]:.1f}" for k in ORDER] + [f"{sum(spr.values()):.1f}", ""])
ecls.append("")
html_t2 = table(["ID", "Module", "Primary", TEAM["J"], TEAM["D"], TEAM["M"], "Row total", "Owner share"], erows,
                ["5%", "27%", "9%", "13%", "13%", "13%", "10%", "10%"], ecls)
A(html_t2.replace('<td><span class="own">', '<td class="own"><span>'))
hi = max(col, key=col.get)
lo = min(col, key=col.get)
gap = 100 * (col[hi] - col[lo]) / col[lo]
crit_owner = {k: sum(1 for c in CRITICAL if TID[c]["owner"] == k) for k in ORDER}
A("<h3>Balance check and rebalancing plan</h3>")
A(f"<p><b>Hours are even.</b> The largest column ({TEAM[hi]}, {col[hi]:.1f} h) is only {gap:.1f}% above the smallest ({TEAM[lo]}, {col[lo]:.1f} h). "
  f"Our limit is 10%.</p>")
A(f"<p><b>Two things are not even, and here is what we will do:</b></p><ul>"
  f"<li><b>Critical path load.</b> {TEAM['D']} owns {crit_owner['D']} of the {len(CRITICAL)} critical-path tasks (T6, T7, T11, T14, T16). A slip there moves the whole plan. "
  f"So {TEAM['J']} is the backup for C8 and C7. He has 3 review hours on T16 and is free from Mar 1 to Mar 10 to take part of T16 if T14 is late.</li>"
  f"<li><b>Fall vs spring.</b> Fall work is small for everyone ({', '.join(f'{SHORT[k]} {fall[k]:.1f} h' for k in ORDER)}). Most work is in spring. "
  "If a member goes on co-op in spring (RK2), we will move their spring tasks to the others at M5 and give that member review work and Phase 1 follow-ups.</li>"
  "<li><b>Weekly check.</b> At each weekly meeting we log real hours next to this table. If any column gets more than 10% above the others, the member with the lowest total takes the next review or test task from them.</li>"
  "</ul>")
A("<p class='small'>This table is the record the syllabus uses to adjust individual grades. We will update it with real hours in the Week 14 report and at M5.</p>")

# 5. WBS
A('<h2 class="pb">5. Work Breakdown Structure (supporting artifact)</h2>')
A("<p>Level 1 is the phase. Level 2 is the task. Every task ID is the same as in the Task List, Table 1, and Table 2. Milestones close each phase.</p>")
wrows = [["<b>0</b>", "<b>Verified Student Sublease Marketplace</b>", "", "", "", ""]]
wcls = ["tot"]
wrows.append(["<b>0.1</b>", "<b>Course deliverables (project management)</b>", "", "Team", "", "M0a to M0e (done), M1, M3, M11"])
wcls.append("ms")
for ph, (name, when, what) in PHASES.items():
    pts = [t for t in TASKS if t["phase"] == ph]
    gates = sorted({GATE[t["id"]] for t in pts}, key=lambda x: int(x[1:]))
    if ph == 2:
        gates = ["M5"] + gates
    if ph == 4:
        gates = gates[:1] + ["M9"] + gates[1:]
    wrows.append([f"<b>{ph}</b>", f"<b>{name}</b> ({when})", E(what), "", f"{sum(t['E'] for t in pts):.1f} h", ", ".join(gates)])
    wcls.append("ms")
    for j, t in enumerate(pts, 1):
        wrows.append([f"{ph}.{j}", f"{t['id']}: {E(t['text'])}", E(t["module"]), SHORT[t["owner"]], f"{t['E']} h", GATE[t["id"]]])
        wcls.append("")
A(table(["WBS code", "Phase / task", "Module", "Owner", "Hours", "Milestone"], wrows, ["6%", "52%", "18%", "8%", "6%", "10%"], wcls))

# 6. Risks
A('<h2 class="pb">6. Risk Register (supporting artifact)</h2>')
A("<p>Likelihood and impact are Low, Medium, or High. Strategy is avoid, reduce, transfer, or accept. "
  "<b>Where in Table 1</b> shows the task rows, buffer blocks, or milestones that carry the risk. High-impact schedule risks (RK1, RK2, RK4, RK8) are listed on those rows in Table 1.</p>")
A(table(["ID", "Category", "Risk", "L", "I", "Strategy", "Mitigation", "Owner", "Trigger", "Where in Table 1"],
        [[f"<b>{r['id']}</b>", r["cat"], E(r["risk"]), r["L"], r["I"], r["strat"], E(r["mit"]), SHORT[r["owner"]], E(r["trigger"]), E(r["where"])] for r in RISKS],
        ["4%", "7%", "18%", "6%", "6%", "6%", "24%", "6%", "12%", "11%"]))
cats = sorted({r["cat"] for r in RISKS})
strats = sorted({r["strat"] for r in RISKS})
A(f"<p>{len(RISKS)} risks. Categories used: {', '.join(cats)}. Strategies used: {', '.join(strats)}.</p>")

# 7. Consistency
A("<h2>7. Consistency check</h2>")
A("<p>The PDF, Tasklist.md, and the CSV files are all made from one file (Planning/plan.py). So every task has the same ID, name, and owner everywhere. The check below is run by the build script.</p>")
md_text = open(os.path.join(OUT, "Tasklist.md")).read()
crow = []
for t in TASKS:
    ok_md = f"{t['id']}. {t['text']}" in md_text and TEAM[t["owner"]] in md_text
    crow.append([t["id"], SHORT[t["owner"]], "✓", "✓" if ok_md else "✗", "✓", "✓", "✓", "✓" if t["eff"][t["owner"]] == max(t["eff"].values()) else "✗"])
A(table(["ID", "Owner", "Task List", "Tasklist.md", "WBS", "Table 1", "Table 2", "Owner has largest share"], crow))

doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(P)}</body></html>"
HTML = os.path.join(OUT, "A8_Plan.html")
open(HTML, "w").write(doc)
PDF = os.path.join(OUT, "A8_Plan_raw.pdf")
subprocess.run(["wkhtmltopdf", "--enable-local-file-access", "-q", "-O", "Landscape", "-s", "Letter",
                "-T", "13mm", "-B", "13mm", "-L", "11mm", "-R", "11mm",
                "--footer-font-size", "7", "--footer-left", "Assignment 8 | Verified Student Sublease Marketplace | Vanganuri, Asker Fredy, Aidja",
                "--footer-right", "page [page] of [topage]", HTML, PDF], check=False)
# page numbers + metadata
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
r = PdfReader(PDF); wtr = PdfWriter(); n = len(r.pages)
for i, pg in enumerate(r.pages, 1):
    pw, ph = float(pg.mediabox.width), float(pg.mediabox.height)
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(pw, ph)); c.setFont("Helvetica", 7); c.setFillGray(0.4)
    c.drawString(31, 18, "Assignment 8 | Verified Student Sublease Marketplace | Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja")
    c.drawRightString(pw - 31, 18, f"page {i} of {n}"); c.save(); buf.seek(0)
    pg.merge_page(PdfReader(buf).pages[0]); wtr.add_page(pg)
wtr.add_metadata({"/Title": "Assignment 8: Task List, Milestones, Timeline, and Effort Matrix", "/Author": "Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja"})
FINAL = os.path.join(OUT, "A8_Task_List_Milestones_Timeline_Effort.pdf")
with open(FINAL, "wb") as f: wtr.write(f)
os.remove(PDF)
print("built", FINAL, {k: round(v, 1) for k, v in col.items()}, "gap", round(gap, 1))
