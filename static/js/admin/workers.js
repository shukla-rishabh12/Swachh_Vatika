/**
 * Admin — Workers list with activate/deactivate
 */
(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    await load();
  }

  async function load() {
    const c = document.getElementById('workers-list');
    if (!c) return;
    c.innerHTML = '<div class="loading">Loading workers...</div>';

    try {
      const res = await window.api.get('/workers?page=1&page_size=100');
      const items = res.data.items || [];
      if (items.length === 0) {
        c.innerHTML = '<div class="empty-state">No workers found.</div>';
        return;
      }

      c.innerHTML = `
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th><th>Name</th><th>Email</th><th>Status</th>
              <th>Total Tasks</th><th>Verified</th><th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${items.map(w => `
              <tr>
                <td>#${w.id}</td>
                <td>${window.utils.escapeHtml(w.full_name || '—')}</td>
                <td>${window.utils.escapeHtml(w.email)}</td>
                <td>${w.is_active
                  ? '<span class="badge-status status-ACTIVE">Active</span>'
                  : '<span class="badge-status status-REJECTED">Inactive</span>'}</td>
                <td>${(w.task_stats && w.task_stats.total) || 0}</td>
                <td>${(w.task_stats && w.task_stats.verified) || 0}</td>
                <td>
                  <a href="/admin/worker_detail.html?id=${w.id}" class="btn-secondary btn-sm">View</a>
                  <button class="btn-secondary btn-sm toggle-status"
                          data-uid="${w.id}"
                          data-active="${w.is_active ? 1 : 0}">
                    ${w.is_active ? '🚫 Deactivate' : '✓ Activate'}
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;

      // Wire toggle buttons
      c.querySelectorAll('.toggle-status').forEach(btn => {
        btn.addEventListener('click', async () => {
          const uid = btn.getAttribute('data-uid');
          const isCurrentlyActive = btn.getAttribute('data-active') === '1';
          const newStatus = !isCurrentlyActive;
          const label = newStatus ? 'activate' : 'deactivate';

          if (!confirm(`Are you sure you want to ${label} this worker?`)) return;

          btn.disabled = true;
          btn.textContent = '...';

          try {
            await window.api.patch(`/users/${uid}/status`, { is_active: newStatus });
            window.utils.toast(`Worker ${newStatus ? 'activated' : 'deactivated'}.`, 'success');
            await load();
          } catch (err) {
            window.utils.toast(err.message || 'Failed.', 'error');
            btn.disabled = false;
            btn.textContent = isCurrentlyActive ? '🚫 Deactivate' : '✓ Activate';
          }
        });
      });
    } catch (err) {
      c.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load.')}</div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();