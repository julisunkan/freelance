// File preview
function setupPreview(inputId, previewId) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  if (!input || !preview) return;
  input.addEventListener('change', function () {
    preview.innerHTML = '';
    if (this.files && this.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        preview.appendChild(img);
      };
      reader.readAsDataURL(this.files[0]);
    }
  });
}

setupPreview('front_id', 'frontPreview');
setupPreview('back_id', 'backPreview');
setupPreview('selfie', 'selfiePreview');

// Loading state on submit
const form = document.getElementById('uploadForm');
if (form) {
  form.addEventListener('submit', function () {
    const btn = document.getElementById('submitBtn');
    if (btn) {
      btn.querySelector('.btn-text').style.display = 'none';
      btn.querySelector('.btn-loading').style.display = 'inline';
      btn.disabled = true;
    }
  });
}

// PWA service worker
if ('serviceWorker' in navigator) {
  const base = document.querySelector('link[rel="manifest"]')?.href
    ?.replace('/static/manifest.json', '') || '';
  navigator.serviceWorker.register(base + '/static/sw.js', { scope: base + '/' })
    .catch(function () {});
}
