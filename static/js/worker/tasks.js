(function () {
  let currentPage = 1;
  const pageSize = 10;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('WORKER')) return;

    window.navigation.build('WORKER');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('filter-status').addEventListener('change', () => {
      currentPage = 1;
      load();
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
      const res = await window.api.get(`/tasks/my?${params.toString()}`);
      render(res.data.items);
      renderPagination(res.data.pagination);
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load tasks.')}</div>`;
    }
  }

  function render(items) {
    const container = document.getElementById('tasks-list');
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="empty-state">No tasks found.</div>';
      return;
    }
    container.innerHTML = items.map(t => `
      <div class="card task-item">
        <div class="task-header">
          <strong>Task #${t.id}</strong>
          <span class="badge-status status-${t.status}">${window.utils.statusLabel(t.status)}</span>
        </div>
        <div class="task-body">
          <p><strong>Category:</strong> ${window.utils.escapeHtml(window.utils.categoryLabel(t.complaint_category) || '—')}</p>
          <p><strong>Priority:</strong> ${window.utils.escapeHtml(t.complaint_priority || '—')}</p>
          <p><strong>Address:</strong> ${window.utils.escapeHtml(t.complaint_address || '—')}</p>
          <p class="muted">${window.utils.timeAgo(t.created_at)}</p>
        </div>
        <a href="/worker/task_detail.html?id=${t.id}" class="btn-secondary">View Task</a>
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