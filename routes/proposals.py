from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
import models

proposals_bp = Blueprint('proposals', __name__)


@proposals_bp.route('/')
def dashboard():
    status = request.args.get('status', '')
    proposals = models.get_all_proposals(status if status else None)
    stats = models.get_stats()
    return render_template('dashboard.html', proposals=proposals, stats=stats, current_status=status)


@proposals_bp.route('/proposals/new', methods=['GET', 'POST'])
def new_proposal():
    if request.method == 'POST':
        data = {
            'client_name': request.form.get('client_name', '').strip(),
            'project_title': request.form.get('project_title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'price': request.form.get('price') or None,
            'timeline': request.form.get('timeline', '').strip(),
            'status': request.form.get('status', 'Draft'),
            'content': request.form.get('content', ''),
        }
        if not data['client_name'] or not data['project_title']:
            flash('Client name and project title are required.', 'error')
            return render_template('editor.html', proposal=data,
                                   templates=models.get_all_templates(),
                                   sections=models.get_all_sections())
        pid = models.create_proposal(data)
        flash('Proposal created successfully!', 'success')
        return redirect(url_for('proposals.view_proposal', pid=pid))

    return render_template('editor.html', proposal=None,
                           templates=models.get_all_templates(),
                           sections=models.get_all_sections())


@proposals_bp.route('/proposals/<int:pid>/edit', methods=['GET', 'POST'])
def edit_proposal(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        abort(404)

    if request.method == 'POST':
        data = {
            'client_name': request.form.get('client_name', '').strip(),
            'project_title': request.form.get('project_title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'price': request.form.get('price') or None,
            'timeline': request.form.get('timeline', '').strip(),
            'status': request.form.get('status', 'Draft'),
            'content': request.form.get('content', ''),
        }
        if not data['client_name'] or not data['project_title']:
            flash('Client name and project title are required.', 'error')
            return render_template('editor.html', proposal=proposal,
                                   templates=models.get_all_templates(),
                                   sections=models.get_all_sections())
        models.update_proposal(pid, data)
        flash('Proposal updated successfully!', 'success')
        return redirect(url_for('proposals.view_proposal', pid=pid))

    return render_template('editor.html', proposal=proposal,
                           templates=models.get_all_templates(),
                           sections=models.get_all_sections())


@proposals_bp.route('/proposals/<int:pid>')
def view_proposal(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        abort(404)
    export_history = models.get_export_history(pid)
    return render_template('proposal_view.html', proposal=proposal, export_history=export_history)


@proposals_bp.route('/proposals/<int:pid>/delete', methods=['POST'])
def delete_proposal(pid):
    models.delete_proposal(pid)
    flash('Proposal deleted.', 'success')
    return redirect(url_for('proposals.dashboard'))


@proposals_bp.route('/proposals/<int:pid>/report', methods=['POST'])
def report_proposal(pid):
    proposal = models.get_proposal(pid)
    if not proposal:
        abort(404)
    reason = request.form.get('reason', '').strip()
    models.create_report(pid, reason)
    flash('Report submitted. Thank you for your feedback.', 'success')
    return redirect(url_for('proposals.view_proposal', pid=pid))


@proposals_bp.route('/share/<token>')
def public_view(token):
    proposal = models.get_proposal_by_token(token)
    if not proposal:
        abort(404)
    models.increment_views(proposal['id'])
    return render_template('public_view.html', proposal=proposal)


@proposals_bp.route('/sections')
def sections_page():
    sections = models.get_all_sections()
    return render_template('sections.html', sections=sections)


@proposals_bp.route('/templates')
def templates_page():
    templates = models.get_all_templates()
    return render_template('template_selector.html', templates=templates)
