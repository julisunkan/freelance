/* ── Notification System ─────────────────────────────── */
function showNotification(message, type) {
  type = type || 'info';
  const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '⚠' };
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-notif ${type}`;
  toast.innerHTML = `
    <span style="font-size:1rem;flex-shrink:0">${icons[type] || 'ℹ'}</span>
    <span style="flex:1">${message}</span>
    <button class="toast-close" onclick="this.parentElement.remove()">×</button>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(16px)';
    toast.style.transition = 'all .3s ease';
    setTimeout(() => toast.remove(), 320);
  }, 4500);
}

/* ── Score handler ──────────────────────────────────── */
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
