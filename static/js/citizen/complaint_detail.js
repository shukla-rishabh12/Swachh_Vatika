/**
 * Citizen — Complaint Detail
 * URL: /citizen/complaint_detail.html?id=<complaint_id>
 */
(function () {
  let complaintId = null;

  console.log('[citizen/complaint_detail] Script loaded');

  async function init() {
    try {
      if (!window.api || !window.auth || !window.utils) {
        console.error('[citizen/complaint_detail] Core JS missing');
        return;
      }

      const user = await window.auth.load();
      if (!user) { window.location.href = '/auth/login.html'; return; }
      if (user.role !== 'CITIZEN') { window.location.href = '/403.html'; return; }

      try { window.navigation.build('CITIZEN'); } catch (e) {}
      try { window.notif.updateBadge(); } catch (e) {}

      const emailEl = document.getElementById('user-email');
      if (emailEl) emailEl.textContent = user.email || '';

      complaintId = window.utils.getQueryParam('id');
      console.log('[citizen/complaint_detail] ID:', complaintId);
      if (!complaintId) { showError('No complaint ID in URL.'); return; }

      await load();
    } catch (err) {
      console.error('[citizen/complaint_detail] init error:', err);
      showError('Init error: ' + (err.message || err));
    }
  }

  async function load() {
    const w = document.getElementById('detail-wrapper');
    if (!w) { console.error('#detail-wrapper not found'); return; }
    w.innerHTML = '<div class="loading">Loading complaint #' + complaintId + '...</div>';

    try {
      const res = await window.api.get(`/complaints/${complaintId}`);
      console.log('[citizen/complaint_detail] Response:', res);
      if (!res || !res.data) throw new Error('Empty response');
      render(res.data);
    } catch (err) {
      console.error('[citizen/complaint_detail] load error:', err);
      showError((err && err.message) || 'Failed to load complaint.');
    }
  }

  function render(c) {
    const w = document.getElementById('detail-wrapper');
    if (!w) return;

    const esc = window.utils.escapeHtml.bind(window.utils);
    const catLabel = window.utils.categoryLabel;
    const statusLabel = window.utils.statusLabel;
    const fmtDate = window.utils.formatDateTime;
    const timeAgo = window.utils.timeAgo;

    const images = (c.images || []).length
      ? c.images.map(img =>
          `<img src="/uploads/${esc(img.file_path)}" alt="complaint" class="detail-image" />`
        ).join('')
      : '<p class="muted">No image uploaded.</p>';

    const history = (c.history || []).length
      ? c.history.map(h => `
          <li>
            <strong>${esc(statusLabel(h.new_status))}</strong>
            <span class="muted"> — ${esc(fmtDate(h.created_at))}</span>
            ${h.reason ? `<div class="history-reason">${esc(h.reason)}</div>` : ''}
          </li>
        `).join('')
      : '<li class="muted">No history yet.</li>';

    w.innerHTML = `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <h2 style="margin:0;">Complaint #${esc(c.id)}</h2>
          <span class="badge-status status-${esc(c.status)}">${esc(statusLabel(c.status))}</span>
        </div>

        <div class="stat-row" style="margin-top:18px;">
          <div class="stat"><span class="stat-label">Category</span><span class="stat-value" style="font-size:15px;">${esc(catLabel(c.category))}</span></div>
          <div class="stat"><span class="stat-label">Priority</span><span class="stat-value" style="font-size:15px;">${esc(c.priority)}</span></div>
          <div class="stat"><span class="stat-label">Created</span><span class="stat-value" style="font-size:13px;">${esc(fmtDate(c.created_at))}</span></div>
        </div>

        <div style="margin-top:18px;">
          <strong>📍 Address:</strong> ${esc(c.address || '—')}
          ${c.latitude && c.longitude ? `
            <br><strong>🗺️ Coordinates:</strong> ${c.latitude}, ${c.longitude}
            <a target="_blank" href="https://www.openstreetmap.org/?mlat=${c.latitude}&mlon=${c.longitude}#map=17/${c.latitude}/${c.longitude}" style="margin-left:8px;">Open Map</a>
          ` : ''}
        </div>

        <div style="margin-top:18px;">
          <strong>📝 Description:</strong>
          <p style="margin-top:6px;">${esc(c.description)}</p>
        </div>

        <div style="margin-top:18px;">
          <strong>📸 Photo:</strong>
          <div class="image-gallery">${images}</div>
        </div>
      </div>

      <div class="card">
        <h3>📅 Timeline</h3>
        <ul class="history-list">${history}</ul>
      </div>

      <div class="form-actions">
        <a href="/citizen/complaints.html" class="btn-secondary">← Back to My Complaints</a>
      </div>
    `;
  }

  function showError(msg) {
    const w = document.getElementById('detail-wrapper');
    if (w) {
      w.innerHTML = `
        <div class="error-state">
          <p><strong>Error:</strong> ${window.utils.escapeHtml(msg)}</p>
          <p class="muted">Open F12 → Console for details.</p>
          <a href="/citizen/complaints.html" class="btn-secondary" style="margin-top:12px;">← Back</a>
        </div>
      `;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();