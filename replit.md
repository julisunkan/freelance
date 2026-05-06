# Freelancer Suite + Online ID Validator

A multi-app web platform combining three independent Flask tools:
- **Proposal Builder** — create, manage, and export client proposals with AI content generation
- **NDA Generator** — produce, e-sign, and audit Non-Disclosure Agreements with AI enhancement
- **Online ID Validator** — upload identity documents for OCR extraction, image quality analysis, duplicate detection, risk scoring, and Groq AI-powered fraud analysis

## Run & Operate

- **Run**: `python main.py` (starts all three apps on port 5000)
- **Proposal Builder**: `/`
- **NDA Generator**: `/nda`
- **Online ID Validator**: `/onlineid`
- **Admin panels**:
  - Proposal Builder: `/julisunkan?token=julisunkan`
  - NDA Generator: `/nda/admin?token=julisunkan`
  - ID Validator: `/onlineid/julisunkan?token=julisunkan`
  - ID Validator Settings: `/onlineid/julisunkan/settings?token=julisunkan`
- **Required env vars**: None at startup. Groq API keys stored in SQLite via admin panels.

## Stack

- Python 3.12, Flask 3.1.1, Werkzeug 3.1.8
- SQLite — three separate databases: `freelancer.db`, `nda/nda.db`, `onlineid/instance/app.db`
- SQLAlchemy ORM (ID Validator only), raw sqlite3 (Proposal Builder + NDA)
- Jinja2 templates, Bootstrap 5.3 (Proposal Builder), custom CSS (NDA + ID Validator)
- ReportLab (PDF), python-docx (Word), Groq API (AI), pytesseract + Tesseract (OCR), OpenCV (image analysis)
- Werkzeug DispatcherMiddleware to combine all apps under one server

## Where things live

- `main.py` — entry point; combines all three apps via DispatcherMiddleware
- `app.py` / `models.py` / `routes/` / `services/` / `templates/` / `static/` — Proposal Builder
- `nda/` — NDA Generator (mirrors root structure)
- `onlineid/app.py` — ID Validator Flask app
- `onlineid/models.py` — SQLAlchemy models (IDRecord, Settings)
- `onlineid/utils/` — ocr.py, image_checks.py, scoring.py, groq_ai.py, face_match.py, hashing.py
- `onlineid/templates/` / `onlineid/static/` — ID Validator UI and PWA assets
- `onlineid/uploads/` — uploaded ID images
- `requirements.txt` — Python dependencies

## Architecture decisions

- Three independent Flask apps mounted via DispatcherMiddleware — one Replit workflow, one port
- Module isolation in `main.py`: each sub-app loaded with `importlib`, generic module names (models, utils, config) evicted from `sys.modules` between loads to prevent collisions
- Werkzeug sets `SCRIPT_NAME` on sub-app requests — `url_for()` automatically produces correct prefixed URLs; avoid hardcoding `/nda` or `/onlineid` prefixes in templates
- Groq API keys stored in SQLite settings tables — runtime configuration via admin panels, no deploy needed
- Token-based admin access (`julisunkan`) — intentional, no user auth system
- OCR/CV features degrade gracefully when libraries unavailable (TESSERACT_AVAILABLE / CV2_AVAILABLE guards)

## Product

- **Proposal Builder**: WYSIWYG editor (Quill), AI content generation, PDF/Word export, shareable token links, status tracking (Draft/Sent/Accepted/Rejected)
- **NDA Generator**: 20 industry templates, party details, AI tone enhancement, e-sign with signature pad, PDF export, audit trail
- **Online ID Validator**: Upload front/back ID + optional selfie, OCR extraction, structured field parsing, image quality analysis, SHA256 duplicate detection, risk scoring (LOW/MEDIUM/HIGH), AI auto-fix and fraud analysis via Groq, admin record management
- All three apps are PWA-installable (manifest.json + service workers)

## User preferences

_Populate as you build_

## Gotchas

- Module loading order in `main.py` is critical — NDA and onlineid apps must load before Proposal Builder
- `_evict_generic_modules(prefix)` must be called after each sub-app load to prevent `models`, `utils`, `config` collisions
- DispatcherMiddleware sets `SCRIPT_NAME` — use `request.script_root` in templates, not hardcoded paths
- The `requests` version warning (urllib3/chardet mismatch) is cosmetic and does not affect functionality
- SQLite databases are created automatically on first run via `init_db()` in each app
- face_recognition is optional — face match returns `match: None` with an error message if unavailable

## Pointers

- Groq API docs: https://console.groq.com/docs
- Flask DispatcherMiddleware: https://werkzeug.palletsprojects.com/en/latest/middleware/dispatcher/
- Tesseract Nix package: `tesseract`
