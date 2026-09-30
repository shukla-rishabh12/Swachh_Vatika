(function () {
  let currentPage = 1;
  const pageSize = 15;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('filter-status').addEventListener('change', () => {
      currentPage = 1; load();
    });

    await load();
  }

  async function load() {
    const container = document.getElementById('tasks-list');
    container.innerHTML = '<div class="loading">Loading...</div>';

    const status = document.getElementById('filter-status').value;
    const params = new URLSearchParams({ page: currentPage, page_size: pageSize });
    if (status) params.append('status', status);

    try {
      const res = await window.api.get(`/admin/tasks?${params.toString()}`);
      render(res.data.items);
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load.')}</div>`;
    }
  }

  function render(items) {
    const container = document.getElementById('tasks-list');
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="empty-state">No tasks found.</div>';
      return;
    }
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr><th>Task ID</th><th>Worker</th><th>Category</th><th>Address</th><th>Status</th><th>Assigned</th><th>Action</th></tr>
        </thead>
        <tbody>
          ${items.map(t => `
            <tr>
              <td>#${t.id}</td>
              <td>${window.utils.escapeHtml(t.worker_name || '—')}</td>
              <td>${window.utils.escapeHtml(window.utils.categoryLabel(t.complaint_category) || '—')}</td>
              <td>${window.utils.escapeHtml((t.complaint_address || '—').slice(0, 40))}</td>
              <td><span class="badge-status status-${t.status}">${window.utils.statusLabel(t.status)}</span></td>
              <td>${window.utils.formatDate(t.assigned_at)}</td>
              <td><a href="/admin/tasks.html?task=${t.id}" class="btn-secondary btn-sm" onclick="event.preventDefault(); window.location.href='/admin/verification.html?task=${t.id}'">View</a></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }

  document.addEventListener('DOMContentLoaded', init);
})();