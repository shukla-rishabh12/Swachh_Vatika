"""
Dashboard aggregation for citizen / worker / admin home pages.
"""
from backend.repositories.complaint_repository import ComplaintRepository
from backend.repositories.pickup_repository import PickupRepository
from backend.repositories.task_repository import TaskRepository
from backend.repositories.token_repository import TokenRepository
from backend.repositories.notification_repository import NotificationRepository
from backend.services.analytics_service import AnalyticsService


class DashboardService:

    def __init__(self):
        self.complaints = ComplaintRepository()
        self.pickups = PickupRepository()
        self.tasks = TaskRepository()
        self.tokens = TokenRepository()
        self.notifs = NotificationRepository()
        self.analytics = AnalyticsService()

    # ====================== CITIZEN ======================
    def citizen_dashboard(self, user_id):
        stats = self.complaints.count_by_citizen(user_id)
        recent_c, _ = self.complaints.list_by_citizen(user_id, page=1, page_size=5)

        recent_p, pickup_total = self.pickups.list_by_citizen(user_id, page=1, page_size=3)
        pickup_completed = sum(1 for p in recent_p if p['status'] == 'COMPLETED')

        wallet = self.tokens.get_wallet_by_user(user_id) or {}

        recent_n, _ = self.notifs.list_for_user(user_id, page=1, page_size=5)
        unread = self.notifs.unread_count(user_id)

        return {
            'complaint_summary': {
                'total':    stats.get('total') or 0,
                'open':     stats.get('open') or 0,
                'resolved': stats.get('resolved') or 0,
            },
            'pickup_summary': {
                'total':     pickup_total,
                'completed': pickup_completed,
            },
            'wallet': {
                'balance':         wallet.get('balance', 0),
                'lifetime_earned': wallet.get('lifetime_earned', 0),
                'lifetime_spent':  wallet.get('lifetime_spent', 0),
            },
            'recent_complaints': recent_c,
            'recent_notifications': recent_n,
            'unread_notifications': unread,
        }

    # ====================== WORKER ======================
    def worker_dashboard(self, user_id):
        stats = self.tasks.count_by_worker(user_id)
        recent, _ = self.tasks.list_by_worker(user_id, page=1, page_size=5)
        unread = self.notifs.unread_count(user_id)
        return {
            'stats': {
                'total':       stats.get('total') or 0,
                'assigned':    stats.get('assigned') or 0,
                'accepted':    stats.get('accepted') or 0,
                'in_progress': stats.get('in_progress') or 0,
                'completed':   stats.get('completed') or 0,
                'verified':    stats.get('verified') or 0,
            },
            'recent_tasks': recent,
            'unread_notifications': unread,
        }

    # ====================== ADMIN ======================
    def admin_dashboard(self):
        summary = self.analytics.get_summary()
        return {
            'summary': summary,
            'unread_notifications': 0,
        }