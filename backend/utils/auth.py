"""
Password hashing and session helpers.
Passwords are NEVER stored in plaintext — always via Werkzeug hash.
"""
from functools import wraps
from flask import session, g
from werkzeug.security import generate_password_hash, check_password_hash


# ====================== PASSWORD ======================
def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password, method='pbkdf2:sha256')


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not plain_password or not password_hash:
        return False
    try:
        return check_password_hash(password_hash, plain_password)
    except Exception:
        return False


# ====================== SESSION ======================
def set_session(user):
    """Store minimal identity in session."""
    session.clear()
    session['user_id'] = user['id']
    session['role'] = user['role']
    session.permanent = True


def clear_session():
    session.clear()


def get_session_user_id():
    return session.get('user_id')


def get_session_role():
    return session.get('role')


def is_authenticated():
    return get_session_user_id() is not None


# ====================== CURRENT USER CACHE ======================
def load_current_user():
    """
    Load the current user from DB (once per request) and cache it on g.
    Returns dict or None.
    """
    if hasattr(g, 'current_user'):
        return g.current_user

    user_id = get_session_user_id()
    if not user_id:
        g.current_user = None
        return None

    # Import here to avoid circular imports
    from backend.repositories.user_repository import UserRepository
    repo = UserRepository()
    user = repo.find_by_id(user_id)
    if user and user.get('is_active'):
        g.current_user = user
    else:
        g.current_user = None
    return g.current_user


def get_current_user():
    return load_current_user()


# ====================== DECORATORS ======================
def login_required(fn):
    """Ensure a logged-in active user. Attaches user to g.current_user."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = load_current_user()
        if not user:
            from backend.utils.response import error
            from backend.utils.constants import ERR_AUTH_REQUIRED
            return error('Authentication required.', ERR_AUTH_REQUIRED, 401)
        return fn(*args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """Ensure the current user has one of the allowed roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from backend.utils.response import error
            from backend.utils.constants import ERR_AUTH_REQUIRED, ERR_FORBIDDEN

            user = load_current_user()
            if not user:
                return error('Authentication required.', ERR_AUTH_REQUIRED, 401)
            if user['role'] not in allowed_roles:
                return error('You are not allowed to perform this action.',
                             ERR_FORBIDDEN, 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator