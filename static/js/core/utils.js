/**
 * Shared utility helpers.
 */
(function () {
  const utils = {

    // ---------- DOM ----------
    $(selector, root = document) {
      return root.querySelector(selector);
    },
    $$(selector, root = document) {
      return Array.from(root.querySelectorAll(selector));
    },
    on(el, event, handler) {
      if (el) el.addEventListener(event, handler);
    },

    // ---------- HTML SAFETY ----------
    escapeHtml(str) {
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    },

    // ---------- DATE / TIME ----------
    formatDate(iso) {
      if (!iso) return '—';
      try {
        const d = new Date(iso);
        return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
      } catch { return iso; }
    },
    formatDateTime(iso) {
      if (!iso) return '—';
      try {
        const d = new Date(iso);
        return d.toLocaleString('en-IN', {
          day: '2-digit', month: 'short', year: 'numeric',
          hour: '2-digit', minute: '2-digit'
        });
      } catch { return iso; }
    },
    timeAgo(iso) {
      if (!iso) return '';
      try {
        const then = new Date(iso).getTime();
        const now = Date.now();
        const sec = Math.floor((now - then) / 1000);
        if (sec < 60) return 'just now';
        const min = Math.floor(sec / 60);
        if (min < 60) return `${min}m ago`;
        const hr = Math.floor(min / 60);
        if (hr < 24) return `${hr}h ago`;
        const day = Math.floor(hr / 24);
        if (day < 30) return `${day}d ago`;
        return utils.formatDate(iso);
      } catch { return ''; }
    },

    // ---------- LABELS ----------
    categoryLabel(cat) {
      const map = {
        GARBAGE_DUMP: 'Garbage Dump',
        OVERFLOWING_BIN: 'Overflowing Bin',
        PLASTIC_WASTE: 'Plastic Waste',
        CONSTRUCTION_WASTE: 'Construction Waste',
        DRAIN_WASTE: 'Drain Waste',
        OPEN_DUMPING: 'Open Dumping',
        DEAD_ANIMAL: 'Dead Animal',
        OTHER: 'Other',
      };
      return map[cat] || cat || '—';
    },
    statusLabel(status) {
      return (status || '').replace(/_/g, ' ');
    },

    // ---------- TOAST ----------
    toast(message, type = 'info', duration = 3500) {
      let container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
      }
      const el = document.createElement('div');
      el.className = `toast toast-${type}`;
      el.textContent = message;
      container.appendChild(el);
      setTimeout(() => {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 300);
      }, duration);
    },

    // ---------- LOADING OVERLAY ----------
    showLoading(text = 'Loading...') {
      let overlay = document.getElementById('loading-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.innerHTML = `<div class="spinner"></div><div class="loading-text"></div>`;
        document.body.appendChild(overlay);
      }
      overlay.querySelector('.loading-text').textContent = text;
      overlay.style.display = 'flex';
    },
    hideLoading() {
      const overlay = document.getElementById('loading-overlay');
      if (overlay) overlay.style.display = 'none';
    },

    // ---------- QUERY PARAMS ----------
    getQueryParam(name) {
      return new URLSearchParams(window.location.search).get(name);
    },

    // ---------- MISC ----------
    debounce(fn, delay = 300) {
      let timer;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
      };
    },

    confirmDialog(message) {
      return window.confirm(message);
    },
  };

  window.utils = utils;
})();