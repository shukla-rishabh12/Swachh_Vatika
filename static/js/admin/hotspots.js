(function () {
  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('ADMIN')) return;

    window.navigation.build('ADMIN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    await Promise.all([loadWards(), loadGrid()]);
  }

  async function loadWards() {
    const el = document.getElementById('ward-hotspots');
    try {
      const res = await window.api.get('/map/ward-hotspots');
      const items = res.data || [];
      if (items.length === 0) { el.innerHTML = '<div class="empty-state">No data.</div>'; return; }

      el.innerHTML = items.map(w => `
        <div class="hotspot-row">
          <span>${window.utils.escapeHtml(w.ward_name)} (${window.utils.escapeHtml(w.ward_code)})</span>
          <span class="badge-status density-${w.density}">${w.density}</span>
          <span>${w.count} complaints</span>
        </div>
      `).join('');
    } catch (err) {
      el.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed.')}</div>`;
    }
  }

  async function loadGrid() {
    const el = document.getElementById('grid-hotspots');
    try {
      const res = await window.api.get('/map/hotspots?min_count=2');
      const items = res.data || [];
      if (items.length === 0) { el.innerHTML = '<div class="empty-state">No hotspot clusters found.</div>'; return; }
      el.innerHTML = `
        <table class="data-table">
          <thead><tr><th>Latitude</th><th>Longitude</th><th>Count</th><th>Top Category</th><th>Density</th><th>Map</th></tr></thead>
          <tbody>
            ${items.slice(0, 20).map(h => `
              <tr>
                <td>${h.latitude}</td>
                <td>${h.longitude}</td>
                <td>${h.count}</td>
                <td>${window.utils.escapeHtml(window.utils.categoryLabel(h.top_category))}</td>
                <td><span class="badge-status density-${h.density}">${h.density}</span></td>
                <td><a target="_blank" href="https://www.openstreetmap.org/?mlat=${h.latitude}&mlon=${h.longitude}#map=16/${h.latitude}/${h.longitude}">Open</a></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } catch (err) {
      el.innerHTML = `<div class="error-state">${window.utils.escapeHtml(err.message || 'Failed.')}</div>`;
    }
  }

  document.addEventListener('DOMContentLoaded', init);
})();