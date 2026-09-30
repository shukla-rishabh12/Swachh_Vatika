(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    const imageInput = document.getElementById('image');
    const previewBox = document.getElementById('image-preview');

    imageInput.addEventListener('change', () => {
      previewBox.innerHTML = '';
      const file = imageInput.files[0];
      if (!file) return;
      if (file.size > 5 * 1024 * 1024) {
        window.utils.toast('Image too large (max 5 MB).', 'error');
        imageInput.value = '';
        return;
      }
      const img = document.createElement('img');
      img.src = URL.createObjectURL(file);
      img.alt = 'preview';
      previewBox.appendChild(img);
    });

    const locBtn = document.getElementById('use-location-btn');
    const locStatus = document.getElementById('location-status');
    locBtn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        locStatus.textContent = 'Geolocation not supported by this browser.';
        return;
      }
      locStatus.textContent = 'Fetching your location...';
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          document.getElementById('latitude').value  = pos.coords.latitude.toFixed(6);
          document.getElementById('longitude').value = pos.coords.longitude.toFixed(6);
          locStatus.textContent = '✅ Location captured.';
        },
        () => {
          locStatus.textContent = '⚠️ Location permission denied. Enter address manually.';
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });

    const form = document.getElementById('report-form');
    const btn = document.getElementById('submit-btn');
    const errEl = document.getElementById('form-error');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errEl.style.display = 'none';

      const category = document.getElementById('category').value;
      const description = document.getElementById('description').value.trim();
      const latitude = document.getElementById('latitude').value;
      const longitude = document.getElementById('longitude').value;
      const address = document.getElementById('address').value.trim();
      const imageFile = imageInput.files[0];

      if (!category)   { showErr('Please select a category.'); return; }
      if (description.length < 5) { showErr('Description must be at least 5 characters.'); return; }
      if (!imageFile)  { showErr('Please upload a photo.'); return; }

      const fd = new FormData();
      fd.append('category', category);
      fd.append('description', description);
      if (latitude)  fd.append('latitude', latitude);
      if (longitude) fd.append('longitude', longitude);
      if (address)   fd.append('address', address);
      fd.append('image', imageFile);

      btn.disabled = true;
      btn.textContent = 'Submitting...';

      try {
        const res = await window.api.upload('/complaints', fd);
        window.utils.toast('Complaint submitted!', 'success');
        setTimeout(() => {
          window.location.href = `/citizen/complaint_detail.html?id=${res.data.complaint_id}`;
        }, 700);
      } catch (err) {
        showErr(err.message || 'Submission failed.');
        btn.disabled = false;
        btn.textContent = 'Submit Complaint';
      }
    });

    function showErr(msg) {
      errEl.textContent = msg;
      errEl.style.display = 'block';
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();