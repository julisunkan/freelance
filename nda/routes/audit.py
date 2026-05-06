from flask import Blueprint, render_template, abort
import models

audit_bp = Blueprint('audit', __name__)


@audit_bp.route('/audit/<public_id>')
def audit_log(public_id):
    nda = models.get_nda(public_id)
    if not nda:
        abort(404)
    logs = models.get_audit_log(public_id)
    return render_template('audit.html', nda=nda, logs=logs)
