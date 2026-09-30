(function () {
  let currentPage = 1;
  const pageSize = 10;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('filter-status').addEventListener('change', () => { currentPage = 1; load(); });
    document.getElementById('filter-category').addEventListener('change', () => { currentPage = 1; load(); });

    load();
  }

  async function load() {
    const container = document.getElementById('complaints-list');
    container.innerHTML = '<div class="loading">Loading...</div>';

    const status = document.getElementById('filter-status').value;
    const category = document.getElementById('filter-category').value;

    const params = new URLSearchParams({ page: currentPage, page_size: pageSize });
    if (status) params.append('status', status);
    if (category) params.append('category', category);

    try {
      const res = await window.api.get(`/complaints/my?${params.toString()}`);
      render(res.data.items);
      renderPagination(res.data.pagination);
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load.')}</div>`;
    }
  }

  function render(items) {
    const container = document.getElementById('complaints-list');
    if (!items || items.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No complaints found.</p>
          <a href="/citizen/report_waste.html" class="btn-primary">Report Waste</a>
        </div>`;
      return;
    }

    container.innerHTML = items.map(c => `
      <div class="complaint-item card">
        <div class="complaint-header">
          <strong>#${c.id} — ${window.utils.escapeHtml(window.utils.categoryLabel(c.category))}</strong>
          <span class="badge-status status-${c.status}">${window.utils.escapeHtml(window.utils.statusLabel(c.status))}</span>
        </div>
        <p class="complaint-desc">${window.utils.escapeHtml((c.description || '').slice(0, 120))}${(c.description || '').length > 120 ? '…' : ''}</p>
        <div class="complaint-meta">
          <span>Priority: ${window.utils.escapeHtml(c.priority)}</span>
          <span>${window.utils.formatDate(c.created_at)}</span>
        </div>
        <a href="/citizen/complaint_detail.html?id=${c.id}" class="btn-secondary">View Details</a>
      </div>
    `).join('');
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