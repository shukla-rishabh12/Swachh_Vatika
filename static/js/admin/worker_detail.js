/**
 * Admin — Worker Detail with activate/deactivate
 */
(function () {
  let workerId = null;

  console.log('[admin/worker_detail] loaded');

  async function init() {
    if (!window.api || !window.auth || !window.utils) return;

    const user = await window.auth.load();
    if (!user) { window.location.href = '/auth/login.html'; return; }
    if (user.role !== 'ADMIN') { window.location.href = '/403.html'; return; }

    try { window.navigation.build('ADMIN'); } catch (e) {}
    try { window.notif.updateBadge(); } catch (e) {}

    const emailEl = document.getElementById('user-email');
    if (emailEl) emailEl.textContent = user.email || '';

    workerId = window.utils.getQueryParam('id');
    if (!workerId) { showError('No worker ID.'); return; }

    await load();
  }

  async function load() {
    const w = document.getElementById('worker-wrapper') || document.querySelector('.page-wrapper');
    if (!w) return;
    w.innerHTML = '<div class="loading">Loading worker...</div>';

    try {
      const res = await window.api.get(`/workers/${workerId}`);
      if (!res || !res.data) throw new Error('Empty response');
      render(res.data);
    } catch (err) {
      console.error(err);
      showError(err.message || 'Failed to load.');
    }
  }

  function render(w) {
    const el = document.getElementById('worker-wrapper') || document.querySelector('.page-wrapper');
    if (!el) return;

    const esc = window.utils.escapeHtml.bind(window.utils);
    const fmtDate = window.utils.formatDateTime;
    const profile = w.profile || {};
    const stats = w.stats || {};

    el.innerHTML = `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <h2 style="margin:0;">👷 Worker #${esc(w.id)}</h2>
          <span class="badge-status ${w.is_active ? 'status-ACTIVE' : 'status-REJECTED'}">
            ${w.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div class="stat-row" style="margin-top:18px;">
          <div class="stat"><span class="stat-label">Name</span><span class="stat-value" style="font-size:15px;">${esc(profile.full_name || '—')}</span></div>
          <div class="stat"><span class="stat-label">Email</span><span class="stat-value" style="font-size:13px;">${esc(w.email || '—')}</span></div>
          <div class="stat"><span class="stat-label">Phone</span><span class="stat-value" style="font-size:15px;">${esc(profile.phone || '—')}</span></div>
        </div>

        ${profile.address || profile.city ? `
          <div style="margin-top:18px;">
            <strong>📍 Address:</strong> ${esc(profile.address || '—')}${profile.city ? ', ' + esc(profile.city) : ''}
          </div>
        ` : ''}
      </div>

      <div class="card">
        <h3>📊 Task Statistics</h3>
        <div class="stat-row" style="margin-top:14px;">
          <div class="stat"><span class="stat-label">Total</span><span class="stat-value">${stats.total || 0}</span></div>
          <div class="stat"><span class="stat-label">Assigned</span><span class="stat-value">${stats.assigned || 0}</span></div>
          <div class="stat"><span class="stat-label">In Progress</span><span class="stat-value">${stats.in_progress || 0}</span></div>
          <div class="stat"><span class="stat-label">Completed</span><span class="stat-value">${stats.completed || 0}</span></div>
          <div class="stat"><span class="stat-label">Verified</span><span class="stat-value">${stats.verified || 0}</span></div>
        </div>
      </div>

      <div class="card">
        <h3>⚡ Actions</h3>
        <div class="action-buttons" style="margin-top:14px;">
          <button class="btn-danger" id="toggle-status-btn">
            ${w.is_active ? '🚫 Deactivate Worker' : '✓ Activate Worker'}
          </button>
          <a href="/admin/tasks.html?worker_id=${w.id}" class="btn-secondary">🔧 View Tasks</a>
        </div>
      </div>

      <div class="form-actions">
        <a href="/admin/workers.html" class="btn-secondary">← Back to Workers</a>
      </div>
    `;

    document.getElementById('toggle-status-btn')?.addEventListener('click', async () => {
      const newStatus = !w.is_active;
      const msg = newStatus ? 'Activate this worker?' : 'Deactivate this worker?';
      if (!confirm(msg)) return;

      const btn = document.getElementById('toggle-status-btn');
      btn.disabled = true;
      btn.textContent = 'Updating...';

      try {
        await window.api.patch(`/users/${w.id}/status`, { is_active: newStatus });
        window.utils.toast('Worker status updated.', 'success');
        await load();
      } catch (err) {
        window.utils.toast(err.message || 'Update failed.', 'error');
        btn.disabled = false;
        btn.textContent = newStatus ? '✓ Activate Worker' : '🚫 Deactivate Worker';
      }
    });
  }

  function showError(msg) {
    const el = document.getElementById('worker-wrapper') || document.querySelector('.page-wrapper');
    if (el) {
      el.innerHTML = `
        <div class="error-state">
          <p><strong>Error:</strong> ${window.utils.escapeHtml(msg)}</p>
          <a href="/admin/workers.html" class="btn-secondary" style="margin-top:12px;">← Back</a>
        </div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();