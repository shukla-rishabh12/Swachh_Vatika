(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    document.getElementById('adjust-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const userId = document.getElementById('adj-user-id').value;
      const amount = document.getElementById('adj-amount').value;
      const reason = document.getElementById('adj-reason').value.trim();
      const status = document.getElementById('adj-status');

      try {
        await window.api.post('/admin/tokens/adjust', {
          user_id: parseInt(userId),
          amount: parseInt(amount),
          description: reason || 'Admin adjustment',
        });
        status.textContent = 'Adjustment recorded.';
        window.utils.toast('Adjustment applied.', 'success');
        document.getElementById('adjust-form').reset();
        await load();
      } catch (err) {
        status.textContent = err.message || 'Failed.';
      }
    });

    await load();
  }

  async function load() {
    const container = document.getElementById('wallets-list');
    try {
      const res = await window.api.get('/admin/tokens?page=1&page_size=50');
      const stats = res.data.stats || {};
      document.getElementById('tk-earned').textContent = stats.total_earned || 0;
      document.getElementById('tk-spent').textContent = stats.total_spent || 0;
      document.getElementById('tk-adjusted').textContent = stats.total_adjusted || 0;
      document.getElementById('tk-balance').textContent = stats.total_balance || 0;

      const wallets = res.data.wallets || [];
      if (wallets.length === 0) {
        container.innerHTML = '<div class="empty-state">No wallets.</div>';
        return;
      }
      container.innerHTML = `
        <table class="data-table">
          <thead><tr><th>User ID</th><th>Name</th><th>Email</th><th>Balance</th><th>Earned</th><th>Spent</th></tr></thead>
          <tbody>
            ${wallets.map(w => `
              <tr>
                <td>#${w.user_id}</td>
                <td>${window.utils.escapeHtml(w.full_name || '—')}</td>
                <td>${window.utils.escapeHtml(w.email || '—')}</td>
                <td><strong>${w.balance}</strong></td>
                <td>${w.lifetime_earned}</td>
                <td>${w.lifetime_spent}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed.')}</div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();