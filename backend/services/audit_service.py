
"""
Audit business logic — high-level helpers.
"""
from flask import request
from backend.repositories.audit_repository import AuditRepository
from backend.utils.constants import (
    AUDIT_ADMIN_VERIFIED_COMPLAINT, AUDIT_ADMIN_REJECTED_COMPLAINT,
    AUDIT_WORKER_ASSIGNED, AUDIT_ADMIN_VERIFIED_TASK,
    AUDIT_ADMIN_REJECTED_TASK, AUDIT_TOKEN_ADJUSTED,
    AUDIT_USER_STATUS_CHANGED, AUDIT_ADMIN_LOGIN,
)


class AuditService:

    def __init__(self):
        self.repo = AuditRepository()

    @staticmethod
    def _ip():
        try:
            return request.remote_addr
        except Exception:
            return None

    # ====================== READ ======================
    def list_logs(self, **filters):
        return self.repo.list_logs(**filters)

    # ====================== HIGH-LEVEL HELPERS ======================
    def log(self, actor_user_id, action, entity_type=None, entity_id=None,
            old_value=None, new_value=None):
        return self.repo.create(
            actor_user_id, action, entity_type, entity_id,
            old_value, new_value, self._ip()
        )

    def log_complaint_verified(self, admin_id, complaint_id, old_status, new_status):
        return self.repo.create(
            admin_id, AUDIT_ADMIN_VERIFIED_COMPLAINT,
            'COMPLAINT', complaint_id,
            old_value=old_status, new_value=new_status,
            ip_address=self._ip()
        )

    def log_complaint_rejected(self, admin_id, complaint_id, reason=None):
        return self.repo.create(
            admin_id, AUDIT_ADMIN_REJECTED_COMPLAINT,
            'COMPLAINT', complaint_id,
            old_value=None, new_value={'reason': reason},
            ip_address=self._ip()
        )

    def log_worker_assigned(self, admin_id, task_id, worker_id, complaint_id):
        return self.repo.create(
            admin_id, AUDIT_WORKER_ASSIGNED,
            'TASK', task_id,
            new_value={'worker_id': worker_id, 'complaint_id': complaint_id},
            ip_address=self._ip()
        )

    def log_task_verified(self, admin_id, task_id, approved, reason=None):
        action = AUDIT_ADMIN_VERIFIED_TASK if approved else AUDIT_ADMIN_REJECTED_TASK
        return self.repo.create(
            admin_id, action,
            'TASK', task_id,
            new_value={'approved': approved, 'reason': reason},
            ip_address=self._ip()
        )

    def log_token_adjusted(self, admin_id, user_id, amount, reason=None):
        return self.repo.create(
            admin_id, AUDIT_TOKEN_ADJUSTED,
            'USER', user_id,
            new_value={'amount': amount, 'reason': reason},
            ip_address=self._ip()
        )

    def log_user_status_changed(self, admin_id, user_id, old_status, new_status):
        return self.repo.create(
            admin_id, AUDIT_USER_STATUS_CHANGED,
            'USER', user_id,
            old_value=old_status, new_value=new_status,
            ip_address=self._ip()
        )

    def log_admin_login(self, admin_id):
        return self.repo.create(
            admin_id, AUDIT_ADMIN_LOGIN,
            'USER', admin_id,
            new_value='Admin logged in',
            ip_address=self._ip()
        )