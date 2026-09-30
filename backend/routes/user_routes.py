from flask import Blueprint, request

from backend.services.user_service import UserService
from backend.services.auth_service import AuthError
from backend.utils.auth import login_required, role_required, get_current_user
from backend.utils.constants import ROLE_ADMIN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


user_bp = Blueprint('user_bp', __name__)
user_service = UserService()


# ====================== MY PROFILE ======================
@user_bp.route('/me', methods=['GET'])
@login_required
def get_me():
    user = get_current_user()
    try:
        data = user_service.get_my_profile(user['id'])
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(data, 'Profile loaded.')


@user_bp.route('/me', methods=['PATCH'])
@login_required
def update_me():
    user = get_current_user()
    body = request.get_json(silent=True) or {}
    try:
        data = user_service.update_my_profile(user['id'], body)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(data, 'Profile updated.')


# ====================== ADMIN: LIST USERS ======================
@user_bp.route('', methods=['GET'])
@role_required(ROLE_ADMIN)
def list_users():
    page, page_size = parse_pagination(request.args)
    role = request.args.get('role') or None
    is_active_raw = request.args.get('is_active')
    search = request.args.get('search')

    is_active = None
    if is_active_raw is not None and is_active_raw != '':
        is_active = is_active_raw.lower() in ('1', 'true', 'yes')

    try:
        items, total = user_service.list_users(
            role=role, is_active=is_active, search=search,
            page=page, page_size=page_size
        )
    except AuthError as e:
        return error(e.message, e.code, e.status)

    return paginated(items, page, page_size, total, 'Users loaded.')


# ====================== ADMIN: USER DETAIL ======================
@user_bp.route('/<int:user_id>', methods=['GET'])
@role_required(ROLE_ADMIN)
def get_user(user_id):
    try:
        data = user_service.get_user_detail(user_id)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(data, 'User loaded.')


# ====================== ADMIN: ACTIVATE/DEACTIVATE ======================
@user_bp.route('/<int:user_id>/status', methods=['PATCH', 'POST'])
@role_required(ROLE_ADMIN)
def set_status(user_id):
    body = request.get_json(silent=True) or {}
    is_active = bool(body.get('is_active'))
    try:
        data = user_service.set_user_status(user_id, is_active)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return success(data, 'User status updated.')