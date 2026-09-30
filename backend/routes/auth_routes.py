from flask import Blueprint, request

from backend.services.auth_service import AuthService, AuthError
from backend.utils.auth import set_session, clear_session, load_current_user
from backend.utils.response import success, error


auth_bp = Blueprint('auth_bp', __name__)
auth_service = AuthService()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = auth_service.register_citizen(data)
    except AuthError as e:
        return error(e.message, e.code, e.status)

    set_session(user)
    return success({'user': user}, 'Registration successful.', 201)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = auth_service.login(data)
    except AuthError as e:
        return error(e.message, e.code, e.status)

    set_session(user)
    return success({'user': user}, 'Login successful.', 200)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    clear_session()
    return success({}, 'Logged out successfully.', 200)


@auth_bp.route('/me', methods=['GET'])
def me():
    user = load_current_user()
    if not user:
        return error('Authentication required.', 'AUTH_REQUIRED', 401)
    return success({
        'user': {
            'id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'is_active': bool(user['is_active']),
        }
    }, 'Current user loaded.')