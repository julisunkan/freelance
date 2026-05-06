# Freelancer Proposal Builder

A single-user Flask web app for creating, editing, scoring, and exporting freelance proposals with AI generation via Groq.

## Run & Operate
```
python main.py
```
No required env vars — Groq API key is stored in the SQLite `settings` table via the Admin panel.

## Stack
- **Backend**: Python 3, Flask 3.1.1
- **Database**: SQLite (freelancer.db in project root)
- **PDF export**: ReportLab 4.2.5
- **DOCX export**: python-docx 1.1.2
- **AI**: Groq API (llama3-70b-8192) via `requests`
- **Frontend**: Bootstrap 5.3 CDN + Bootstrap Icons CDN + Quill JS 1.3 CDN

## Where things live
```
app.py              Flask app factory, blueprint registration
main.py             Entry point
models.py           All SQLite schema, helpers, and 10 seeded templates
routes/
  proposals.py      CRUD, public share, sections page
  admin.py          /julisunkan admin panel (token-protected)
  export_routes.py  PDF / DOCX / TXT download endpoints
  api.py            Score, AI generate/improve, sections/templates AJAX
services/
  ai_service.py     Groq API calls
  pdf_service.py    ReportLab PDF generation
  docx_service.py   python-docx DOCX generation
  txt_service.py    Plain-text export
  scoring_service.py  0–100 score with feedback
templates/          Jinja2 HTML (base, dashboard, editor, proposal_view,
                    template_selector, sections, admin, reports,
                    public_view, 404, 500)
static/
  style.css         Custom CSS (sidebar layout, indigo brand)
  script.js         Notification system + score modal
  editor.js         Quill editor, AI buttons, template/section loading
  sw.js             PWA service worker
  manifest.json     PWA manifest
```

## Architecture decisions
- No authentication — single-user tool; admin protected by secret token (`julisunkan`)
- ReportLab used for PDF (pure Python, no system deps like WeasyPrint requires)
- Groq API key stored in DB `settings` table, never in code or env vars exposed to frontend
- All exports are server-side `send_file` — no client-side blob downloads
- 10 templates seeded on first run only (`COUNT(*) == 0` guard)

## Product
- Dashboard with stats (total, accepted, sent, acceptance rate) and status filters
- Proposal CRUD with Quill WYSIWYG editor and placeholder support (`{{ client_name }}` etc.)
- Load any of 10 professional templates or insert reusable sections
- AI: generate full proposal or improve existing text (requires Groq API key)
- Proposal scoring (0–100) across clarity, structure, pricing, call-to-action
- Export to PDF, DOCX, or TXT with export history log
- Shareable public link per proposal (no-auth view, tracks view count)
- Report proposals; admin reviews/ignores via `/julisunkan?token=julisunkan`
- PWA manifest + service worker for offline shell access

## User preferences
- Admin route: `/julisunkan?token=julisunkan` — no login required
- Brand color: indigo `#4f46e5`
- Sidebar layout (dark `#1e1b4b` sidebar, light content area)

## Gotchas
- Delete `freelancer.db` to reset all data and re-seed templates
- Quill editor content is synced to hidden `<input name="content">` on form submit via `editor.js`
- `editor.js` is loaded only on editor pages; `script.js` is loaded on all pages
