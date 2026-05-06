/* ── Quill Editor initialization ─────────────────────── */
let quill;

document.addEventListener('DOMContentLoaded', function () {
  quill = new Quill('#quill-editor', {
    theme: 'snow',
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ color: [] }, { background: [] }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        [{ indent: '-1' }, { indent: '+1' }],
        ['link', 'blockquote', 'code-block'],
        ['clean']
      ]
    }
  });

  /* ── Sync hidden input on form submit ─────────────── */
  document.getElementById('proposalForm').addEventListener('submit', function () {
    document.getElementById('contentInput').value = quill.root.innerHTML;
  });

  /* ── Load template from URL param ─────────────────── */
  const params = new URLSearchParams(window.location.search);
  const tplIdParam = params.get('template');
  if (tplIdParam) {
    fetch('/api/templates/' + tplIdParam)
      .then(r => r.json())
      .then(t => {
        quill.clipboard.dangerouslyPasteHTML(t.content || '');
        showNotification('Template loaded: ' + t.name, 'success');
      });
  }

  /* ── Load template button ──────────────────────────── */
  document.getElementById('loadTemplateBtn').addEventListener('click', function () {
    const sel = document.getElementById('templateSelect');
    const tid = sel.value;
    if (!tid) {
      showNotification('Please select a template first.', 'warning');
      return;
    }

    const html = quill.root.innerHTML.trim();
    const hasContent = html !== '' && html !== '<p><br></p>';

    if (hasContent) {
      _showInlineConfirm(
        'tpl-replace-bar',
        document.getElementById('loadTemplateBtn'),
        '<i class="bi bi-exclamation-triangle-fill me-1 text-warning"></i>This will replace your current editor content.',
        'Replace Content',
        () => _doLoadTemplate(tid)
      );
      return;
    }
    _doLoadTemplate(tid);
  });

  /* ── AI: Generate ──────────────────────────────────── */
  document.getElementById('aiGenerateBtn').addEventListener('click', function () {
    const btn = this;
    const data = _collectFormData();
    if (!data.client_name || !data.project_title) {
      showNotification('Fill in Client Name and Project Title first.', 'warning');
      return;
    }
    _setAILoading(btn, true, 'Generating…');
    fetch('/api/ai/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
      .then(r => r.json())
      .then(res => {
        if (res.error) { showNotification(res.error, 'error'); return; }
        quill.clipboard.dangerouslyPasteHTML(res.content || '');
        showNotification('AI proposal generated successfully!', 'success');
      })
      .catch(() => showNotification('AI request failed. Check your connection.', 'error'))
      .finally(() => _setAILoading(btn, false, 'Generate Proposal'));
  });

  /* ── AI: Improve ───────────────────────────────────── */
  document.getElementById('aiImproveBtn').addEventListener('click', function () {
    const btn = this;
    const content = quill.root.innerHTML;
    if (!content || content.trim() === '<p><br></p>') {
      showNotification('Write something in the editor first.', 'warning');
      return;
    }
    _setAILoading(btn, true, 'Improving…');
    fetch('/api/ai/improve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    })
      .then(r => r.json())
      .then(res => {
        if (res.error) { showNotification(res.error, 'error'); return; }
        quill.clipboard.dangerouslyPasteHTML(res.content || '');
        showNotification('Proposal improved by AI!', 'success');
      })
      .catch(() => showNotification('AI request failed.', 'error'))
      .finally(() => _setAILoading(btn, false, 'Improve Writing'));
  });

  /* ── Score button (editor page) ────────────────────── */
  const scoreBtn = document.getElementById('scoreBtn');
  if (scoreBtn) {
    scoreBtn.addEventListener('click', function () {
      const pid = this.dataset.pid;
      document.getElementById('contentInput').value = quill.root.innerHTML;
      const modal = new bootstrap.Modal(document.getElementById('scoreModal'));
      document.getElementById('scoreModalBody').innerHTML =
        '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
      modal.show();
      fetch('/api/score/' + pid)
        .then(r => r.json())
        .then(data => renderScoreModal(data))
        .catch(() => {
          document.getElementById('scoreModalBody').innerHTML =
            '<p class="text-danger text-center">Failed to score proposal.</p>';
        });
    });
  }
});

/* ── Insert section by id ────────────────────────────── */
function insertSection(sid) {
  fetch('/api/sections')
    .then(r => r.json())
    .then(sections => {
      const s = sections.find(x => x.id === sid);
      if (!s) return;
      const range = quill.getSelection(true);
      quill.clipboard.dangerouslyPasteHTML(range.index, s.content);
      showNotification('Section "' + s.name + '" inserted.', 'success');
    });
}

/* ── Private helpers ─────────────────────────────────── */
function _doLoadTemplate(tid) {
  fetch('/api/templates/' + tid)
    .then(r => r.json())
    .then(t => {
      let html = t.content || '';
      html = _replacePlaceholders(html);
      quill.clipboard.dangerouslyPasteHTML(html);
      showNotification('Template loaded: ' + t.name, 'success');
    })
    .catch(() => showNotification('Failed to load template.', 'error'));
}

function _collectFormData() {
  return {
    client_name:   (document.querySelector('[name=client_name]')   || {}).value || (typeof proposalData !== 'undefined' ? proposalData.client_name : '') || '',
    project_title: (document.querySelector('[name=project_title]') || {}).value || (typeof proposalData !== 'undefined' ? proposalData.project_title : '') || '',
    description:   (document.querySelector('[name=description]')   || {}).value || (typeof proposalData !== 'undefined' ? proposalData.description : '') || '',
    price:         (document.querySelector('[name=price]')         || {}).value || (typeof proposalData !== 'undefined' ? proposalData.price : '') || '',
    timeline:      (document.querySelector('[name=timeline]')      || {}).value || (typeof proposalData !== 'undefined' ? proposalData.timeline : '') || '',
  };
}

function _replacePlaceholders(html) {
  const d = _collectFormData();
  return html
    .replace(/\{\{\s*client_name\s*\}\}/g,   d.client_name   || '{{ client_name }}')
    .replace(/\{\{\s*project_title\s*\}\}/g, d.project_title || '{{ project_title }}')
    .replace(/\{\{\s*price\s*\}\}/g,         d.price         || '{{ price }}');
}

function _setAILoading(btn, loading, label) {
  btn.disabled = loading;
  const icon = btn.id === 'aiGenerateBtn' ? 'magic' : 'arrow-up-circle';
  btn.innerHTML = loading
    ? `<span class="ai-loading"></span>${label}`
    : `<i class="bi bi-${icon} me-1"></i>${label}`;
}

/* ── Generic inline confirmation bar ────────────────────
   anchorId  — unique id for the bar element
   anchor    — DOM element to insert after
   message   — HTML string shown as the prompt
   confirmLabel — button text
   onConfirm — callback on confirm
*/
function _showInlineConfirm(anchorId, anchor, message, confirmLabel, onConfirm) {
  // Toggle off if already showing
  const existing = document.getElementById(anchorId);
  if (existing) { existing.remove(); return; }

  const bar = document.createElement('div');
  bar.id = anchorId;
  bar.className = 'inline-confirm-bar mt-2';
  bar.innerHTML = `
    <p class="small mb-2">${message}</p>
    <div class="d-flex gap-2">
      <button class="btn btn-sm btn-danger flex-grow-1 ic-yes">${confirmLabel}</button>
      <button class="btn btn-sm btn-outline-secondary flex-grow-1 ic-no">Cancel</button>
    </div>`;
  anchor.insertAdjacentElement('afterend', bar);

  bar.querySelector('.ic-yes').addEventListener('click', () => { bar.remove(); onConfirm(); });
  bar.querySelector('.ic-no').addEventListener('click', () => bar.remove());
}
