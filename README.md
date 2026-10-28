# CS5001: Senior Capstone

## 1. Project

**Roost: a verified student sublease marketplace for UC.** Only UC email addresses (`@mail.uc.edu`, `@uc.edu`) can join. Seekers swipe, list or map listings, filter by whole-term dates and distance from campus, and see rooms ranked by roommate fit. Hosts must confirm landlord consent and can split the sublet fee. Chat is real-time, with contact details hidden until shared and messages deleted after 30 days.

- **Prototype (code, setup, security notes):** [roost-uc-sublease](https://github.com/trivinity/roost-uc-sublease)
- **Live demo:** https://roost-uc-sublease.vercel.app
- **Stack:** Next.js on Vercel, Supabase (Auth, Postgres with row-level security, Realtime, Storage), Expo phone app

## 2. Team

Danvanth Vanganuri, Jovan Jose Asker Fredy, Mohamed Aidja (Team JDM).

## 3. Documents

**Current documents** (these match the prototype):

| Document | Assignment |
|---|---|
| [Requirements_Document.md](Requirements_Document.md) ([PDF](Requirements_Document.pdf)) | A9: Requirements Document v2.0 |
| [Technical_Specification.md](Technical_Specification.md) ([PDF](Technical_Specification.pdf)) | A9: Technical Specification v2.0 (traces to Requirements Document v2.0); §7 logs every design change since D2 |
| [User_Stories.md](User_Stories.md) | A4: user stories and use cases, v2.0 (revised to match the prototype) |
| [Tasklist.md](Tasklist.md) | A8 task list, v2.0 (re-baselined to the prototype) |
| [Project-Description.md](Project-Description.md) | Week 3 project description |

**Earlier design records** (kept unchanged as graded; superseded where TS v2.0 §7 says so):

| Document | Assignment |
|---|---|
| [D0_High_Level_Design.pdf](D0_High_Level_Design.pdf) and `D0_*.drawio` | A5: Design D0 (block diagram, data flows, decision log) |
| [D1_Detailed_Design.pdf](D1_Detailed_Design.pdf) | A6: Design D1 (C3 Listing, C5 Search) |
| [D2_Detailed_Design.pdf](D2_Detailed_Design.pdf), [D2_figures/](D2_figures/), [D2_source/](D2_source/) | A7: Design D2 |
| [Peer_Review_Notes.md](Peer_Review_Notes.md) | A7: peer design review (with a 2026-10-28 status note) |
| [A8_Task_List_Milestones_Timeline_Effort.pdf](A8_Task_List_Milestones_Timeline_Effort.pdf), [Planning/](Planning/) | A8: milestones, timeline, effort (baseline) |

PDFs for A9 are built with `python3 A9_source/build.py` (it needs `pip install markdown` and Google Chrome).
