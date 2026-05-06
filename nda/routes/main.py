from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import models
from services.ai_service import enhance_nda

main_bp = Blueprint('main', __name__)


def _get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '')


@main_bp.route('/')
def index():
    templates = models.get_all_templates()
    settings = models.get_all_settings()
    ai_enabled = settings.get('ai_enabled', 'false').lower() == 'true'
    groq_key = settings.get('groq_api_key', '')
    return render_template('index.html', templates=templates,
                           ai_available=bool(groq_key and ai_enabled))


@main_bp.route('/create', methods=['POST'])
def create_nda():
    f = request.form
    clauses = f.getlist('clauses')

    template_id = int(f.get('template_id', 1))
    data = {
        'party_a':       f.get('party_a', '').strip(),
        'party_b':       f.get('party_b', '').strip(),
        'party_a_email': f.get('party_a_email', '').strip(),
        'party_b_email': f.get('party_b_email', '').strip(),
        'purpose':       f.get('purpose', '').strip(),
        'jurisdiction':  f.get('jurisdiction', 'California, USA').strip(),
        'template_id':   template_id,
        'duration':      f.get('duration', '2 years'),
        'mutual':        bool(f.get('mutual')),
        'clauses':       clauses,
    }

    if not data['party_a'] or not data['party_b'] or not data['purpose']:
        templates = models.get_all_templates()
        return render_template('index.html', templates=templates,
                               error='Party A, Party B, and Purpose are required.',
                               form_data=data)

    base_html = models.generate_nda_html(template_id, data)

    settings = models.get_all_settings()
    groq_key = settings.get('groq_api_key', '')
    ai_enabled = settings.get('ai_enabled', 'false').lower() == 'true'
    ai_enhance = bool(f.get('ai_enhance')) and bool(groq_key) and ai_enabled

    nda_html = base_html
    if ai_enhance:
        tmpl = models.get_template(template_id)
        enhanced = enhance_nda(base_html, data, tmpl, groq_key,
                               settings.get('groq_model', 'llama-3.3-70b-versatile'),
                               settings.get('default_tone', 'formal'))
        if enhanced:
            nda_html = enhanced

    data['nda_html'] = nda_html
    data['clauses'] = ','.join(clauses)

    public_id, nda_id, token_a, token_b = models.create_nda(data)
    models.log_audit(nda_id, 'NDA created', _get_ip(), request.user_agent.string)

    return redirect(url_for('main.view_nda', public_id=public_id))


# Route is /view/<id> — the /nda prefix is added by DispatcherMiddleware
@main_bp.route('/view/<public_id>')
def view_nda(public_id):
    nda = models.get_nda(public_id)
    if not nda:
        return render_template('error.html', code=404, message='NDA not found.'), 404

    models.log_audit(nda['id'], 'NDA viewed', _get_ip(), request.user_agent.string)

    # url_for respects SCRIPT_NAME set by DispatcherMiddleware → /nda/sign/a/...
    sign_url_a = request.host_url.rstrip('/') + url_for(
        'signing.sign_a', token=nda['sign_token_a'])
    sign_url_b = request.host_url.rstrip('/') + url_for(
        'signing.sign_b', token=nda['sign_token_b'])

    return render_template('view_nda.html', nda=nda,
                           sign_url_a=sign_url_a, sign_url_b=sign_url_b)
