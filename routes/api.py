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
    data = request.get_json(force=True)
    api_key = models.get_setting('groq_api_key', '')
    if not api_key:
        return jsonify({'error': 'Groq API key not configured. Visit /julisunkan?token=julisunkan to set it.'}), 400
    result = generate_proposal_content(data, api_key)
    return jsonify(result)


@api_bp.route('/api/ai/improve', methods=['POST'])
def api_ai_improve():
    data = request.get_json(force=True)
    api_key = models.get_setting('groq_api_key', '')
    if not api_key:
        return jsonify({'error': 'Groq API key not configured. Visit /julisunkan?token=julisunkan to set it.'}), 400
    result = improve_proposal_content(data.get('content', ''), api_key)
    return jsonify(result)


@api_bp.route('/api/templates/<int:tid>')
def api_get_template(tid):
    t = models.get_template(tid)
    if not t:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(t))


@api_bp.route('/api/templates/<int:tid>', methods=['PUT'])
def api_update_template(tid):
    data = request.get_json(force=True)
    models.update_template(tid, {
        'name': data.get('name', ''),
        'content': data.get('content', ''),
        'category': data.get('category', '')
    })
    return jsonify({'ok': True})


@api_bp.route('/api/sections', methods=['GET'])
def api_sections():
    return jsonify(models.get_all_sections())


@api_bp.route('/api/sections', methods=['POST'])
def api_create_section():
    data = request.get_json(force=True)
    name = (data.get('name') or '').strip()
    content = (data.get('content') or '').strip()
    if not name or not content:
        return jsonify({'error': 'Name and content are required'}), 400
    sid = models.create_section({'name': name, 'content': content})
    return jsonify({'id': sid, 'name': name, 'content': content}), 201


@api_bp.route('/api/sections/<int:sid>', methods=['PUT'])
def api_update_section(sid):
    data = request.get_json(force=True)
    models.update_section(sid, {
        'name': data.get('name', ''),
        'content': data.get('content', '')
    })
    return jsonify({'ok': True})


@api_bp.route('/api/sections/<int:sid>', methods=['DELETE'])
def api_delete_section(sid):
    models.delete_section(sid)
    return jsonify({'ok': True})
