"""
Worker-specific business logic (dashboard stats + profile).
"""
from backend.repositories.task_repository import TaskRepository
from backend.repositories.user_repository import UserRepository
from backend.services.auth_service import AuthError
from backend.utils.constants import ROLE_WORKER


class WorkerService:

    def __init__(self):
        self.tasks = TaskRepository()
        self.users = UserRepository()

    def get_dashboard(self, worker_id):
        stats = self.tasks.count_by_worker(worker_id)
        recent, _ = self.tasks.list_by_worker(worker_id, page=1, page_size=5)
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
        }

    def list_all_workers(self, page=1, page_size=20):
        items, total = self.users.list_users(
            role=ROLE_WORKER, page=page, page_size=page_size
        )
        for w in items:
            w.pop('password_hash', None)
            w['task_stats'] = self.tasks.count_by_worker(w['id'])
        return items, total

    def get_worker_detail(self, worker_id):
        w = self.users.find_by_id(worker_id)
        if not w or w['role'] != ROLE_WORKER:
            raise AuthError('Worker not found.', 'NOT_FOUND', 404)
        profile = self.users.get_profile(worker_id)
        stats = self.tasks.count_by_worker(worker_id)
        return {
            'id': w['id'],
            'email': w['email'],
            'is_active': bool(w['is_active']),
            'profile': profile or {},
            'stats': stats,
        }