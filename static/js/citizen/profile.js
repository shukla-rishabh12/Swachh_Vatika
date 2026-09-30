(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('email').value = user.email || '';

    // Load profile
    try {
      const res = await window.api.get('/users/me');
      const p = res.data.profile || {};
      document.getElementById('full_name').value = p.full_name || '';
      document.getElementById('phone').value     = p.phone || '';
      document.getElementById('address').value   = p.address || '';
      document.getElementById('city').value      = p.city || '';
    } catch (e) { /* ignore */ }

    // Save
    const form = document.getElementById('profile-form');
    const btn  = document.getElementById('save-btn');
    const errEl = document.getElementById('form-error');
    const okEl  = document.getElementById('form-success');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errEl.style.display = 'none';
      okEl.style.display = 'none';

      const payload = {
        full_name: document.getElementById('full_name').value.trim(),
        phone:     document.getElementById('phone').value.trim(),
        address:   document.getElementById('address').value.trim(),
        city:      document.getElementById('city').value.trim(),
      };

      if (!payload.full_name) {
        errEl.textContent = 'Full name is required.';
        errEl.style.display = 'block';
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Saving...';

      try {
        await window.api.patch('/users/me', payload);
        okEl.textContent = 'Profile updated successfully.';
        okEl.style.display = 'block';
        window.utils.toast('Profile updated.', 'success');
      } catch (err) {
        errEl.textContent = err.message || 'Save failed.';
        errEl.style.display = 'block';
      } finally {
        btn.disabled = false;
        btn.textContent = 'Save Changes';
      }
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();