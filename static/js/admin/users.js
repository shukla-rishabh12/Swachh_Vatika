(function () {
  let currentPage = 1;
  const pageSize = 20;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('filter-role').addEventListener('change', () => { currentPage = 1; load(); });
    document.getElementById('filter-search').addEventListener('input',
      window.utils.debounce(() => { currentPage = 1; load(); }, 400)
    );

    await load();
  }

  async function load() {
    const container = document.getElementById('users-list');
    container.innerHTML = '<div class="loading">Loading...</div>';

    const role = document.getElementById('filter-role').value;
    const search = document.getElementById('filter-search').value.trim();

    const params = new URLSearchParams({ page: currentPage, page_size: pageSize });
    if (role) params.append('role', role);
    if (search) params.append('search', search);

    try {
      const res = await window.api.get(`/users?${params.toString()}`);
      render(res.data.items);
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load.')}</div>`;
    }
  }

  function render(items) {
    const container = document.getElementById('users-list');
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="empty-state">No users found.</div>';
      return;
    }
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Action</th></tr>
        </thead>
        <tbody>
          ${items.map(u => `
            <tr>
              <td>#${u.id}</td>
              <td>${window.utils.escapeHtml(u.full_name || '—')}</td>
              <td>${window.utils.escapeHtml(u.email)}</td>
              <td>${window.utils.escapeHtml(u.role)}</td>
              <td>${u.is_active ? '<span class="badge-status status-ACTIVE">Active</span>' : '<span class="badge-status status-REJECTED">Inactive</span>'}</td>
              <td>
                <button class="btn-secondary btn-sm" data-uid="${u.id}" data-active="${u.is_active ? 1 : 0}">
                  ${u.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;

    container.querySelectorAll('button[data-uid]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const uid = btn.getAttribute('data-uid');
        const currentlyActive = btn.getAttribute('data-active') === '1';
        const newStatus = !currentlyActive;
        if (!confirm(`${newStatus ? 'Activate' : 'Deactivate'} this user?`)) return;
        try {
          await window.api.patch(`/users/${uid}/status`, { is_active: newStatus });
          window.utils.toast('User status updated.', 'success');
          await load();
        } catch (err) {
          window.utils.toast(err.message || 'Failed.', 'error');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();