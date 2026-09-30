"""
Notification service.
"""
from backend.repositories.notification_repository import NotificationRepository
from backend.utils.constants import (
    NOTIF_COMPLAINT_SUBMITTED, NOTIF_COMPLAINT_VERIFIED,
    NOTIF_COMPLAINT_REJECTED, NOTIF_WORKER_ASSIGNED,
    NOTIF_TASK_STARTED, NOTIF_TASK_COMPLETED,
    NOTIF_WORK_VERIFIED, NOTIF_COMPLAINT_CLOSED,
    NOTIF_TOKENS_CREDITED, NOTIF_PICKUP_UPDATED,
)


class NotificationService:

    def __init__(self):
        self.repo = NotificationRepository()

    # ====================== READ ======================
    def get_my_notifications(self, user_id, unread_only=False,
                             page=1, page_size=20):
        return self.repo.list_for_user(user_id, unread_only, page, page_size)

    def get_unread_count(self, user_id):
        return self.repo.unread_count(user_id)

    def mark_read(self, notification_id, user_id):
        return self.repo.mark_read(notification_id, user_id)

    def mark_all_read(self, user_id):
        return self.repo.mark_all_read(user_id)

    # ====================== HIGH-LEVEL HELPERS ======================
    def notify_complaint_submitted(self, citizen_id, complaint_id):
        return self.repo.create(
            citizen_id, NOTIF_COMPLAINT_SUBMITTED,
            'Complaint submitted',
            f'Your complaint #{complaint_id} has been submitted for review.',
            'COMPLAINT', complaint_id
        )

    def notify_complaint_verified(self, citizen_id, complaint_id):
        return self.repo.create(
            citizen_id, NOTIF_COMPLAINT_VERIFIED,
            'Complaint verified',
            f'Your complaint #{complaint_id} has been verified.',
            'COMPLAINT', complaint_id
        )

    def notify_complaint_rejected(self, citizen_id, complaint_id, reason=None):
        msg = f'Your complaint #{complaint_id} was rejected.'
        if reason:
            msg += f' Reason: {reason}'
        return self.repo.create(
            citizen_id, NOTIF_COMPLAINT_REJECTED,
            'Complaint rejected', msg,
            'COMPLAINT', complaint_id
        )

    def notify_worker_assigned(self, worker_id, task_id, complaint_id):
        return self.repo.create(
            worker_id, NOTIF_WORKER_ASSIGNED,
            'New task assigned',
            f'Task #{task_id} for complaint #{complaint_id} assigned to you.',
            'TASK', task_id
        )

    def notify_task_started(self, citizen_id, complaint_id):
        return self.repo.create(
            citizen_id, NOTIF_TASK_STARTED,
            'Work started',
            f'Worker has started work on complaint #{complaint_id}.',
            'COMPLAINT', complaint_id
        )

    def notify_task_completed(self, admin_id, task_id):
        return self.repo.create(
            admin_id, NOTIF_TASK_COMPLETED,
            'Task completed',
            f'Task #{task_id} has been completed and awaits verification.',
            'TASK', task_id
        )

    def notify_work_verified(self, worker_id, task_id):
        return self.repo.create(
            worker_id, NOTIF_WORK_VERIFIED,
            'Work verified',
            f'Your work on task #{task_id} has been verified.',
            'TASK', task_id
        )

    def notify_complaint_closed(self, citizen_id, complaint_id):
        return self.repo.create(
            citizen_id, NOTIF_COMPLAINT_CLOSED,
            'Complaint closed',
            f'Your complaint #{complaint_id} has been closed.',
            'COMPLAINT', complaint_id
        )

    def notify_tokens_credited(self, citizen_id, amount, description):
        return self.repo.create(
            citizen_id, NOTIF_TOKENS_CREDITED,
            f'+{amount} SwachhTokens credited',
            description or f'You earned {amount} SwachhTokens.',
            None, None
        )

    def notify_pickup_updated(self, citizen_id, pickup_id, status):
        return self.repo.create(
            citizen_id, NOTIF_PICKUP_UPDATED,
            'Pickup request updated',
            f'Your pickup request #{pickup_id} status: {status}.',
            'PICKUP', pickup_id
        )