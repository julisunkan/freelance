/* ── Notification system ─────────────────────────────── */
function notify(message, type) {
  type = type || 'info';
  const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
  const bar = document.getElementById('notifications');
  if (!bar) return;
  const el = document.createElement('div');
  el.className = 'notif notif-' + type;
  el.innerHTML = `<span class="notif-icon">${icons[type] || 'ℹ'}</span><span class="notif-msg">${message}</span><button class="notif-close" onclick="this.parentElement.remove()">×</button>`;
  bar.prepend(el);
  setTimeout(() => { el.classList.add('notif-hide'); setTimeout(() => el.remove(), 400); }, 5000);
}

/* ── Template dropdown ───────────────────────────────── */
function toggleTplDropdown() {
  const btn = document.getElementById('tplSelectBtn');
  const dropdown = document.getElementById('tplDropdown');
  const search = document.getElementById('tplSearch');
  if (!btn || !dropdown) return;
  const isOpen = dropdown.classList.contains('open');
  if (isOpen) {
    closeTplDropdown();
  } else {
    dropdown.classList.add('open');
    btn.classList.add('open');
    if (search) { search.value = ''; filterTemplates(''); search.focus(); }
  }
}

function closeTplDropdown() {
  const btn = document.getElementById('tplSelectBtn');
  const dropdown = document.getElementById('tplDropdown');
  if (btn) btn.classList.remove('open');
  if (dropdown) dropdown.classList.remove('open');
}

function selectTemplate(id, name, cat, color) {
  document.getElementById('template_id').value = id;
  document.getElementById('tplSelectName').textContent = name;
  document.getElementById('tplSelectCat').textContent = cat || '';
  document.getElementById('tplDot').style.background = color || '#4f46e5';
  document.querySelectorAll('.tpl-option').forEach(o => o.classList.remove('selected'));
  const opt = document.getElementById('tpl-opt-' + id);
  if (opt) opt.classList.add('selected');
  closeTplDropdown();
}

function filterTemplates(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.tpl-option').forEach(opt => {
    const name = (opt.dataset.name || '').toLowerCase();
    const cat  = (opt.dataset.cat  || '').toLowerCase();
    opt.style.display = (!q || name.includes(q) || cat.includes(q)) ? '' : 'none';
  });
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  const wrap = document.getElementById('tplDropdownWrap');
  if (wrap && !wrap.contains(e.target)) closeTplDropdown();
});

/* ── AI toggle ───────────────────────────────────────── */
function toggleAI(el) {
  const notice = document.getElementById('ai-notice');
  const toneRow = document.getElementById('ai-tone-row');
  if (notice)  notice.style.display  = el.checked ? 'block' : 'none';
  if (toneRow) toneRow.style.display = el.checked ? 'block' : 'none';
}

/* ── Signature pad ───────────────────────────────────── */
let signaturePad = null;

function initSignaturePad(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof SignaturePad === 'undefined') return;

  function resize() {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width  = canvas.offsetWidth * ratio;
    canvas.height = 180 * ratio;
    canvas.getContext('2d').scale(ratio, ratio);
    if (signaturePad) signaturePad.clear();
  }

  signaturePad = new SignaturePad(canvas, {
    backgroundColor: 'rgb(255,255,255)',
    penColor: '#1e1b4b'
  });
  window.addEventListener('resize', resize);
  resize();
}

function clearSignature() {
  if (signaturePad) signaturePad.clear();
}

/* ── Sign form submit ────────────────────────────────── */
function submitSignature() {
  if (!signaturePad || signaturePad.isEmpty()) {
    notify('Please draw your signature before submitting.', 'error');
    return;
  }
  if (typeof SIGN_ACTION === 'undefined') {
    notify('Signing configuration error. Please reload the page.', 'error');
    return;
  }
  const sigData = signaturePad.toDataURL('image/png');
  const btn = document.getElementById('signBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Submitting…'; }

  const fd = new FormData();
  fd.append('signature', sigData);

  fetch(SIGN_ACTION, { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        notify(data.error, 'error');
        if (btn) { btn.disabled = false; btn.textContent = '✓ Submit Signature'; }
        return;
      }
      notify('Signature submitted successfully!', 'success');
      setTimeout(() => {
        window.location.href = data.view_url || ('/nda/view/' + data.public_id);
      }, 1800);
    })
    .catch(() => {
      notify('Submission failed. Please try again.', 'error');
      if (btn) { btn.disabled = false; btn.textContent = '✓ Submit Signature'; }
    });
}

/* ── Copy to clipboard ───────────────────────────────── */
function copyLink(text, label) {
  navigator.clipboard.writeText(text).then(() => {
    notify((label || 'Link') + ' copied to clipboard!', 'success');
  }).catch(() => {
    notify('Could not copy. Please copy manually.', 'warning');
  });
}
