"""
Task business logic (with notifications + audit + token reward hooks).
"""
from backend.repositories.task_repository import TaskRepository
from backend.repositories.complaint_repository import ComplaintRepository
from backend.repositories.user_repository import UserRepository
from backend.services.auth_service import AuthError
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.db import utc_now
from backend.utils.constants import (
    ROLE_ADMIN, ROLE_WORKER,
    COMPLAINT_VERIFIED, COMPLAINT_ASSIGNED,
    COMPLAINT_IN_PROGRESS, COMPLAINT_WORKER_COMPLETED,
    COMPLAINT_ADMIN_VERIFIED, COMPLAINT_CLOSED,
    TASK_ASSIGNED, TASK_ACCEPTED, TASK_IN_PROGRESS,
    TASK_COMPLETED, TASK_VERIFIED, TASK_VERIFICATION_FAILED,
)


class TaskService:

    def __init__(self):
        self.tasks = TaskRepository()
        self.complaints = ComplaintRepository()
        self.users = UserRepository()
        self.notifs = NotificationService()
        self.audit = AuditService()

    # ====================== ADMIN: ASSIGN ======================
    def assign_task(self, complaint_id, worker_id, admin_user, priority=None):
        complaint = self.complaints.find_by_id(complaint_id)
        if not complaint:
            raise AuthError('Complaint not found.', 'NOT_FOUND', 404)

        if complaint['status'] != COMPLAINT_VERIFIED:
            raise AuthError(
                f'Only VERIFIED complaints can be assigned. Current: {complaint["status"]}',
                'INVALID_STATUS_TRANSITION', 422
            )

        worker = self.users.find_by_id(worker_id)
        if not worker:
            raise AuthError('Worker not found.', 'NOT_FOUND', 404)
        if worker['role'] != ROLE_WORKER:
            raise AuthError('Selected user is not a worker.',
                            'VALIDATION_ERROR', 422)
        if not worker['is_active']:
            raise AuthError('Worker account is inactive.',
                            'ACCOUNT_INACTIVE', 403)

        task_id = self.tasks.create(
            worker_id=worker_id,
            assigned_by=admin_user['id'],
            complaint_id=complaint_id,
            status=TASK_ASSIGNED,
        )

        self.complaints.update_status(complaint_id, COMPLAINT_ASSIGNED)
        self.complaints.add_history(
            complaint_id, complaint['status'], COMPLAINT_ASSIGNED,
            admin_user['id'], f'Assigned to worker #{worker_id}'
        )

        # ---- Notifications ----
        try:
            self.notifs.notify_worker_assigned(worker_id, task_id, complaint_id)
        except Exception as e:
            print(f'[WARN] notify failed: {e}')

        # ---- Audit ----
        try:
            self.audit.log_worker_assigned(admin_user['id'], task_id,
                                           worker_id, complaint_id)
        except Exception as e:
            print(f'[WARN] audit failed: {e}')

        return self.tasks.find_by_id(task_id)

    # ====================== WORKER: LIFECYCLE ======================
    def get_my_tasks(self, worker_id, status=None, page=1, page_size=20):
        return self.tasks.list_by_worker(worker_id, status, page, page_size)

    def list_all_tasks(self, **filters):
        return self.tasks.list_all(**filters)

    def get_task_detail(self, task_id, user):
        task = self.tasks.find_by_id(task_id)
        if not task:
            raise AuthError('Task not found.', 'NOT_FOUND', 404)
        if user['role'] == ROLE_WORKER and task['worker_id'] != user['id']:
            raise AuthError('Not allowed to view this task.',
                            'FORBIDDEN', 403)
        task['proofs'] = self.tasks.get_proofs(task_id)
        return task

    def _load_task_for_worker(self, task_id, worker_id):
        task = self.tasks.find_by_id(task_id)
        if not task:
            raise AuthError('Task not found.', 'NOT_FOUND', 404)
        if task['worker_id'] != worker_id:
            raise AuthError('This task is not assigned to you.',
                            'FORBIDDEN', 403)
        return task

    def accept_task(self, task_id, worker_user):
        task = self._load_task_for_worker(task_id, worker_user['id'])
        if task['status'] != TASK_ASSIGNED:
            raise AuthError(
                f'Cannot accept task in status {task["status"]}.',
                'INVALID_STATUS_TRANSITION', 422
            )
        self.tasks.update_status(task_id, TASK_ACCEPTED,
                                 {'accepted_at': utc_now()})
        return self.tasks.find_by_id(task_id)

    def start_task(self, task_id, worker_user):
        task = self._load_task_for_worker(task_id, worker_user['id'])
        if task['status'] != TASK_ACCEPTED:
            raise AuthError(
                f'Cannot start task in status {task["status"]}.',
                'INVALID_STATUS_TRANSITION', 422
            )
        self.tasks.update_status(task_id, TASK_IN_PROGRESS,
                                 {'started_at': utc_now()})

        if task['complaint_id']:
            c = self.complaints.find_by_id(task['complaint_id'])
            if c and c['status'] == COMPLAINT_ASSIGNED:
                self.complaints.update_status(task['complaint_id'], COMPLAINT_IN_PROGRESS)
                self.complaints.add_history(
                    task['complaint_id'], c['status'], COMPLAINT_IN_PROGRESS,
                    worker_user['id'], 'Work started'
                )
                try:
                    self.notifs.notify_task_started(c['citizen_id'], task['complaint_id'])
                except Exception as e:
                    print(f'[WARN] notify failed: {e}')
        return self.tasks.find_by_id(task_id)

    def upload_proof(self, task_id, worker_user, file_storage,
                     upload_root, latitude=None, longitude=None):
        task = self._load_task_for_worker(task_id, worker_user['id'])
        if task['status'] not in (TASK_IN_PROGRESS, TASK_ACCEPTED):
            raise AuthError(
                f'Cannot upload proof in status {task["status"]}.',
                'INVALID_STATUS_TRANSITION', 422
            )

        from backend.utils.file_utils import save_upload
        try:
            info = save_upload(file_storage, 'task_proofs', upload_root)
        except ValueError as e:
            raise AuthError(str(e), 'FILE_INVALID', 422)

        info['latitude']  = latitude
        info['longitude'] = longitude
        self.tasks.add_proof(task_id, worker_user['id'], info)
        return self.tasks.get_proofs(task_id)

    def complete_task(self, task_id, worker_user):
        task = self._load_task_for_worker(task_id, worker_user['id'])
        if task['status'] != TASK_IN_PROGRESS:
            raise AuthError(
                f'Cannot complete task in status {task["status"]}.',
                'INVALID_STATUS_TRANSITION', 422
            )

        proofs = self.tasks.get_proofs(task_id)
        if not proofs:
            raise AuthError('Upload at least one proof before completing.',
                            'VALIDATION_ERROR', 422)

        self.tasks.update_status(task_id, TASK_COMPLETED,
                                 {'completed_at': utc_now()})

        if task['complaint_id']:
            c = self.complaints.find_by_id(task['complaint_id'])
            if c and c['status'] == COMPLAINT_IN_PROGRESS:
                self.complaints.update_status(task['complaint_id'], COMPLAINT_WORKER_COMPLETED)
                self.complaints.add_history(
                    task['complaint_id'], c['status'], COMPLAINT_WORKER_COMPLETED,
                    worker_user['id'], 'Worker completed, awaiting verification'
                )
        return self.tasks.find_by_id(task_id)

    # ====================== ADMIN: VERIFY ======================
    def verify_task(self, task_id, admin_user, approved: bool, reason=None):
        task = self.tasks.find_by_id(task_id)
        if not task:
            raise AuthError('Task not found.', 'NOT_FOUND', 404)
        if task['status'] != TASK_COMPLETED:
            raise AuthError(
                f'Cannot verify task in status {task["status"]}.',
                'INVALID_STATUS_TRANSITION', 422
            )

        if approved:
            self.tasks.update_status(task_id, TASK_VERIFIED,
                                     {'verified_at': utc_now()})
            if task['complaint_id']:
                c = self.complaints.find_by_id(task['complaint_id'])
                if c and c['status'] == COMPLAINT_WORKER_COMPLETED:
                    self.complaints.update_status(
                        task['complaint_id'], COMPLAINT_ADMIN_VERIFIED
                    )
                    self.complaints.add_history(
                        task['complaint_id'], c['status'], COMPLAINT_ADMIN_VERIFIED,
                        admin_user['id'], reason or 'Verified by admin'
                    )
                    self.complaints.update_status(
                        task['complaint_id'], COMPLAINT_CLOSED
                    )
                    self.complaints.add_history(
                        task['complaint_id'], COMPLAINT_ADMIN_VERIFIED, COMPLAINT_CLOSED,
                        admin_user['id'], 'Complaint closed'
                    )

                    # Notifications
                    try:
                        self.notifs.notify_work_verified(task['worker_id'], task_id)
                        self.notifs.notify_complaint_closed(
                            c['citizen_id'], task['complaint_id']
                        )
                    except Exception as e:
                        print(f'[WARN] notify failed: {e}')

                    # ---- Issue SwachhTokens to citizen (idempotent) ----
                    try:
                        from backend.services.token_service import TokenService
                        from backend.config_helper import get_report_reward
                        reward = get_report_reward()
                        TokenService().award_complaint_reward(
                            citizen_id=c['citizen_id'],
                            complaint_id=task['complaint_id'],
                            amount=reward,
                            description=f'Complaint #{task["complaint_id"]} closed'
                        )
                    except Exception as e:
                        print(f'[WARN] token reward failed: {e}')
        else:
            self.tasks.update_status(task_id, TASK_VERIFICATION_FAILED)
            if task['complaint_id']:
                c = self.complaints.find_by_id(task['complaint_id'])
                if c:
                    self.complaints.add_history(
                        task['complaint_id'], c['status'], c['status'],
                        admin_user['id'], reason or 'Verification rejected'
                    )

        # Audit log
        try:
            self.audit.log_task_verified(admin_user['id'], task_id, approved, reason)
        except Exception as e:
            print(f'[WARN] audit failed: {e}')

        return self.tasks.find_by_id(task_id)