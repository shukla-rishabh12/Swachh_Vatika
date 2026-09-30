/**
 * Admin — Complaint Detail (single-call verify/reject via backend chain)
 */
(function () {
  let complaintId = null;

  console.log('[admin/complaint_detail] loaded');

  async function init() {
    try {
      if (!window.api || !window.auth || !window.utils) return;

      const user = await window.auth.load();
      if (!user) { window.location.href = '/auth/login.html'; return; }
      if (user.role !== 'ADMIN') { window.location.href = '/403.html'; return; }

      try { window.navigation.build('ADMIN'); } catch (e) {}
      try { window.notif.updateBadge(); } catch (e) {}

      const em = document.getElementById('user-email');
      if (em) em.textContent = user.email || '';

      complaintId = window.utils.getQueryParam('id');
      if (!complaintId) { showError('No complaint ID.'); return; }

      await load();
    } catch (err) {
      console.error('[admin/complaint_detail] init FAILED:', err);
      showError(err.message || String(err));
    }
  }

  async function load() {
    const w = document.getElementById('detail-wrapper');
    if (!w) return;
    w.innerHTML = '<div class="loading">Loading complaint #' + complaintId + '...</div>';

    try {
      const res = await window.api.get(`/admin/complaints/${complaintId}`);
      if (!res || !res.data) throw new Error('Empty response');
      render(res.data);
    } catch (err) {
      console.error('[admin/complaint_detail] load FAILED:', err);
      showError((err && err.message) || 'Failed to load.');
    }
  }

  function render(c) {
    const w = document.getElementById('detail-wrapper');
    if (!w) return;

    const esc = window.utils.escapeHtml.bind(window.utils);
    const catLabel = window.utils.categoryLabel;
    const statusLabel = window.utils.statusLabel;
    const fmtDate = window.utils.formatDateTime;

    const images = (c.images || []).length
      ? c.images.map(img => `<img src="/uploads/${esc(img.file_path)}" alt="img" class="detail-image" />`).join('')
      : '<p class="muted">No image attached.</p>';

    const history = (c.history || []).length
      ? c.history.map(h => `
          <li>
            <strong>${esc(statusLabel(h.new_status))}</strong>
            <span class="muted"> — ${esc(fmtDate(h.created_at))}</span>
            ${h.changed_by_name ? `<span class="muted"> · ${esc(h.changed_by_name)}</span>` : ''}
            ${h.reason ? `<div class="history-reason">${esc(h.reason)}</div>` : ''}
          </li>
        `).join('')
      : '<li class="muted">No history.</li>';

    let actionsHtml = '';

    if (c.status === 'SUBMITTED' || c.status === 'UNDER_REVIEW') {
      actionsHtml = `
        <button class="btn-primary" data-action="verify">✓ Verify Complaint</button>
        <button class="btn-danger" data-action="reject" style="margin-left:10px;">✗ Reject</button>
        <button class="btn-danger" data-action="delete" style="margin-left:10px;">🗑 Delete</button>
      `;
    } else if (c.status === 'VERIFIED') {
      actionsHtml = `
        <div style="margin-top:14px;">
          <label style="display:block;font-weight:700;margin-bottom:8px;color:var(--forest);">Assign to Worker</label>
          <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
            <select id="worker-select" style="flex:1;min-width:220px;padding:10px;border:1.5px solid var(--line);border-radius:10px;background:var(--mint2);">
              <option value="">Loading workers...</option>
            </select>
            <button class="btn-primary" data-action="assign">Assign</button>
          </div>
        </div>
        <button class="btn-danger" data-action="delete" style="margin-top:14px;">🗑 Delete Complaint</button>
      `;
    } else if (c.status === 'CLOSED' || c.status === 'ADMIN_VERIFIED') {
      actionsHtml = `
        <p class="success-box">✓ Complaint is ${esc(statusLabel(c.status))}.</p>
        <button class="btn-danger" data-action="delete" style="margin-top:10px;">🗑 Delete Complaint</button>
      `;
    } else if (c.status === 'REJECTED' || c.status === 'CANCELLED') {
      actionsHtml = `
        <p class="muted">Complaint is ${esc(statusLabel(c.status))}.</p>
        <button class="btn-danger" data-action="delete" style="margin-top:10px;">🗑 Delete Complaint</button>
      `;
    } else {
      actionsHtml = `<p class="muted">Status: <strong>${esc(statusLabel(c.status))}</strong>. No actions.</p>`;
    }

    w.innerHTML = `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <h2 style="margin:0;">Complaint #${esc(c.id)}</h2>
          <span class="badge-status status-${esc(c.status)}">${esc(statusLabel(c.status))}</span>
        </div>

        <div class="stat-row" style="margin-top:18px;">
          <div class="stat"><span class="stat-label">Citizen</span><span class="stat-value" style="font-size:15px;">${esc(c.citizen_name || '—')}</span></div>
          <div class="stat"><span class="stat-label">Category</span><span class="stat-value" style="font-size:15px;">${esc(catLabel(c.category))}</span></div>
          <div class="stat"><span class="stat-label">Priority</span><span class="stat-value" style="font-size:15px;">${esc(c.priority)}</span></div>
          <div class="stat"><span class="stat-label">Created</span><span class="stat-value" style="font-size:13px;">${esc(fmtDate(c.created_at))}</span></div>
        </div>

        <div style="margin-top:18px;">
          <strong>📍 Address:</strong> ${esc(c.address || '—')}
          ${c.latitude && c.longitude ? `
            <br><strong>🗺️ Coords:</strong> ${c.latitude}, ${c.longitude}
            <a target="_blank" href="https://www.openstreetmap.org/?mlat=${c.latitude}&mlon=${c.longitude}#map=17/${c.latitude}/${c.longitude}" style="margin-left:8px;">Open Map</a>
          ` : ''}
        </div>

        <div style="margin-top:18px;">
          <strong>📝 Description:</strong>
          <p style="margin-top:6px;">${esc(c.description)}</p>
        </div>

        <div style="margin-top:18px;">
          <strong>📸 Images:</strong>
          <div class="image-gallery">${images}</div>
        </div>
      </div>

      <div class="card">
        <h3>📅 Timeline</h3>
        <ul class="history-list">${history}</ul>
      </div>

      <div class="card">
        <h3>⚡ Admin Actions</h3>
        <div style="margin-top:14px;">${actionsHtml}</div>
      </div>

      <div class="form-actions">
        <a href="/admin/complaints.html" class="btn-secondary">← Back</a>
      </div>
    `;

    // Attach event listeners using delegation
    w.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', () => handleAction(btn.dataset.action, c));
    });

    // Load workers for VERIFIED status
    const workerSel = document.getElementById('worker-select');
    if (workerSel) {
      loadWorkers().then(workers => {
        workerSel.innerHTML = '<option value="">-- Select worker --</option>' +
          workers.map(x => `<option value="${x.id}">${esc(x.full_name || x.email)}</option>`).join('');
      });
    }
  }

  async function handleAction(action, c) {
    if (action === 'verify') {
      if (!confirm('Verify this complaint?')) return;
      try {
        window.utils.showLoading('Verifying...');
        await window.api.post(`/admin/complaints/${complaintId}/verify`, {});
        window.utils.toast('Complaint verified!', 'success');
        window.utils.hideLoading();
        await load();
      } catch (err) {
        window.utils.hideLoading();
        console.error('verify error:', err);
        window.utils.toast((err && err.message) || 'Verify failed.', 'error');
      }
    } else if (action === 'reject') {
      const reason = prompt('Rejection reason:');
      if (reason === null) return;
      if (!reason.trim()) { window.utils.toast('Reason required.', 'error'); return; }
      try {
        window.utils.showLoading('Rejecting...');
        await window.api.post(`/admin/complaints/${complaintId}/reject`, { reason });
        window.utils.toast('Complaint rejected.', 'success');
        window.utils.hideLoading();
        await load();
      } catch (err) {
        window.utils.hideLoading();
        window.utils.toast((err && err.message) || 'Reject failed.', 'error');
      }
    } else if (action === 'delete') {
      if (!confirm('⚠️ PERMANENTLY DELETE complaint #' + complaintId + '?')) return;
      try {
        window.utils.showLoading('Deleting...');
        await window.api.delete(`/admin/complaints/${complaintId}`);
        window.utils.toast('Deleted.', 'success');
        setTimeout(() => window.location.href = '/admin/complaints.html', 600);
      } catch (err) {
        window.utils.hideLoading();
        window.utils.toast((err && err.message) || 'Delete failed.', 'error');
      }
    } else if (action === 'assign') {
      const workerSel = document.getElementById('worker-select');
      const workerId = workerSel ? workerSel.value : '';
      if (!workerId) { window.utils.toast('Select a worker.', 'error'); return; }
      try {
        window.utils.showLoading('Assigning...');
        await window.api.post('/admin/tasks/assign', {
          complaint_id: parseInt(complaintId),
          worker_id: parseInt(workerId),
        });
        window.utils.toast('Task assigned!', 'success');
        window.utils.hideLoading();
        await load();
      } catch (err) {
        window.utils.hideLoading();
        window.utils.toast((err && err.message) || 'Assign failed.', 'error');
      }
    }
  }

  async function loadWorkers() {
    try {
      const res = await window.api.get('/workers?page=1&page_size=100');
      return res.data.items || [];
    } catch (e) { return []; }
  }

  function showError(msg) {
    const w = document.getElementById('detail-wrapper');
    if (w) w.innerHTML = `
      <div class="error-state">
        <p><strong>Error:</strong> ${window.utils.escapeHtml(msg)}</p>
        <a href="/admin/complaints.html" class="btn-secondary" style="margin-top:12px;">← Back</a>
      </div>`;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();