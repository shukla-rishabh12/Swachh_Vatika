/**
 * Auth state — current user, login, logout, role redirects.
 */
(function () {
  const auth = {
    currentUser: null,

    async load() {
      try {
        const res = await window.api.get('/auth/me', { silent: true });
        this.currentUser = res.data.user;
        return this.currentUser;
      } catch (err) {
        this.currentUser = null;
        return null;
      }
    },

    async login(email, password) {
      const res = await window.api.post('/auth/login', { email, password });
      this.currentUser = res.data.user;
      return this.currentUser;
    },

    async register(payload) {
      const res = await window.api.post('/auth/register', payload);
      this.currentUser = res.data.user;
      return this.currentUser;
    },

    async logout() {
      try {
        await window.api.post('/auth/logout', {});
      } catch (e) { /* ignore */ }
      this.currentUser = null;
      window.location.href = '/auth/login.html';
    },

    redirectAfterLogin(role) {
      const map = {
        CITIZEN: '/citizen/dashboard.html',
        WORKER:  '/worker/dashboard.html',
        ADMIN:   '/admin/dashboard.html',
      };
      window.location.href = map[role] || '/';
    },

    requireRole(expectedRole) {
      if (!this.currentUser) {
        window.location.href = '/auth/login.html';
        return false;
      }
      if (expectedRole && this.currentUser.role !== expectedRole) {
        window.location.href = '/403.html';
        return false;
      }
      return true;
    },
  };

  window.auth = auth;
})();