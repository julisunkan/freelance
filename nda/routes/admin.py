from flask import Blueprint, render_template, request, redirect, url_for, abort
import models

admin_bp = Blueprint('admin', __name__)

ADMIN_TOKEN = 'julisunkan'


def _check():
    return (request.args.get('token') or request.form.get('token')) == ADMIN_TOKEN


@admin_bp.route('/julisunkan')
def admin_panel():
    if not _check():
        abort(403)
    settings = models.get_all_settings()
    templates = models.get_all_templates()
    conn = models.get_db()
    total = conn.execute('SELECT COUNT(*) FROM ndas').fetchone()[0]
    signed = conn.execute("SELECT COUNT(*) FROM ndas WHERE status='signed'").fetchone()[0]
    recent = conn.execute(
        'SELECT n.*, t.name as template_name FROM ndas n '
        'LEFT JOIN templates t ON n.template_id=t.id '
        'ORDER BY n.created_at DESC LIMIT 10'
    ).fetchall()
    conn.close()
    return render_template('admin.html', settings=settings, token=ADMIN_TOKEN,
                           total=total, signed=signed, recent=[dict(r) for r in recent],
                           templates=templates)


@admin_bp.route('/julisunkan/settings', methods=['POST'])
def save_settings():
    if not _check():
        abort(403)
    for key in ['groq_api_key', 'groq_model', 'ai_enabled', 'default_tone']:
        val = request.form.get(key, '').strip()
        models.set_setting(key, val)
    return redirect(url_for('admin.admin_panel', token=ADMIN_TOKEN))
