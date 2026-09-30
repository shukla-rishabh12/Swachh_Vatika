(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    await load();
  }

  async function load() {
    const container = document.getElementById('pickups-list');
    try {
      const res = await window.api.get('/pickups/my?page=1&page_size=20');
      const items = res.data.items || [];

      if (items.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <p>No pickup requests yet.</p>
            <a href="/citizen/pickup_request.html" class="btn-primary">Request a Pickup</a>
          </div>`;
        return;
      }

      container.innerHTML = items.map(p => `
        <div class="card pickup-item">
          <div class="pickup-header">
            <strong>#${p.id} — ${window.utils.escapeHtml(p.waste_type)}</strong>
            <span class="badge-status">${window.utils.escapeHtml(window.utils.statusLabel(p.status))}</span>
          </div>
          ${p.description ? `<p>${window.utils.escapeHtml(p.description)}</p>` : ''}
          <div class="complaint-meta">
            ${p.preferred_date ? `<span>Preferred: ${window.utils.formatDate(p.preferred_date)}</span>` : ''}
            <span>Requested: ${window.utils.formatDate(p.created_at)}</span>
          </div>
        </div>
      `).join('');
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load.')}</div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();