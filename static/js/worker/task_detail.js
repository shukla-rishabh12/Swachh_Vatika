(function () {
  let currentTask = null;
  let taskId = null;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('WORKER')) return;

    window.navigation.build('WORKER');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    taskId = window.utils.getQueryParam('id');
    if (!taskId) { showError('No task ID provided.'); return; }

    await load();
  }

  async function load() {
    try {
      const res = await window.api.get(`/tasks/${taskId}`);
      currentTask = res.data;
      render(currentTask);
    } catch (err) {
      showError(err.message || 'Failed to load task.');
    }
  }

  function render(t) {
    const w = document.getElementById('task-wrapper');
    const proofsHtml = (t.proofs || []).length
      ? t.proofs.map(p => `
          <div class="proof-item">
            <img src="/uploads/${p.file_path}" alt="proof" class="proof-image" />
            <small class="muted">Uploaded ${window.utils.timeAgo(p.uploaded_at)}</small>
          </div>
        `).join('')
      : '<p class="muted">No proof uploaded yet.</p>';

    let actionsHtml = '';
    if (t.status === 'ASSIGNED') {
      actionsHtml = `<button class="btn-primary" id="accept-btn">✓ Accept Task</button>`;
    } else if (t.status === 'ACCEPTED') {
      actionsHtml = `<button class="btn-primary" id="start-btn">▶ Start Task</button>`;
    } else if (t.status === 'IN_PROGRESS') {
      actionsHtml = `
        <div class="form-group" style="margin-top:8px;">
          <label>Upload Completion Proof</label>
          <input type="file" id="proof-input" accept="image/jpeg,image/png,image/webp" />
          <small class="help-text">JPG, PNG, WEBP · max 5 MB</small>
        </div>
        <button class="btn-secondary" id="upload-proof-btn">📤 Upload Proof</button>
        <div id="proof-status" class="help-text"></div>
        <button class="btn-primary" id="complete-btn" style="margin-top:14px;">✓ Complete Task</button>
      `;
    } else if (t.status === 'COMPLETED') {
      actionsHtml = `<div class="info-box">⏳ Task completed. Waiting for admin verification.</div>`;
    } else if (t.status === 'VERIFIED') {
      actionsHtml = `<div class="success-box">✅ Task verified successfully!</div>`;
    } else if (t.status === 'VERIFICATION_FAILED') {
      actionsHtml = `<div class="error-box">❌ Verification failed. Please contact admin.</div>`;
    }

    w.innerHTML = `
      <div class="card">
        <div class="complaint-header">
          <h2 style="margin:0;">Task #${t.id}</h2>
          <span class="badge-status status-${t.status}">${window.utils.statusLabel(t.status)}</span>
        </div>
        <div class="stat-row" style="margin-top:18px;">
          <div class="stat"><span class="stat-label">Complaint #</span><span class="stat-value">${t.complaint_id || '—'}</span></div>
          <div class="stat"><span class="stat-label">Category</span><span class="stat-value" style="font-size:15px;">${window.utils.escapeHtml(window.utils.categoryLabel(t.complaint_category) || '—')}</span></div>
          <div class="stat"><span class="stat-label">Priority</span><span class="stat-value" style="font-size:15px;">${window.utils.escapeHtml(t.complaint_priority || '—')}</span></div>
        </div>
        <div style="margin-top:18px;">
          <strong>📍 Address:</strong> ${window.utils.escapeHtml(t.complaint_address || '—')}
          ${t.complaint_latitude && t.complaint_longitude ? `
            <br><a target="_blank" href="https://www.openstreetmap.org/?mlat=${t.complaint_latitude}&mlon=${t.complaint_longitude}#map=17/${t.complaint_latitude}/${t.complaint_longitude}">🗺️ Open in Map</a>
          ` : ''}
        </div>
        <div style="margin-top:18px;">
          <strong>🕐 Assigned:</strong> ${window.utils.formatDateTime(t.assigned_at)}
        </div>
        ${t.complaint_description ? `
          <div style="margin-top:18px;">
            <strong>📝 Description:</strong>
            <p style="margin-top:6px;">${window.utils.escapeHtml(t.complaint_description)}</p>
          </div>
        ` : ''}
      </div>

      <div class="card">
        <h3>📸 Proof Uploaded</h3>
        <div class="proof-gallery">${proofsHtml}</div>
      </div>

      <div class="card">
        <h3>Actions</h3>
        <div style="margin-top:14px;">${actionsHtml}</div>
      </div>

      <div class="form-actions">
        <a href="/worker/tasks.html" class="btn-secondary">← Back to Tasks</a>
      </div>
    `;

    wireActions();
  }

  function wireActions() {
    document.getElementById('accept-btn')?.addEventListener('click', async () => {
      await doAction('accept', 'Task accepted.');
    });
    document.getElementById('start-btn')?.addEventListener('click', async () => {
      await doAction('start', 'Task started.');
    });
    document.getElementById('complete-btn')?.addEventListener('click', async () => {
      await doAction('complete', 'Task marked complete.');
    });

    document.getElementById('upload-proof-btn')?.addEventListener('click', async () => {
      const input = document.getElementById('proof-input');
      const status = document.getElementById('proof-status');
      if (!input.files[0]) {
        status.textContent = '⚠️ Please choose an image first.';
        return;
      }
      const fd = new FormData();
      fd.append('image', input.files[0]);

      if (navigator.geolocation) {
        await new Promise(resolve => {
          navigator.geolocation.getCurrentPosition(
            (pos) => {
              fd.append('latitude', pos.coords.latitude);
              fd.append('longitude', pos.coords.longitude);
              resolve();
            },
            () => resolve(),
            { timeout: 5000 }
          );
        });
      }

      status.textContent = '⏳ Uploading...';
      try {
        await window.api.upload(`/tasks/${taskId}/proof`, fd);
        status.textContent = '✅ Proof uploaded.';
        window.utils.toast('Proof uploaded.', 'success');
        await load();
      } catch (err) {
        status.textContent = '❌ ' + (err.message || 'Upload failed.');
      }
    });
  }

  async function doAction(action, successMsg) {
    try {
      await window.api.post(`/tasks/${taskId}/${action}`, {});
      window.utils.toast(successMsg, 'success');
      await load();
    } catch (err) {
      window.utils.toast(err.message || 'Action failed.', 'error');
    }
  }

  function showError(msg) {
    document.getElementById('task-wrapper').innerHTML =
      `<div class="error-state">${window.utils.escapeHtml(msg)}</div>`;
  }

  document.addEventListener('DOMContentLoaded', init);
})();