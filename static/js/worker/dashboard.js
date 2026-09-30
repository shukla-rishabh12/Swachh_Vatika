(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('WORKER')) return;

    window.navigation.build('WORKER');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    try {
      window.utils.showLoading('Loading dashboard...');
      const res = await window.api.get('/workers/dashboard');
      render(res.data, user);
    } catch (err) {
      window.utils.toast(err.message || 'Failed to load dashboard.', 'error');
    } finally {
      window.utils.hideLoading();
    }
  }

  function render(data, user) {
    document.getElementById('worker-name').textContent = user.email ? user.email.split('@')[0] : 'Worker';

    const s = data.stats || {};
    setText('stat-total',      s.total || 0);
    setText('stat-assigned',   s.assigned || 0);
    setText('stat-inprogress', s.in_progress || 0);
    setText('stat-completed',  s.completed || 0);
    setText('stat-verified',   s.verified || 0);

    const el = document.getElementById('recent-tasks');
    const items = data.recent_tasks || [];
    if (items.length === 0) {
      el.innerHTML = '<li class="empty">No tasks assigned yet.</li>';
      return;
    }
    el.innerHTML = items.map(t => `
      <li style="padding:12px 0; border-bottom:1px solid var(--line);">
        <a href="/worker/task_detail.html?id=${t.id}">
          <strong>Task #${t.id}</strong> — ${window.utils.escapeHtml(window.utils.categoryLabel(t.complaint_category) || 'Task')}
          <span class="badge-status status-${t.status}">${window.utils.statusLabel(t.status)}</span>
          <div class="muted" style="margin-top:4px;">${window.utils.timeAgo(t.created_at)}</div>
        </a>
      </li>
    `).join('');
  }

  function setText(id, v) {
    const el = document.getElementById(id);
    if (el) el.textContent = v;
  }

  document.addEventListener('DOMContentLoaded', init);
})();