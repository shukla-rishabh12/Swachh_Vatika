"""
Complaint business logic (with notifications + audit hooks).
"""
from backend.repositories.complaint_repository import ComplaintRepository
from backend.services.auth_service import AuthError
from backend.services.notification_service import NotificationService
from backend.services.audit_service import AuditService
from backend.utils.validators import is_valid_category, is_valid_priority
from backend.utils.constants import (
    COMPLAINT_SUBMITTED, COMPLAINT_UNDER_REVIEW, COMPLAINT_VERIFIED,
    COMPLAINT_REJECTED, COMPLAINT_CLOSED, COMPLAINT_TRANSITIONS,
)


class ComplaintService:

    def __init__(self):
        self.repo = ComplaintRepository()
        self.notifs = NotificationService()
        self.audit = AuditService()

    # ====================== CREATE ======================
    def create_complaint(self, citizen_id, data, image_files=None, upload_root='uploads'):
        category    = (data.get('category') or '').strip().upper()
        description = (data.get('description') or '').strip()
        latitude    = data.get('latitude')
        longitude   = data.get('longitude')
        address     = (data.get('address') or '').strip() or None
        ward_id     = data.get('ward_id')
        priority    = (data.get('priority') or 'MEDIUM').strip().upper()

        errors = {}
        ok, msg = is_valid_category(category)
        if not ok:
            errors['category'] = msg
        if not description or len(description) < 5:
            errors['description'] = 'Description must be at least 5 characters.'
        if description and len(description) > 2000:
            errors['description'] = 'Description too long (max 2000 chars).'

        if latitude is not None or longitude is not None:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                if latitude < -90 or latitude > 90:
                    errors['latitude'] = 'Latitude must be between -90 and 90.'
                if longitude < -180 or longitude > 180:
                    errors['longitude'] = 'Longitude must be between -180 and 180.'
            except (TypeError, ValueError):
                errors['latitude'] = 'Invalid coordinates.'
        else:
            latitude = None
            longitude = None

        ok, msg = is_valid_priority(priority)
        if not ok:
            errors['priority'] = msg

        if errors:
            raise AuthError('Validation failed.', 'VALIDATION_ERROR', 422)

        complaint_id = self.repo.create(
            citizen_id=citizen_id, category=category, description=description,
            latitude=latitude, longitude=longitude, address=address,
            ward_id=ward_id, priority=priority, status=COMPLAINT_SUBMITTED,
        )

        if image_files:
            from backend.utils.file_utils import save_upload
            for f in image_files[:5]:
                if not f or not f.filename:
                    continue
                try:
                    info = save_upload(f, 'complaints', upload_root)
                    self.repo.add_image(complaint_id, info)
                except ValueError as e:
                    print(f'[WARN] image skipped: {e}')

        self.repo.add_history(complaint_id, None, COMPLAINT_SUBMITTED,
                              citizen_id, 'Complaint submitted')

        try:
            self.notifs.notify_complaint_submitted(citizen_id, complaint_id)
        except Exception as e:
            print(f'[WARN] notify failed: {e}')

        return self.repo.find_by_id(complaint_id)

    # ====================== READ ======================
    def get_my_complaints(self, citizen_id, status=None, category=None,
                          page=1, page_size=20):
        return self.repo.list_by_citizen(
            citizen_id, status=status, category=category,
            page=page, page_size=page_size
        )

    def get_complaint_detail(self, complaint_id, user):
        c = self.repo.find_by_id(complaint_id)
        if not c:
            raise AuthError('Complaint not found.', 'NOT_FOUND', 404)

        if user['role'] == 'CITIZEN' and c['citizen_id'] != user['id']:
            raise AuthError('Not allowed to view this complaint.',
                            'FORBIDDEN', 403)
        if user['role'] == 'WORKER':
            from backend.utils.db import get_db
            cur = get_db().cursor()
            row = cur.execute(
                'SELECT id FROM tasks WHERE complaint_id = ? AND worker_id = ?',
                (complaint_id, user['id'])
            ).fetchone()
            cur.close()
            if not row:
                raise AuthError('Not allowed to view this complaint.',
                                'FORBIDDEN', 403)

        images = self.repo.get_images(complaint_id)
        history = self.repo.get_history(complaint_id)
        return {**c, 'images': images, 'history': history}

    def list_all_for_admin(self, **filters):
        return self.repo.list_all(**filters)

    # ====================== STATUS TRANSITION ======================
    def change_status(self, complaint_id, new_status, actor_user, reason=None):
        c = self.repo.find_by_id(complaint_id)
        if not c:
            raise AuthError('Complaint not found.', 'NOT_FOUND', 404)

        old_status = c['status']
        allowed = COMPLAINT_TRANSITIONS.get(old_status, set())

        if new_status not in allowed:
            raise AuthError(
                f'Invalid transition from {old_status} to {new_status}.',
                'INVALID_STATUS_TRANSITION', 422
            )

        from backend.utils.db import utc_now
        verified_at = utc_now() if new_status == COMPLAINT_VERIFIED else None
        closed_at   = utc_now() if new_status == COMPLAINT_CLOSED else None

        self.repo.update_status(complaint_id, new_status,
                                verified_at=verified_at, closed_at=closed_at)
        self.repo.add_history(complaint_id, old_status, new_status,
                              actor_user['id'], reason)

        # ---- Notifications ----
        try:
            if new_status == COMPLAINT_VERIFIED:
                self.notifs.notify_complaint_verified(c['citizen_id'], complaint_id)
            elif new_status == COMPLAINT_REJECTED:
                self.notifs.notify_complaint_rejected(c['citizen_id'], complaint_id, reason)
            elif new_status == COMPLAINT_CLOSED:
                self.notifs.notify_complaint_closed(c['citizen_id'], complaint_id)
        except Exception as e:
            print(f'[WARN] notify failed: {e}')

        # ---- Audit log ----
        try:
            if new_status == COMPLAINT_VERIFIED:
                self.audit.log_complaint_verified(actor_user['id'], complaint_id,
                                                  old_status, new_status)
            elif new_status == COMPLAINT_REJECTED:
                self.audit.log_complaint_rejected(actor_user['id'], complaint_id, reason)
        except Exception as e:
            print(f'[WARN] audit failed: {e}')

        return self.repo.find_by_id(complaint_id)

    # ====================== DELETE ======================
    def admin_delete(self, complaint_id, admin_user):
        """Delete a complaint (admin only)."""
        c = self.repo.find_by_id(complaint_id)
        if not c:
            raise AuthError('Complaint not found.', 'NOT_FOUND', 404)

        # Audit before delete
        try:
            self.audit.log(
                admin_user['id'], 'ADMIN_DELETED_COMPLAINT',
                'COMPLAINT', complaint_id,
                old_value={'status': c['status'], 'category': c['category']},
                new_value='DELETED'
            )
        except Exception as e:
            print(f'[WARN] delete audit failed: {e}')

        return self.repo.delete(complaint_id)
        # ====================== VERIFY (auto-chain) ======================
    def verify_complaint_chain(self, complaint_id, admin_user):
        """
        Convenience method: auto-advances through SUBMITTED -> UNDER_REVIEW -> VERIFIED.
        Returns final complaint dict.
        """
        c = self.repo.find_by_id(complaint_id)
        if not c:
            raise AuthError('Complaint not found.', 'NOT_FOUND', 404)

        current = c['status']

        # Already verified
        if current == COMPLAINT_VERIFIED:
            return c

        # Step 1: SUBMITTED -> UNDER_REVIEW
        if current == COMPLAINT_SUBMITTED:
            self.change_status(complaint_id, COMPLAINT_UNDER_REVIEW,
                               admin_user, 'Opened for review')
            current = COMPLAINT_UNDER_REVIEW

        # Step 2: UNDER_REVIEW -> VERIFIED
        if current == COMPLAINT_UNDER_REVIEW:
            return self.change_status(complaint_id, COMPLAINT_VERIFIED,
                                      admin_user, 'Verified by admin')

        # Any other status → reject
        raise AuthError(
            f'Cannot verify from status {current}.',
            'INVALID_STATUS_TRANSITION', 422
        )

    # ====================== REJECT (auto-chain) ======================
    def reject_complaint_chain(self, complaint_id, admin_user, reason):
        c = self.repo.find_by_id(complaint_id)
        if not c:
            raise AuthError('Complaint not found.', 'NOT_FOUND', 404)

        current = c['status']

        if current == COMPLAINT_REJECTED:
            return c

        # Auto-advance to UNDER_REVIEW if needed
        if current == COMPLAINT_SUBMITTED:
            self.change_status(complaint_id, COMPLAINT_UNDER_REVIEW,
                               admin_user, 'Opened for review')
            current = COMPLAINT_UNDER_REVIEW

        if current == COMPLAINT_UNDER_REVIEW:
            return self.change_status(complaint_id, COMPLAINT_REJECTED,
                                      admin_user, reason)

        raise AuthError(
            f'Cannot reject from status {current}.',
            'INVALID_STATUS_TRANSITION', 422
        )