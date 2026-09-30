(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('use-location-btn').addEventListener('click', () => {
      const status = document.getElementById('location-status');
      if (!navigator.geolocation) { status.textContent = 'Geolocation not supported.'; return; }
      status.textContent = 'Fetching...';
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          document.getElementById('latitude').value  = pos.coords.latitude.toFixed(6);
          document.getElementById('longitude').value = pos.coords.longitude.toFixed(6);
          status.textContent = '✅ Location captured.';
        },
        () => { status.textContent = '⚠️ Permission denied. Enter address manually.'; }
      );
    });

    const form = document.getElementById('pickup-form');
    const btn = document.getElementById('submit-btn');
    const errEl = document.getElementById('form-error');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errEl.style.display = 'none';

      const waste_type = document.getElementById('waste_type').value;
      if (!waste_type) { showErr('Please select a waste type.'); return; }

      const payload = {
        waste_type,
        description:    document.getElementById('description').value.trim(),
        latitude:       document.getElementById('latitude').value || null,
        longitude:      document.getElementById('longitude').value || null,
        address:        document.getElementById('address').value.trim(),
        preferred_date: document.getElementById('preferred_date').value || null,
      };

      btn.disabled = true;
      btn.textContent = 'Submitting...';

      try {
        await window.api.post('/pickups', payload);
        window.utils.toast('Pickup request submitted!', 'success');
        setTimeout(() => window.location.href = '/citizen/pickups.html', 700);
      } catch (err) {
        showErr(err.message || 'Submission failed.');
        btn.disabled = false;
        btn.textContent = 'Request Pickup';
      }
    });

    function showErr(m) { errEl.textContent = m; errEl.style.display = 'block'; }
  }

  document.addEventListener('DOMContentLoaded', init);
})();