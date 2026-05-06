from flask import Blueprint, render_template, request, jsonify, abort
import models

signing_bp = Blueprint('signing', __name__)


def _get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '')


@signing_bp.route('/nda/sign/a/<token>')
def sign_a(token):
    nda = models.get_nda_by_token(token)
    if not nda or nda['sign_token_a'] != token:
        abort(404)
    if nda['status'] == 'signed':
        return render_template('sign.html', nda=nda, party='a', already_signed=True,
                               locked=True)
    if nda['signature_a']:
        return render_template('sign.html', nda=nda, party='a', already_signed=True,
                               locked=False)
    models.log_audit(nda['id'], 'Party A viewed signing page', _get_ip(), request.user_agent.string)
    if nda['status'] == 'draft':
        models.update_nda_status(nda['id'], 'sent')
    return render_template('sign.html', nda=nda, party='a', already_signed=False, locked=False)


@signing_bp.route('/nda/sign/b/<token>')
def sign_b(token):
    nda = models.get_nda_by_token(token)
    if not nda or nda['sign_token_b'] != token:
        abort(404)
    if nda['status'] == 'signed':
        return render_template('sign.html', nda=nda, party='b', already_signed=True,
                               locked=True)
    if nda['signature_b']:
        return render_template('sign.html', nda=nda, party='b', already_signed=True,
                               locked=False)
    models.log_audit(nda['id'], 'Party B viewed signing page', _get_ip(), request.user_agent.string)
    if nda['status'] == 'draft':
        models.update_nda_status(nda['id'], 'sent')
    return render_template('sign.html', nda=nda, party='b', already_signed=False, locked=False)


@signing_bp.route('/nda/sign/a/<token>', methods=['POST'])
def submit_sign_a(token):
    nda = models.get_nda_by_token(token)
    if not nda or nda['sign_token_a'] != token:
        return jsonify({'error': 'Invalid token'}), 403
    if nda['status'] == 'signed' or nda['signature_a']:
        return jsonify({'error': 'Already signed'}), 400
    sig = request.form.get('signature', '').strip()
    if not sig:
        return jsonify({'error': 'Signature is required'}), 400
    models.save_signature(nda['id'], 'a', sig, _get_ip(), request.user_agent.string)
    models.log_audit(nda['id'], 'Party A signed', _get_ip(), request.user_agent.string)
    updated = models.get_nda(nda['public_id'])
    return jsonify({'ok': True, 'status': updated['status'], 'public_id': nda['public_id']})


@signing_bp.route('/nda/sign/b/<token>', methods=['POST'])
def submit_sign_b(token):
    nda = models.get_nda_by_token(token)
    if not nda or nda['sign_token_b'] != token:
        return jsonify({'error': 'Invalid token'}), 403
    if nda['status'] == 'signed' or nda['signature_b']:
        return jsonify({'error': 'Already signed'}), 400
    sig = request.form.get('signature', '').strip()
    if not sig:
        return jsonify({'error': 'Signature is required'}), 400
    models.save_signature(nda['id'], 'b', sig, _get_ip(), request.user_agent.string)
    models.log_audit(nda['id'], 'Party B signed', _get_ip(), request.user_agent.string)
    updated = models.get_nda(nda['public_id'])
    return jsonify({'ok': True, 'status': updated['status'], 'public_id': nda['public_id']})
