from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import models

ADMIN_SECRET = "julisunkan"

admin_bp = Blueprint('admin', __name__)


def _check_admin():
    token = request.args.get('token') or request.form.get('token')
    return token == ADMIN_SECRET


@admin_bp.route('/julisunkan')
def admin_panel():
    if not _check_admin():
        abort(403)
    settings = models.get_all_settings()
    return render_template('admin.html', settings=settings, token=ADMIN_SECRET)


@admin_bp.route('/julisunkan/settings', methods=['POST'])
def save_settings():
    if request.form.get('token') != ADMIN_SECRET:
        abort(403)
    for key in ['groq_api_key', 'app_name', 'default_currency']:
        value = request.form.get(key, '').strip()
        models.set_setting(key, value)
    flash('Settings saved successfully!', 'success')
    return redirect(url_for('admin.admin_panel', token=ADMIN_SECRET))


@admin_bp.route('/julisunkan/reports')
def admin_reports():
    if not _check_admin():
        abort(403)
    status = request.args.get('status', '')
    reports = models.get_all_reports(status if status else None)
    return render_template('reports.html', reports=reports,
                           current_status=status, token=ADMIN_SECRET)


@admin_bp.route('/julisunkan/reports/<int:rid>/status', methods=['POST'])
def update_report(rid):
    if request.form.get('token') != ADMIN_SECRET:
        abort(403)
    status = request.form.get('status')
    if status in ('Open', 'Reviewed', 'Ignored'):
        models.update_report_status(rid, status)
        flash(f'Report marked as {status}.', 'success')
    return redirect(url_for('admin.admin_reports', token=ADMIN_SECRET))
