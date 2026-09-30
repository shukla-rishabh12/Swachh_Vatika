/**
 * Navigation builder — role-aware.
 */
(function () {
  const NAV = {
    CITIZEN: [
      { label: 'Dashboard',       href: '/citizen/dashboard.html' },
      { label: 'Report Waste',    href: '/citizen/report_waste.html' },
      { label: 'Request Pickup',  href: '/citizen/pickup_request.html' },
      { label: 'My Complaints',   href: '/citizen/complaints.html' },
      { label: 'My Pickups',      href: '/citizen/pickup.html' },
      { label: 'Wallet',          href: '/citizen/wallet.html' },
      { label: 'Notifications',   href: '/citizen/notifications.html' },
      { label: 'AI Assistant',    href: '/citizen/chat.html' },
      { label: 'Profile',         href: '/citizen/profile.html' },
    ],
    WORKER: [
      { label: 'Dashboard',     href: '/worker/dashboard.html' },
      { label: 'My Tasks',      href: '/worker/tasks.html' },
      { label: 'Task History',  href: '/worker/task_history.html' },
      { label: 'Notifications', href: '/worker/notifications.html' },
      { label: 'Profile',       href: '/worker/profile.html' },
    ],
    ADMIN: [
      { label: 'Dashboard',     href: '/admin/dashboard.html' },
      { label: 'Complaints',    href: '/admin/complaints.html' },
      { label: 'Tasks',         href: '/admin/tasks.html' },
      { label: 'Workers',       href: '/admin/workers.html' },
      { label: 'Users',         href: '/admin/users.html' },
      { label: 'Tokens',        href: '/admin/tokens.html' },
      { label: 'Analytics',     href: '/admin/analytics.html' },
      { label: 'Hotspots',      href: '/admin/hotspots.html' },
      { label: 'Notifications', href: '/admin/notifications.html' },
      { label: 'Audit Logs',    href: '/admin/audit_logs.html' },
    ],
  };

  const NOTIF_PAGE = {
    CITIZEN: '/citizen/notifications.html',
    WORKER:  '/worker/notifications.html',
    ADMIN:   '/admin/notifications.html',
  };

  const navigation = {
    build(role) {
      const sidebar = document.getElementById('sidebar');
      if (!sidebar) return;
      const items = NAV[role] || [];
      const currentPath = window.location.pathname;

      sidebar.innerHTML =
        '<div class="nav-brand">Swachh-Seva</div>' +
        '<ul class="nav-list">' +
          items.map(function(item) {
            return '<li>' +
              '<a href="' + item.href + '" class="' + (currentPath === item.href ? 'active' : '') + '">' +
                window.utils.escapeHtml(item.label) +
              '</a>' +
            '</li>';
          }).join('') +
        '</ul>' +
        '<div class="nav-footer">' +
          '<a href="#" id="nav-logout-btn" class="logout-link">Logout</a>' +
        '</div>';

      var logoutLink = document.getElementById('nav-logout-btn');
      if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
          e.preventDefault();
          window.auth.logout();
        });
      }

      var notifLink = document.getElementById('notif-link');
      if (notifLink) {
        notifLink.href = NOTIF_PAGE[role] || '/';
        notifLink.style.display = '';
      }

      var logoutBtn = document.getElementById('logout-btn');
      if (logoutBtn) {
        logoutBtn.style.display = '';
        logoutBtn.addEventListener('click', function() { window.auth.logout(); });
      }
    },
  };

  window.navigation = navigation;
})();