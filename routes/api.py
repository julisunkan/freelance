from flask import Blueprint, request, jsonify
import models
from services.ai_service import generate_proposal_content, improve_proposal_content
from services.scoring_service import score_proposal

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/score/<int:pid>')
def api_score(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        return jsonify({'error': 'Not found'}), 404
    result = score_proposal(proposal)
    return jsonify(result)


@api_bp.route('/api/ai/generate', methods=['POST'])
def api_ai_generate():
    data = request.get_json(force=True) or {}
    api_key = models.get_setting('groq_api_key', '')
    if not api_key:
        return jsonify({'error': 'Groq API key not configured. Visit /julisunkan?token=julisunkan to set it.'}), 400
    result = generate_proposal_content(data, api_key)
    return jsonify(result)


@api_bp.route('/api/ai/improve', methods=['POST'])
def api_ai_improve():
    data = request.get_json(force=True) or {}
    api_key = models.get_setting('groq_api_key', '')
    if not api_key:
        return jsonify({'error': 'Groq API key not configured. Visit /julisunkan?token=julisunkan to set it.'}), 400
    result = improve_proposal_content(data.get('content', ''), api_key)
    return jsonify(result)


@api_bp.route('/api/sections', methods=['GET'])
def api_get_sections():
    return jsonify(models.get_all_sections())


@api_bp.route('/api/sections', methods=['POST'])
def api_create_section():
    data = request.get_json(force=True) or {}
    name = data.get('name', '').strip()
    content = data.get('content', '').strip()
    if not name or not content:
        return jsonify({'error': 'name and content are required'}), 400
    sid = models.create_section({'name': name, 'content': content})
    return jsonify({'id': sid, 'ok': True}), 201


@api_bp.route('/api/sections/<int:sid>', methods=['GET'])
def api_get_section(sid):
    s = models.get_section(sid)
    if not s:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(s)


@api_bp.route('/api/sections/<int:sid>', methods=['PUT'])
def api_update_section(sid):
    existing = models.get_section(sid)
    if not existing:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json(force=True) or {}
    models.update_section(sid, {
        'name':    data.get('name', existing['name']),
        'content': data.get('content', existing['content']),
    })
    return jsonify({'ok': True})


@api_bp.route('/api/sections/<int:sid>', methods=['DELETE'])
def api_delete_section(sid):
    if not models.get_section(sid):
        return jsonify({'error': 'Not found'}), 404
    models.delete_section(sid)
    return jsonify({'ok': True})


@api_bp.route('/api/templates/<int:tid>')
def api_get_template(tid):
    t = models.get_template(tid)
    if not t:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(t))


@api_bp.route('/api/templates/<int:tid>', methods=['PUT'])
def api_update_template(tid):
    existing = models.get_template(tid)
    if not existing:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json(force=True)
    models.update_template(tid, {
        'name':     data.get('name')     or existing['name'],
        'content':  data.get('content')  if data.get('content') is not None else existing['content'],
        'category': data.get('category') or existing.get('category', '')
    })
    return jsonify({'ok': True})


