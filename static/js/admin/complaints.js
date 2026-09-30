(function () {
  let currentPage = 1;
  const pageSize = 15;

  console.log('[admin/complaints] loaded');

  async function init() {
    try {
      if (!window.api || !window.auth || !window.utils) {
        throw new Error('Core JS missing');
      }

      const user = await window.auth.load();
      if (!user) { window.location.href = '/auth/login.html'; return; }
      if (user.role !== 'ADMIN') { window.location.href = '/403.html'; return; }

      try { window.navigation.build('ADMIN'); } catch (e) {}
      try { window.notif.updateBadge(); } catch (e) {}

      const em = document.getElementById('user-email');
      if (em) em.textContent = user.email || '';

      ['filter-status', 'filter-category', 'filter-priority'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', () => { currentPage = 1; load(); });
      });

      await load();
    } catch (err) {
      console.error('[admin/complaints] init FAILED:', err);
      const c = document.getElementById('complaints-list');
      if (c) c.innerHTML = `<div class="error-state">Script error: ${err.message || err}</div>`;
    }
  }

  async function load() {
    const c = document.getElementById('complaints-list');
    if (!c) { console.error('complaints-list not found'); return; }
    c.innerHTML = '<div class="loading">Loading complaints...</div>';

    const status   = (document.getElementById('filter-status')   || {}).value || '';
    const category = (document.getElementById('filter-category') || {}).value || '';
    const priority = (document.getElementById('filter-priority') || {}).value || '';

    const params = new URLSearchParams({ page: currentPage, page_size: pageSize });
    if (status)   params.append('status', status);
    if (category) params.append('category', category);
    if (priority) params.append('priority', priority);

    const url = '/admin/complaints?' + params.toString();
    console.log('[admin/complaints] fetch:', url);

    try {
      const res = await window.api.get(url);
      console.log('[admin/complaints] res:', res);

      if (!res || !res.data) throw new Error('Empty response');
      render(res.data.items || []);
      renderPagination(res.data.pagination);
    } catch (err) {
      console.error('[admin/complaints] load FAILED:', err);
      const msg = (err && err.message) || 'Failed to load';
      c.innerHTML = `
        <div class="error-state">
          <p><strong>Error:</strong> ${window.utils.escapeHtml(msg)}</p>
          <p class="muted">Code: ${(err && err.error && err.error.code) || '—'}</p>
          <button class="btn-secondary" onclick="location.reload()">Retry</button>
        </div>`;
    }
  }

  function render(items) {
    const c = document.getElementById('complaints-list');
    if (!c) return;

    if (!items || items.length === 0) {
      c.innerHTML = '<div class="empty-state">No complaints found.</div>';
      return;
    }

    c.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th><th>Citizen</th><th>Category</th><th>Priority</th>
            <th>Status</th><th>Created</th><th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${items.map(x => `
            <tr>
              <td>#${x.id}</td>
              <td>${window.utils.escapeHtml(x.citizen_name || '—')}</td>
              <td>${window.utils.escapeHtml(window.utils.categoryLabel(x.category))}</td>
              <td>${window.utils.escapeHtml(x.priority || '—')}</td>
              <td><span class="badge-status status-${x.status}">${window.utils.statusLabel(x.status)}</span></td>
              <td>${window.utils.formatDate(x.created_at)}</td>
              <td><a href="/admin/complaint_detail.html?id=${x.id}" class="btn-secondary btn-sm">View</a></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }

  function renderPagination(p) {
    const el = document.getElementById('pagination');
    if (!el) return;
    if (!p || p.total_pages <= 1) { el.innerHTML = ''; return; }
    el.innerHTML = `
      <button ${p.page <= 1 ? 'disabled' : ''} id="prev-btn">Prev</button>
      <span>Page ${p.page} of ${p.total_pages}</span>
      <button ${p.page >= p.total_pages ? 'disabled' : ''} id="next-btn">Next</button>
    `;
    document.getElementById('prev-btn')?.addEventListener('click', () => { currentPage--; load(); });
    document.getElementById('next-btn')?.addEventListener('click', () => { currentPage++; load(); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();