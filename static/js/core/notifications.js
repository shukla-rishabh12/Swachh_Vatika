/**
 * Notification helpers: unread count badge + list rendering.
 */
(function () {
  const notif = {
    async getUnreadCount() {
      try {
        const res = await window.api.get('/notifications/unread-count', { silent: true });
        return res.data.unread || 0;
      } catch { return 0; }
    },

    async updateBadge() {
      const badge = document.getElementById('notif-badge');
      if (!badge) return;
      const count = await this.getUnreadCount();
      if (count > 0) {
        badge.textContent = count > 99 ? '99+' : String(count);
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }
    },

    async markRead(id) {
      try {
        await window.api.post(`/notifications/${id}/read`, {});
        this.updateBadge();
      } catch (e) { /* ignore */ }
    },

    async markAllRead() {
      try {
        await window.api.post('/notifications/read-all', {});
        this.updateBadge();
      } catch (e) { /* ignore */ }
    },
  };

  window.notif = notif;
})();