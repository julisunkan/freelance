import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)
app.secret_key = os.environ.get('ONLINEID_SECRET_KEY', 'onlineid-secret-key-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ADMIN_TOKEN = 'julisunkan'

from models import init_db, SessionLocal, IDRecord, Settings, get_settings
from utils.ocr import extract_text, extract_structured_fields
from utils.image_checks import analyze_image
from utils.hashing import hash_file
from utils.scoring import compute_risk
from utils.groq_ai import ai_extract_and_fix, ai_risk_analysis
from utils.face_match import compare_faces

with app.app_context():
    init_db()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(path)
        return unique_name
    return None


# ── Public Routes ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    db = SessionLocal()
    try:
        front = request.files.get('front_id')
        back = request.files.get('back_id')
        selfie = request.files.get('selfie')

        if not front or not front.filename:
            flash('Front ID image is required.', 'danger')
            return redirect(url_for('index'))

        fn_front = save_upload(front)
        if not fn_front:
            flash('Invalid file type for front ID.', 'danger')
            return redirect(url_for('index'))

        fn_back = save_upload(back)
        fn_selfie = save_upload(selfie)

        front_path = os.path.join(UPLOAD_FOLDER, fn_front)

        file_hash = hash_file(front_path)
        existing = db.query(IDRecord).filter_by(file_hash=file_hash).first()
        is_duplicate = existing is not None and existing.filename_front != fn_front

        ocr_text = extract_text(front_path)
        if fn_back:
            back_text = extract_text(os.path.join(UPLOAD_FOLDER, fn_back))
            if back_text:
                ocr_text = ocr_text + '\n' + back_text

        structured = extract_structured_fields(ocr_text)

        img_analysis = analyze_image(front_path)

        face_ok = True
        if fn_selfie:
            face_result = compare_faces(front_path, os.path.join(UPLOAD_FOLDER, fn_selfie))
            if face_result.get('match') is False:
                face_ok = False

        risk = compute_risk(structured, img_analysis, is_duplicate, face_ok)

        record = IDRecord(
            filename_front=fn_front,
            filename_back=fn_back,
            filename_selfie=fn_selfie,
            extracted_text=ocr_text,
            structured_data=json.dumps(structured),
            risk_level=risk,
            file_hash=file_hash,
            is_duplicate=1 if is_duplicate else 0,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
        return redirect(url_for('result', record_id=record_id))
    finally:
        db.close()


@app.route('/result/<int:record_id>')
def result(record_id):
    db = SessionLocal()
    try:
        record = db.query(IDRecord).filter_by(id=record_id).first()
        if not record:
            abort(404)
        structured = {}
        try:
            structured = json.loads(record.structured_data or '{}')
        except Exception:
            pass
        return render_template('result.html', record=record, structured=structured)
    finally:
        db.close()


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ── Admin Routes ───────────────────────────────────────────────────────────

def _check_admin():
    token = request.args.get('token') or request.form.get('token')
    return token == ADMIN_TOKEN


@app.route('/julisunkan')
def admin():
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        records = db.query(IDRecord).order_by(IDRecord.created_at.desc()).all()
        parsed = []
        for r in records:
            try:
                s = json.loads(r.structured_data or '{}')
            except Exception:
                s = {}
            parsed.append((r, s))
        return render_template('admin.html', records=parsed, token=ADMIN_TOKEN)
    finally:
        db.close()


@app.route('/julisunkan/edit/<int:record_id>', methods=['GET', 'POST'])
def admin_edit(record_id):
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        record = db.query(IDRecord).filter_by(id=record_id).first()
        if not record:
            abort(404)

        if request.method == 'POST':
            record.extracted_text = request.form.get('extracted_text', record.extracted_text)
            new_structured = request.form.get('structured_data', record.structured_data)
            try:
                json.loads(new_structured)
                record.structured_data = new_structured
            except Exception:
                flash('Invalid JSON in structured data.', 'danger')
            record.risk_level = request.form.get('risk_level', record.risk_level)
            db.commit()
            flash('Record updated successfully.', 'success')
            return redirect(url_for('admin_edit', record_id=record_id, token=ADMIN_TOKEN))

        structured = {}
        try:
            structured = json.loads(record.structured_data or '{}')
        except Exception:
            pass
        return render_template('edit.html', record=record, structured=structured, token=ADMIN_TOKEN)
    finally:
        db.close()


@app.route('/julisunkan/ai-fix/<int:record_id>', methods=['POST'])
def admin_ai_fix(record_id):
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        record = db.query(IDRecord).filter_by(id=record_id).first()
        if not record:
            abort(404)
        settings = get_settings(db)
        api_key = settings.groq_api_key if settings else ''
        result = ai_extract_and_fix(record.extracted_text or '', api_key)
        if result:
            structured = {
                'full_name': result.get('name', ''),
                'date_of_birth': result.get('dob', ''),
                'id_number': result.get('id_number', ''),
                'expiry_date': result.get('expiry_date', ''),
                'notes': result.get('notes', ''),
            }
            record.structured_data = json.dumps(structured)
            db.commit()
            flash('AI auto-fix applied successfully.', 'success')
        else:
            flash('AI fix failed. Check your Groq API key in settings.', 'danger')
        return redirect(url_for('admin_edit', record_id=record_id, token=ADMIN_TOKEN))
    finally:
        db.close()


@app.route('/julisunkan/ai-risk/<int:record_id>', methods=['POST'])
def admin_ai_risk(record_id):
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        record = db.query(IDRecord).filter_by(id=record_id).first()
        if not record:
            abort(404)
        settings = get_settings(db)
        api_key = settings.groq_api_key if settings else ''
        structured = {}
        try:
            structured = json.loads(record.structured_data or '{}')
        except Exception:
            pass
        result = ai_risk_analysis(record.extracted_text or '', structured, api_key)
        if result:
            record.risk_level = result.get('risk_level', record.risk_level)
            db.commit()
            flash(f'AI risk recalculated: {record.risk_level}. Reasons: {", ".join(result.get("reasons", []))}', 'success')
        else:
            flash('AI risk analysis failed. Check your Groq API key in settings.', 'danger')
        return redirect(url_for('admin_edit', record_id=record_id, token=ADMIN_TOKEN))
    finally:
        db.close()


@app.route('/julisunkan/settings', methods=['GET', 'POST'])
def admin_settings():
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        settings = get_settings(db)
        if not settings:
            from models import Settings as S
            settings = S(groq_api_key='')
            db.add(settings)
            db.commit()
            db.refresh(settings)

        if request.method == 'POST':
            new_key = request.form.get('groq_api_key', '').strip()
            settings.groq_api_key = new_key
            db.commit()
            flash('Settings saved successfully.', 'success')
            return redirect(url_for('admin_settings', token=ADMIN_TOKEN))

        return render_template('settings.html', settings=settings, token=ADMIN_TOKEN)
    finally:
        db.close()


@app.route('/julisunkan/batch-ai-fix', methods=['POST'])
def admin_batch_ai_fix():
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        settings = get_settings(db)
        api_key = settings.groq_api_key if settings else ''
        if not api_key:
            flash('No Groq API key configured. Add it in Settings first.', 'danger')
            return redirect(url_for('admin', token=ADMIN_TOKEN))

        records = db.query(IDRecord).order_by(IDRecord.created_at.desc()).all()
        fixed = 0
        failed = 0
        for record in records:
            if not record.extracted_text:
                continue
            result = ai_extract_and_fix(record.extracted_text, api_key)
            if result:
                structured = {
                    'full_name':    result.get('name', ''),
                    'date_of_birth': result.get('dob', ''),
                    'id_number':    result.get('id_number', ''),
                    'expiry_date':  result.get('expiry_date', ''),
                    'notes':        result.get('notes', ''),
                }
                record.structured_data = json.dumps(structured)
                fixed += 1
            else:
                failed += 1
        db.commit()

        if fixed:
            flash(f'Batch AI fix complete — {fixed} record(s) updated, {failed} skipped.', 'success')
        else:
            flash('No records were updated. Ensure your Groq API key is valid.', 'warning')
        return redirect(url_for('admin', token=ADMIN_TOKEN))
    finally:
        db.close()


@app.route('/julisunkan/batch-ai-risk', methods=['POST'])
def admin_batch_ai_risk():
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        settings = get_settings(db)
        api_key = settings.groq_api_key if settings else ''
        if not api_key:
            flash('No Groq API key configured. Add it in Settings first.', 'danger')
            return redirect(url_for('admin', token=ADMIN_TOKEN))

        records = db.query(IDRecord).order_by(IDRecord.created_at.desc()).all()
        updated = 0
        failed = 0
        for record in records:
            if not record.extracted_text:
                continue
            structured = {}
            try:
                structured = json.loads(record.structured_data or '{}')
            except Exception:
                pass
            result = ai_risk_analysis(record.extracted_text, structured, api_key)
            if result and result.get('risk_level') in ('LOW', 'MEDIUM', 'HIGH'):
                record.risk_level = result['risk_level']
                updated += 1
            else:
                failed += 1
        db.commit()

        if updated:
            flash(f'Batch risk recalculation complete — {updated} record(s) updated, {failed} skipped.', 'success')
        else:
            flash('No records were updated. Ensure your Groq API key is valid.', 'warning')
        return redirect(url_for('admin', token=ADMIN_TOKEN))
    finally:
        db.close()


@app.route('/julisunkan/delete/<int:record_id>', methods=['POST'])
def admin_delete(record_id):
    if not _check_admin():
        abort(403)
    db = SessionLocal()
    try:
        record = db.query(IDRecord).filter_by(id=record_id).first()
        if record:
            db.delete(record)
            db.commit()
            flash('Record deleted.', 'success')
        return redirect(url_for('admin', token=ADMIN_TOKEN))
    finally:
        db.close()


# ── PWA / Static ───────────────────────────────────────────────────────────

@app.after_request
def add_headers(response):
    if request.path.endswith('/sw.js'):
        scope = (request.script_root or '') + '/'
        response.headers['Service-Worker-Allowed'] = scope
    return response


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
