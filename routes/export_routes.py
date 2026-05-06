import io
from flask import Blueprint, send_file, abort
import models
from services.pdf_service import generate_pdf
from services.docx_service import generate_docx
from services.txt_service import generate_txt

export_bp = Blueprint('export', __name__)


@export_bp.route('/proposals/<int:pid>/export/pdf')
def export_pdf(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        abort(404)
    buf = generate_pdf(proposal)
    models.log_export(pid, 'pdf')
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'proposal_{pid}.pdf')


@export_bp.route('/proposals/<int:pid>/export/docx')
def export_docx(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        abort(404)
    buf = generate_docx(proposal)
    models.log_export(pid, 'docx')
    return send_file(
        buf,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=True,
        download_name=f'proposal_{pid}.docx'
    )


@export_bp.route('/proposals/<int:pid>/export/txt')
def export_txt(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        abort(404)
    content = generate_txt(proposal)
    buf = io.BytesIO(content.encode('utf-8'))
    models.log_export(pid, 'txt')
    return send_file(buf, mimetype='text/plain',
                     as_attachment=True,
                     download_name=f'proposal_{pid}.txt')
