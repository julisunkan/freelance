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
  const tplId = params.get('template');
  if (tplId) {
    fetch('/api/templates/' + tplId)
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
    if (!tid) { showNotification('Please select a template first.', 'warning'); return; }
    if (quill.root.innerHTML.trim().length > 10) {
      if (!confirm('This will replace the current content. Continue?')) return;
    }
    fetch('/api/templates/' + tid)
      .then(r => r.json())
      .then(t => {
        let html = t.content || '';
        html = replacePlaceholders(html);
        quill.clipboard.dangerouslyPasteHTML(html);
        showNotification('Template loaded: ' + t.name, 'success');
      })
      .catch(() => showNotification('Failed to load template.', 'error'));
  });

  /* ── AI: Generate ──────────────────────────────────── */
  document.getElementById('aiGenerateBtn').addEventListener('click', function () {
    const btn = this;
    const data = collectFormData();
    if (!data.client_name || !data.project_title) {
      showNotification('Fill in Client Name and Project Title first.', 'warning');
      return;
    }
    setAILoading(btn, true, 'Generating…');
    fetch('/api/ai/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
      .then(r => r.json())
      .then(res => {
        if (res.error) { showNotification(res.error, 'error'); return; }
        quill.clipboard.dangerouslyPasteHTML(res.content || '');
        showNotification('AI proposal generated!', 'success');
      })
      .catch(() => showNotification('AI request failed. Check your connection.', 'error'))
      .finally(() => setAILoading(btn, false, 'Generate Proposal'));
  });

  /* ── AI: Improve ───────────────────────────────────── */
  document.getElementById('aiImproveBtn').addEventListener('click', function () {
    const btn = this;
    const content = quill.root.innerHTML;
    if (!content || content.trim() === '<p><br></p>') {
      showNotification('Write something in the editor first.', 'warning');
      return;
    }
    setAILoading(btn, true, 'Improving…');
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
      .finally(() => setAILoading(btn, false, 'Improve Writing'));
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

/* ── Helpers ─────────────────────────────────────────── */
function collectFormData() {
  return {
    client_name:   (document.querySelector('[name=client_name]')   || {}).value || (proposalData || {}).client_name || '',
    project_title: (document.querySelector('[name=project_title]') || {}).value || (proposalData || {}).project_title || '',
    description:   (document.querySelector('[name=description]')   || {}).value || (proposalData || {}).description || '',
    price:         (document.querySelector('[name=price]')         || {}).value || (proposalData || {}).price || '',
    timeline:      (document.querySelector('[name=timeline]')      || {}).value || (proposalData || {}).timeline || '',
  };
}

function replacePlaceholders(html) {
  const data = collectFormData();
  return html
    .replace(/\{\{\s*client_name\s*\}\}/g,   data.client_name   || '{{ client_name }}')
    .replace(/\{\{\s*project_title\s*\}\}/g, data.project_title || '{{ project_title }}')
    .replace(/\{\{\s*price\s*\}\}/g,         data.price         || '{{ price }}');
}

function setAILoading(btn, loading, label) {
  btn.disabled = loading;
  btn.innerHTML = loading
    ? `<span class="ai-loading"></span> ${label}`
    : `<i class="bi bi-${btn.id === 'aiGenerateBtn' ? 'magic' : 'arrow-up-circle'} me-1"></i> ${label}`;
}
