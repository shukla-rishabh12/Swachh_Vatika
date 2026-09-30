/**
 * Citizen dashboard page logic.
 */
(function () {
  async function init() {
    // 1. Load auth + build navigation
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();

    // Show user email / name
    const emailEl = document.getElementById('user-email');
    if (emailEl) emailEl.textContent = user.email || '';

    // 2. Fetch dashboard data
    try {
      window.utils.showLoading('Loading dashboard...');
      const res = await window.api.get('/citizen/dashboard');
      render(res.data, user);
    } catch (err) {
      window.utils.toast(err.message || 'Failed to load dashboard.', 'error');
    } finally {
      window.utils.hideLoading();
    }
  }

  function render(data, user) {
    // Welcome
    const nameEl = document.getElementById('user-name');
    if (nameEl) nameEl.textContent = (data.recent_notifications && '') || user.email || 'Citizen';

    // Stats
    const cs = data.complaint_summary || {};
    setText('stat-total-complaints', cs.total || 0);
    setText('stat-open-complaints', cs.open || 0);
    setText('stat-resolved-complaints', cs.resolved || 0);

    const w = data.wallet || {};
    setText('stat-wallet-balance', w.balance || 0);
    setText('stat-wallet-earned', w.lifetime_earned || 0);

    // Recent complaints
    const rc = document.getElementById('recent-complaints');
    if (rc) {
      const list = data.recent_complaints || [];
      if (list.length === 0) {
        rc.innerHTML = '<li class="empty">No complaints yet. <a href="/citizen/report_waste.html">Report one</a>.</li>';
      } else {
        rc.innerHTML = list.map(c => `
          <li>
            <a href="/citizen/complaint_detail.html?id=${c.id}">
              #${c.id} — ${window.utils.escapeHtml(window.utils.categoryLabel(c.category))}
              <span class="badge-status">${window.utils.escapeHtml(window.utils.statusLabel(c.status))}</span>
              <span class="muted">${window.utils.timeAgo(c.created_at)}</span>
            </a>
          </li>`).join('');
      }
    }

    // Recent notifications
    const rn = document.getElementById('recent-notifications');
    if (rn) {
      const list = data.recent_notifications || [];
      if (list.length === 0) {
        rn.innerHTML = '<li class="empty">You\'re all caught up.</li>';
      } else {
        rn.innerHTML = list.map(n => `
          <li class="${n.is_read ? 'read' : 'unread'}">
            <strong>${window.utils.escapeHtml(n.title)}</strong>
            <span class="muted">${window.utils.timeAgo(n.created_at)}</span>
            <div class="notif-msg">${window.utils.escapeHtml(n.message)}</div>
          </li>`).join('');
      }
    }
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  document.addEventListener('DOMContentLoaded', init);
})();