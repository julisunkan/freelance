# Freelancer Suite — Proposal Builder + NDA Generator

Two standalone Flask apps: a Proposal Builder (port 5000) and an NDA Generator (port 8080).

## Run & Operate
```
python main.py          # Proposal Builder — port 5000 (workflow: "Start application")
python nda/main.py      # NDA Generator   — port 8080 (workflow: "NDA Generator")
```
No required env vars — Groq API keys stored in each app's SQLite `settings` table via `/julisunkan?token=julisunkan`.

## Stack
- **Backend**: Python 3.12, Flask 3.1.1
- **Databases**: SQLite — `freelancer.db` (proposals), `nda/nda.db` (NDAs)
- **PDF export**: ReportLab 4.2.5 (both apps)
- **DOCX export**: python-docx 1.1.2 (Proposal Builder only)
- **AI**: Groq API via `requests` — configurable model per app
- **Frontend**: Bootstrap 5.3 CDN (Proposal Builder) · custom CSS + Vanilla JS (NDA Generator)
- **E-Sign**: signature_pad 4.1.7 CDN (NDA Generator)

## Where things live
```
# Proposal Builder
app.py / main.py / models.py
routes/proposals.py     CRUD, public share, sections
routes/admin.py         /julisunkan admin
routes/export_routes.py PDF / DOCX / TXT
routes/api.py           Score, AI generate/improve, sections CRUD, templates
services/               ai_service, pdf_service, docx_service, txt_service, scoring_service
templates/              base, dashboard, editor, proposal_view, template_selector, sections, admin, reports, public_view
static/script.js (v=3), editor.js (v=3), style.css, manifest.json, sw.js

# NDA Generator
nda/app.py / nda/main.py / nda/models.py
nda/routes/main.py      /, /create, /nda/<public_id>
nda/routes/signing.py   /nda/sign/a/<token>, /nda/sign/b/<token>
nda/routes/export.py    /nda/download/<public_id>
nda/routes/admin.py     /julisunkan (token-protected)
nda/routes/audit.py     /audit/<public_id>
nda/services/ai_service.py   Groq NDA enhancement
nda/services/pdf_service.py  ReportLab PDF with signatures
nda/templates/          base, index, view_nda, sign, admin, audit, error
nda/static/             style.css, app.js, manifest.json, sw.js, icons/
nda/generated/          PDF output directory
```

## Architecture decisions
- Two completely independent Flask apps — no blueprint sharing between them
- NDA Generator: no login at all; access via `public_id` (view) or `sign_token_a/b` (sign)
- All PDFs generated server-side with ReportLab `send_file` — no client-side blob downloads
- Signatures stored as base64 data URLs in SQLite; embedded in PDF via ReportLab Image
- 20 NDA templates defined as Python dicts + TEMPLATE_SPECS in `nda/models.py` (not separate files)
- Audit log records every view, sign, and download event with IP + user agent
- NDA locks to "signed" status automatically when both signatures are collected
- Groq API key in DB `settings` table, never in code/env; AI skipped gracefully if unconfigured

## Product — Proposal Builder
- Dashboard with stats (total, accepted, sent, acceptance rate) and status filters
- Proposal CRUD with Quill WYSIWYG editor and placeholder support
- 10 professional templates; reusable sections with full REST API
- AI: generate or improve text; proposal scoring (0–100)
- Export to PDF, DOCX, TXT; shareable public link; PWA installable

## Product — NDA Generator
- 20 industry templates (Startup, Corporate, Healthcare, Finance, M&A, etc.)
- Groq AI enhancement with configurable tone (formal/strict/startup/legal-heavy)
- Token-based e-signing — Party A and Party B each get a unique link, no login required
- canvas-based signature pad (signature_pad CDN); signatures embedded in PDF
- Status flow: draft → sent → partial → signed (auto-locked)
- Per-document audit log (all views, signs, downloads with IP)
- Server-side PDF with signatures, timestamps, and audit metadata
- PWA installable; inline-only notifications (no alert/popup/modal)
- Admin at `/julisunkan?token=julisunkan` — Groq config + system overview

## User preferences
- Admin route: `/julisunkan?token=julisunkan` — no login required (both apps)
- Brand color: indigo `#4f46e5` / dark `#1e1b4b` (both apps)
- Inline-only notifications in NDA app (`notify(msg, type)` in app.js)

## Gotchas
- Delete `freelancer.db` to reset Proposal Builder; delete `nda/nda.db` to reset NDA Generator
- NDA templates are seeds — re-seeded only when `templates` table is empty
- Quill editor syncs to hidden `<input name="content">` on submit (Proposal Builder only)
- `editor.js` loaded only on editor pages; `script.js` on all Proposal Builder pages
- NDA port is 8080; Replit preview pane shows port 5000 (Proposal Builder) — access NDA via dev domain on port 8080
