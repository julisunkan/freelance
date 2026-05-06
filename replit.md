# Freelancer Suite

A dual-app web platform for freelancers: a **Proposal Builder** to create and manage client proposals, and an **NDA Generator** to produce, e-sign, and audit Non-Disclosure Agreements — both with AI-powered content enhancement via Groq.

## Run & Operate

- **Run**: `python main.py` (starts combined server on port 5000)
- **Proposal Builder**: served at `/`
- **NDA Generator**: served at `/nda`
- **Admin panel**: `/julisunkan?token=julisunkan` (both apps have separate admin panels)
- **Required env vars**: None at startup. Groq API key is stored per-app in SQLite via the admin panel.

## Stack

- Python 3.12, Flask 3.1.1, Werkzeug 3.1.8
- SQLite (two separate databases: `freelancer.db` and `nda/nda.db`)
- Jinja2 templates, Bootstrap 5.3 (Proposal Builder), custom CSS (NDA Generator)
- ReportLab (PDF export), python-docx (Word export), Groq API (AI)
- Werkzeug DispatcherMiddleware to combine both apps under one server

## Where things live

- `main.py` — entry point; combines both apps via DispatcherMiddleware
- `app.py` — Proposal Builder Flask app
- `nda/app.py` — NDA Generator Flask app
- `models.py` / `nda/models.py` — SQLite schema and DB helpers
- `routes/` / `nda/routes/` — Blueprint-based routing
- `services/` / `nda/services/` — AI, PDF/DOCX generation logic
- `templates/` / `nda/templates/` — Jinja2 HTML templates
- `static/` / `nda/static/` — CSS and JS assets
- `requirements.txt` — Python dependencies

## Architecture decisions

- Two independent Flask apps mounted under a single Werkzeug server using DispatcherMiddleware — avoids port management complexity and lets both apps share one Replit workflow
- Module isolation in `main.py`: NDA app is loaded first via `importlib` and its module names are renamed in `sys.modules` before the root app loads, preventing name collisions for `models`, `routes`, and `services`
- Groq API key stored in SQLite settings table (not environment variable) — allows runtime configuration via the admin panel without redeploying
- Token-based admin access (`ADMIN_SECRET = "julisunkan"`) — simple protection for internal admin routes, no user auth system

## Product

- **Proposal Builder**: Create/edit proposals with a Quill WYSIWYG editor, AI-generate or improve content with Groq, export to PDF/Word, share via unique token link, track status (Draft/Sent/Accepted/Rejected)
- **NDA Generator**: Choose from 20 industry-specific templates, fill party details, AI-enhance legal language by tone, e-sign with signature pad, export to PDF, audit trail logging
- Both apps installable as PWAs (manifest.json + service workers)

## User preferences

_Populate as you build_

## Gotchas

- Module loading order in `main.py` is critical — NDA app must load before Proposal Builder or module name collisions occur
- DispatcherMiddleware sets `SCRIPT_NAME=/nda` so Flask's `url_for()` inside the NDA app automatically produces `/nda/...` URLs; do not hardcode `/nda` prefixes in NDA templates
- The `requests` version warning (urllib3/chardet mismatch) is cosmetic and does not affect functionality
- SQLite databases are created automatically on first run via `init_db()` in each app

## Pointers

- Groq API docs: https://console.groq.com/docs
- Flask DispatcherMiddleware: https://werkzeug.palletsprojects.com/en/latest/middleware/dispatcher/
