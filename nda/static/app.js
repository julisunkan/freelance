/* ── Notification system ───────────────────────────── */
function notify(message, type) {
  type = type || 'info';
  const colors = { success: '#22c55e', error: '#ef4444', info: '#4f46e5', warning: '#f59e0b' };
  const icons  = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };

  const bar = document.getElementById('notifications');
  if (!bar) return;

  const el = document.createElement('div');
  el.className = 'notif notif-' + type;
  el.innerHTML = `<span class="notif-icon">${icons[type] || 'ℹ'}</span><span class="notif-msg">${message}</span><button class="notif-close" onclick="this.parentElement.remove()">×</button>`;
  bar.prepend(el);

  setTimeout(() => { el.classList.add('notif-hide'); setTimeout(() => el.remove(), 400); }, 5000);
}

/* ── Signature pad ─────────────────────────────────── */
let signaturePad = null;

function initSignaturePad(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof SignaturePad === 'undefined') return;

  function resize() {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    const w = canvas.offsetWidth;
    canvas.width  = w * ratio;
    canvas.height = 180 * ratio;
    canvas.getContext('2d').scale(ratio, ratio);
    if (signaturePad) signaturePad.clear();
  }

  signaturePad = new SignaturePad(canvas, { backgroundColor: 'rgb(255,255,255)', penColor: '#1e1b4b' });
  window.addEventListener('resize', resize);
  resize();
}

function clearSignature() {
  if (signaturePad) signaturePad.clear();
}

/* ── Sign form submit ──────────────────────────────── */
function submitSignature(token, party) {
  if (!signaturePad || signaturePad.isEmpty()) {
    notify('Please draw your signature before submitting.', 'error');
    return;
  }
  const sigData = signaturePad.toDataURL('image/png');
  const btn = document.getElementById('signBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Submitting…'; }

  const fd = new FormData();
  fd.append('signature', sigData);

  fetch('/nda/sign/' + party + '/' + token, { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        notify(data.error, 'error');
        if (btn) { btn.disabled = false; btn.textContent = 'Submit Signature'; }
        return;
      }
      notify('Signature submitted successfully!', 'success');
      setTimeout(() => { window.location.href = '/nda/' + data.public_id; }, 1800);
    })
    .catch(() => {
      notify('Submission failed. Please try again.', 'error');
      if (btn) { btn.disabled = false; btn.textContent = 'Submit Signature'; }
    });
}

/* ── Copy to clipboard ─────────────────────────────── */
function copyLink(text, label) {
  navigator.clipboard.writeText(text).then(() => {
    notify((label || 'Link') + ' copied to clipboard!', 'success');
  }).catch(() => {
    notify('Could not copy. Please copy manually.', 'warning');
  });
}

/* ── Template preview ──────────────────────────────── */
function selectTemplate(id, name) {
  document.getElementById('template_id').value = id;
  document.querySelectorAll('.tpl-card').forEach(c => c.classList.remove('selected'));
  const card = document.getElementById('tpl-' + id);
  if (card) card.classList.add('selected');
  const label = document.getElementById('selected-tpl-label');
  if (label) label.textContent = name;
}

/* ── AI toggle ─────────────────────────────────────── */
function toggleAI(el) {
  const notice = document.getElementById('ai-notice');
  if (notice) notice.style.display = el.checked ? 'block' : 'none';
}

/* ── PWA install ───────────────────────────────────── */
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById('installBtn');
  if (btn) btn.style.display = 'inline-flex';
});

function installPWA() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(() => { deferredPrompt = null; });
  }
}

/* ── Service worker ────────────────────────────────── */
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/static/sw.js').catch(() => {});
}
