/* ── Inline Notification System ──────────────────────── */
function showNotification(message, type) {
  type = type || 'info';
  const bsType  = { success: 'success', error: 'danger', info: 'info', warning: 'warning' }[type] || 'info';
  const iconMap  = { success: 'check-circle-fill', error: 'x-circle-fill', info: 'info-circle-fill', warning: 'exclamation-triangle-fill' };

  const container = document.getElementById('inline-messages');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `alert alert-${bsType} alert-dismissible d-flex align-items-center gap-2 mb-2 fade show`;
  el.role = 'alert';
  el.innerHTML = `
    <i class="bi bi-${iconMap[type] || 'info-circle-fill'} flex-shrink-0"></i>
    <span class="flex-grow-1">${message}</span>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
  container.prepend(el);

  // Auto-dismiss after 4.5 s
  setTimeout(() => {
    const inst = bootstrap.Alert.getOrCreateInstance(el);
    if (inst) inst.close(); else el.remove();
  }, 4500);
}

/* ── Score handler (proposal_view page) ──────────────── */
document.addEventListener('DOMContentLoaded', function () {
  const scoreBtn = document.getElementById('scoreBtn');
  if (scoreBtn) {
    scoreBtn.addEventListener('click', function () {
      const pid = this.dataset.pid;
      if (!pid) return;
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

function renderScoreModal(data) {
  const color = data.score >= 80 ? '#22c55e'
              : data.score >= 60 ? '#f59e0b'
              : data.score >= 40 ? '#f97316' : '#ef4444';
  const fb = (data.feedback || []).map(f => `<li class="mb-1 small">${f}</li>`).join('');
  const bd = Object.entries(data.breakdown || {}).map(([k, v]) => `
    <div class="mb-2">
      <div class="d-flex justify-content-between small mb-1">
        <span class="text-capitalize fw-semibold">${k}</span><span>${v}/25</span>
      </div>
      <div class="progress" style="height:6px">
        <div class="progress-bar" style="width:${(v / 25) * 100}%;background:${color}"></div>
      </div>
    </div>`).join('');
  document.getElementById('scoreModalBody').innerHTML = `
    <div class="text-center mb-4">
      <div class="score-circle" style="--score-color:${color}">
        <span class="score-num">${data.score}</span>
        <span class="score-denom">/100</span>
      </div>
      <div class="fw-bold mt-2 fs-5">${data.grade}</div>
      <p class="text-muted small mb-0">${data.summary}</p>
    </div>
    <div class="score-breakdown mb-3">${bd}</div>
    ${fb ? `<ul class="list-unstyled border-top pt-3 mb-0">${fb}</ul>` : ''}`;
}
