import io
from flask import Blueprint, send_file, abort, request
import models
from services.pdf_service import generate_nda_pdf

export_bp = Blueprint('export', __name__)


def _get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '')


@export_bp.route('/nda/download/<public_id>')
def download_pdf(public_id):
    nda = models.get_nda(public_id)
    if not nda:
        abort(404)
    buf = generate_nda_pdf(nda)
    models.log_audit(nda['id'], 'PDF downloaded', _get_ip(), request.user_agent.string)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'nda_{public_id}.pdf'
    )
