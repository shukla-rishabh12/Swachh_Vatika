(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    try {
      window.utils.showLoading('Loading dashboard...');
      const res = await window.api.get('/admin/dashboard');
      render(res.data.summary || {});
    } catch (err) {
      window.utils.toast(err.message || 'Failed to load.', 'error');
    } finally {
      window.utils.hideLoading();
    }
  }

  function render(s) {
    setText('kpi-total-complaints', s.total_complaints || 0);
    setText('kpi-pending-review',   s.pending_review || 0);
    setText('kpi-verified',         s.verified_complaints || 0);
    setText('kpi-pending-proof',    s.pending_proof_verification || 0);
    setText('kpi-resolved',         s.resolved_complaints || 0);
    setText('kpi-active-tasks',     s.active_tasks || 0);
    setText('kpi-workers',          s.total_workers || 0);
    setText('kpi-active-workers',   s.active_workers || 0);
    setText('kpi-citizens',         s.total_citizens || 0);
    setText('kpi-pickups',          s.total_pickups || 0);
    setText('kpi-pending-pickups',  s.pending_pickups || 0);
    setText('kpi-tokens',           s.tokens_issued || 0);
  }

  function setText(id, v) {
    const el = document.getElementById(id);
    if (el) el.textContent = v;
  }

  document.addEventListener('DOMContentLoaded', init);
})();