(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    try {
      const res = await window.api.get('/analytics/complaints');
      const d = res.data;

      renderBreakdown('by-status',   d.by_status,   'status');
      renderBreakdown('by-category', d.by_category, 'category', true);
      renderBreakdown('by-priority', d.by_priority, 'priority');
      renderBreakdown('by-ward',     d.by_ward,     'ward_name');

      const r = d.resolution || {};
      document.getElementById('res-total').textContent = r.total_closed || 0;
      document.getElementById('res-avg').textContent = r.avg_resolution_days || 0;
    } catch (err) {
      window.utils.toast(err.message || 'Failed to load analytics.', 'error');
    }
  }

  function renderBreakdown(elId, items, key, useLabel = false) {
    const el = document.getElementById(elId);
    if (!items || items.length === 0) {
      el.innerHTML = '<div class="empty-state">No data.</div>';
      return;
    }
    const max = Math.max(...items.map(i => i.count || 0));
    el.innerHTML = items.map(i => {
      const label = useLabel
        ? window.utils.categoryLabel(i[key])
        : (i[key] || '—');
      const pct = max ? Math.round((i.count / max) * 100) : 0;
      return `
        <div class="bar-row">
          <span class="bar-label">${window.utils.escapeHtml(label)}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
          <span class="bar-value">${i.count || 0}</span>
        </div>`;
    }).join('');
  }

  document.addEventListener('DOMContentLoaded', init);
})();