(function () {
  let taskId = null;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    taskId = window.utils.getQueryParam('task');
    if (!taskId) { showError('No task specified.'); return; }

    await load();
  }

  async function load() {
    try {
      const res = await window.api.get(`/admin/tasks/${taskId}`);
      render(res.data);
    } catch (err) {
      showError(err.message || 'Failed to load task.');
    }
  }

  function render(t) {
    const w = document.getElementById('verify-wrapper');
    const proofs = (t.proofs || []).map(p => `
      <div class="proof-item">
        <img src="/uploads/${p.file_path}" alt="proof" class="proof-image" />
        ${p.latitude && p.longitude ? `<div class="muted">Lat ${p.latitude}, Lng ${p.longitude}</div>` : ''}
        <div class="muted">Uploaded: ${window.utils.formatDateTime(p.uploaded_at)}</div>
      </div>
    `).join('') || '<p class="muted">No proof uploaded.</p>';

    let actions = '';
    if (t.status === 'COMPLETED') {
      actions = `
        <button class="btn-primary" id="approve-btn">Approve & Close</button>
        <button class="btn-danger" id="reject-btn">Reject</button>
      `;
    } else {
      actions = `<p class="muted">Task status: ${window.utils.statusLabel(t.status)}</p>`;
    }

    w.innerHTML = `
      <div class="card">
        <div class="detail-header">
          <h2>Task #${t.id}</h2>
          <span class="badge-status status-${t.status}">${window.utils.statusLabel(t.status)}</span>
        </div>
        <div class="detail-grid">
          <div><strong>Worker:</strong> ${window.utils.escapeHtml(t.worker_name || '—')}</div>
          <div><strong>Complaint #:</strong> ${t.complaint_id || '—'}</div>
          <div><strong>Category:</strong> ${window.utils.escapeHtml(window.utils.categoryLabel(t.complaint_category) || '—')}</div>
          <div><strong>Address:</strong> ${window.utils.escapeHtml(t.complaint_address || '—')}</div>
          <div><strong>Completed:</strong> ${t.completed_at ? window.utils.formatDateTime(t.completed_at) : '—'}</div>
        </div>
      </div>

      <div class="card">
        <h3>Completion Proof</h3>
        <div class="proof-gallery">${proofs}</div>
      </div>

      <div class="card">
        <h3>Verification</h3>
        <div class="detail-actions">${actions}</div>
      </div>

      <div class="detail-actions">
        <a href="/admin/tasks.html" class="btn-secondary">Back</a>
      </div>
    `;

    document.getElementById('approve-btn')?.addEventListener('click', async () => {
      try {
        await window.api.post(`/admin/tasks/${taskId}/verify`, {
          approved: true,
          reason: 'Approved by admin',
        });
        window.utils.toast('Task verified & complaint closed.', 'success');
        setTimeout(() => window.location.href = '/admin/tasks.html', 800);
      } catch (err) {
        window.utils.toast(err.message || 'Verify failed.', 'error');
      }
    });

    document.getElementById('reject-btn')?.addEventListener('click', async () => {
      const reason = prompt('Reason for rejection:');
      if (!reason || !reason.trim()) return;
      try {
        await window.api.post(`/admin/tasks/${taskId}/verify`, {
          approved: false,
          reason,
        });
        window.utils.toast('Verification rejected.', 'success');
        await load();
      } catch (err) {
        window.utils.toast(err.message || 'Failed.', 'error');
      }
    });
  }

  function showError(msg) {
    document.getElementById('verify-wrapper').innerHTML =
      `<div class="error-state">${window.utils.escapeHtml(msg)}</div>`;
  }

  document.addEventListener('DOMContentLoaded', init);
})();