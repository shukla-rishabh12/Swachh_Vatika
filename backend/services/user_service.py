"""
User profile + admin user management business logic.
"""
from flask import g

from backend.repositories.user_repository import UserRepository
from backend.services.auth_service import AuthError
from backend.utils.constants import ALL_ROLES


class UserService:

    def __init__(self):
        self.users = UserRepository()

    # ====================== PROFILE (SELF) ======================
    def get_my_profile(self, user_id):
        user = self.users.find_by_id(user_id)
        if not user:
            raise AuthError('User not found.', 'NOT_FOUND', 404)

        profile = self.users.get_profile(user_id)
        return {
            'id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'is_active': bool(user['is_active']),
            'created_at': user['created_at'],
            'last_login_at': user.get('last_login_at'),
            'profile': profile or {},
        }

    def update_my_profile(self, user_id, data):
        allowed = ['full_name', 'phone', 'address', 'city', 'ward_id']
        fields = {}

        for k in allowed:
            if k in data:
                v = data.get(k)
                if isinstance(v, str):
                    v = v.strip()
                    if v == '':
                        v = None
                fields[k] = v

        if not fields:
            raise AuthError('No valid fields to update.',
                            'VALIDATION_ERROR', 422)

        if 'full_name' in fields:
            name = fields['full_name']
            if not name or len(name) < 2 or len(name) > 120:
                raise AuthError('Full name must be 2-120 characters.',
                                'VALIDATION_ERROR', 422)

        if 'phone' in fields and fields['phone']:
            phone = str(fields['phone'])
            if not phone.isdigit() or len(phone) != 10:
                raise AuthError('Phone must be 10 digits.',
                                'VALIDATION_ERROR', 422)

        self.users.update_profile(user_id, **fields)
        return self.get_my_profile(user_id)

    # ====================== ADMIN: LIST / DETAIL ======================
    def list_users(self, role=None, is_active=None, search=None,
                   page=1, page_size=20):
        if role and role not in ALL_ROLES:
            raise AuthError('Invalid role filter.', 'VALIDATION_ERROR', 422)

        items, total = self.users.list_users(
            role=role, is_active=is_active, search=search,
            page=page, page_size=page_size
        )

        for it in items:
            it.pop('password_hash', None)

        return items, total

    def get_user_detail(self, user_id):
        user = self.users.find_by_id(user_id)
        if not user:
            raise AuthError('User not found.', 'NOT_FOUND', 404)

        profile = self.users.get_profile(user_id)
        wallet = self.users.get_wallet(user_id)

        return {
            'id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'is_active': bool(user['is_active']),
            'created_at': user['created_at'],
            'last_login_at': user.get('last_login_at'),
            'profile': profile or {},
            'wallet': wallet or {},
        }

    # ====================== ADMIN: ACTIVATE/DEACTIVATE ======================
    def set_user_status(self, user_id, is_active):
        user = self.users.find_by_id(user_id)
        if not user:
            raise AuthError('User not found.', 'NOT_FOUND', 404)

        actor = None
        try:
            actor = getattr(g, 'current_user', None)
        except Exception:
            actor = None

        if actor and actor['id'] == user_id and not is_active:
            raise AuthError('You cannot deactivate your own account.',
                            'VALIDATION_ERROR', 422)

        old_status = bool(user['is_active'])
        self.users.update_status(user_id, is_active)

        try:
            from backend.services.audit_service import AuditService
            actor_id = actor['id'] if actor else None
            AuditService().log_user_status_changed(
                actor_id, user_id, old_status, bool(is_active)
            )
        except Exception as e:
            print(f'[WARN] audit failed: {e}')

        return {'id': user_id, 'is_active': bool(is_active)}