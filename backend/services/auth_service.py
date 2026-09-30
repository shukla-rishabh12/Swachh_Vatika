"""
Authentication business logic.
"""
from backend.repositories.user_repository import UserRepository
from backend.utils.auth import hash_password, verify_password
from backend.utils.validators import (
    is_valid_email, is_valid_password, is_valid_full_name, is_valid_phone
)
from backend.utils.constants import ROLE_CITIZEN


class AuthError(Exception):
    """Raised for auth-related business rule failures."""
    def __init__(self, message, code='AUTH_ERROR', status=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class AuthService:

    def __init__(self):
        self.users = UserRepository()

    # ====================== REGISTER ======================
    def register_citizen(self, data):
        """Register a new CITIZEN. Returns public user dict."""
        full_name = (data.get('full_name') or '').strip()
        email     = (data.get('email') or '').strip().lower()
        password  = data.get('password') or ''
        phone     = (data.get('phone') or '').strip() or None

        # Validate
        errors = {}
        ok, msg = is_valid_full_name(full_name)
        if not ok:
            errors['full_name'] = msg
        ok, msg = is_valid_email(email)
        if not ok:
            errors['email'] = msg
        ok, msg = is_valid_password(password)
        if not ok:
            errors['password'] = msg
        ok, msg = is_valid_phone(phone)
        if not ok:
            errors['phone'] = msg
        if errors:
            raise AuthError('Validation failed.', 'VALIDATION_ERROR', 422)

        # Duplicate email check
        if self.users.email_exists(email):
            raise AuthError('Email is already registered.',
                            'DUPLICATE_RESOURCE', 409)

        # Create user + profile + wallet
        pwd_hash = hash_password(password)
        user_id = self.users.create_user(email, pwd_hash, ROLE_CITIZEN)
        self.users.create_profile(user_id, full_name=full_name, phone=phone)
        self.users.create_wallet(user_id)

        user = self.users.find_by_id(user_id)
        return self._public_user(user)

    # ====================== LOGIN ======================
    def login(self, data):
        email    = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not email or not password:
            raise AuthError('Email and password are required.',
                            'VALIDATION_ERROR', 422)

        user = self.users.find_by_email(email)
        if not user:
            raise AuthError('Invalid email or password.',
                            'INVALID_CREDENTIALS', 401)

        if not verify_password(password, user['password_hash']):
            raise AuthError('Invalid email or password.',
                            'INVALID_CREDENTIALS', 401)

        if not user['is_active']:
            raise AuthError('Your account is inactive. Contact admin.',
                            'ACCOUNT_INACTIVE', 403)

        self.users.update_last_login(user['id'])
        return self._public_user(user)

    # ====================== HELPERS ======================
    @staticmethod
    def _public_user(user):
        """Return safe user fields (never expose password_hash)."""
        return {
            'id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'is_active': bool(user['is_active']),
        }