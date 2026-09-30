(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    await Promise.all([loadWallet(), loadTransactions()]);
  }

  async function loadWallet() {
    try {
      const res = await window.api.get('/tokens/wallet');
      const w = res.data;
      document.getElementById('wallet-balance').textContent = w.balance || 0;
      document.getElementById('wallet-earned').textContent = w.lifetime_earned || 0;
      document.getElementById('wallet-spent').textContent = w.lifetime_spent || 0;
    } catch (e) { /* ignore */ }
  }

  async function loadTransactions() {
    const container = document.getElementById('tx-list');
    try {
      const res = await window.api.get('/tokens/transactions?page=1&page_size=30');
      const items = res.data.items || [];
      if (items.length === 0) {
        container.innerHTML = '<div class="empty-state">No transactions yet. Report waste or complete activities to earn SwachhTokens.</div>';
        return;
      }
      container.innerHTML = items.map(t => {
        const sign = t.transaction_type === 'EARN' ? '+' : (t.transaction_type === 'SPEND' ? '-' : '');
        const cls = t.transaction_type === 'EARN' ? 'tx-earn' : 'tx-spend';
        return `
          <div class="tx-row ${cls}">
            <div class="tx-main">
              <span class="tx-amount">${sign}${Math.abs(t.amount)}</span>
              <span class="tx-desc">${window.utils.escapeHtml(t.description || t.transaction_type)}</span>
            </div>
            <span class="tx-date">${window.utils.timeAgo(t.created_at)}</span>
          </div>`;
      }).join('');
    } catch (err) {
      container.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed to load transactions.')}</div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();