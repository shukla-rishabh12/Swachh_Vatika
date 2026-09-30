from flask import Blueprint, request

from backend.services.pickup_service import PickupService
from backend.services.auth_service import AuthError
from backend.utils.auth import role_required, login_required, get_current_user
from backend.utils.constants import ROLE_CITIZEN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


pickup_bp = Blueprint('pickup_bp', __name__)
service = PickupService()


@pickup_bp.route('', methods=['POST'], strict_slashes=False)
@pickup_bp.route('/', methods=['POST'], strict_slashes=False)
@role_required(ROLE_CITIZEN)
def create_pickup():
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    try:
        p = service.create_pickup(user['id'], data)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Unexpected error: ' + str(e), 'INTERNAL_ERROR', 500)

    return success(
        {'pickup_id': p['id'], 'status': p['status']},
        'Pickup request submitted.', 201
    )


@pickup_bp.route('/my', methods=['GET'], strict_slashes=False)
@role_required(ROLE_CITIZEN)
def my_pickups():
    user = get_current_user()
    page, page_size = parse_pagination(request.args)
    try:
        items, total = service.get_my_pickups(user['id'], page, page_size)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Unexpected error: ' + str(e), 'INTERNAL_ERROR', 500)
    return paginated(items, page, page_size, total, 'Pickups loaded.')


@pickup_bp.route('/<int:pickup_id>', methods=['GET'], strict_slashes=False)
@login_required
def pickup_detail(pickup_id):
    user = get_current_user()
    try:
        p = service.get_pickup_detail(pickup_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(p, 'Pickup loaded.')