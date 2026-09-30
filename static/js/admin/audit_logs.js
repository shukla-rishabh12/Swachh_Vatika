(function () {
  let currentPage = 1;
  const pageSize = 25;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('filter-entity').addEventListener('change', () => {
      currentPage = 1; load();
    });

    await load();
  }

  async function load() {
    const container = document.getElementById('logs-list');
    container.innerHTML = '<div class="loading">Loading...</div>';

    const entity = document.getElementById('filter-entity').value;
    const params = new URLSearchParams({ page: currentPage, page_size: pageSize });
    if (entity) params.append('entity_type', entity);

    try {
      const res = await window.api.get(`/audit?${params.toString()}`);
      render(res.data.items);
      renderPagination(res.data.pagination);
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed.')}</div>`;
    }
  }

  function render(items) {
    const container = document.getElementById('logs-list');
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="empty-state">No audit logs.</div>';
      return;
    }
    container.innerHTML = `
      <table class="data-table">
        <thead>
          <tr><th>Time</th><th>Actor</th><th>Action</th><th>Entity</th><th>Entity ID</th><th>IP</th></tr>
        </thead>
        <tbody>
          ${items.map(l => `
            <tr>
              <td>${window.utils.formatDateTime(l.created_at)}</td>
              <td>${window.utils.escapeHtml(l.actor_name || l.actor_email || 'system')}</td>
              <td>${window.utils.escapeHtml(l.action)}</td>
              <td>${window.utils.escapeHtml(l.entity_type || '—')}</td>
              <td>${l.entity_id || '—'}</td>
              <td>${window.utils.escapeHtml(l.ip_address || '—')}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }

  function renderPagination(p) {
    const el = document.getElementById('pagination');
    if (!p || p.total_pages <= 1) { el.innerHTML = ''; return; }
    el.innerHTML = `
      <button ${p.page <= 1 ? 'disabled' : ''} id="prev-btn">Prev</button>
      <span>Page ${p.page} of ${p.total_pages}</span>
      <button ${p.page >= p.total_pages ? 'disabled' : ''} id="next-btn">Next</button>
    `;
    document.getElementById('prev-btn')?.addEventListener('click', () => { currentPage--; load(); });
    document.getElementById('next-btn')?.addEventListener('click', () => { currentPage++; load(); });
  }

  document.addEventListener('DOMContentLoaded', init);
})();