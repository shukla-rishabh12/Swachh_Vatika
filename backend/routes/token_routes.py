from flask import Blueprint, request

from backend.services.token_service import TokenService
from backend.services.auth_service import AuthError
from backend.utils.auth import login_required, get_current_user
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


token_bp = Blueprint('token_bp', __name__)
service = TokenService()


@token_bp.route('/wallet', methods=['GET'])
@login_required
def my_wallet():
    user = get_current_user()
    wallet = service.get_my_wallet(user['id'])
    return success(wallet, 'Wallet loaded.')


@token_bp.route('/transactions', methods=['GET'])
@login_required
def my_transactions():
    user = get_current_user()
    page, page_size = parse_pagination(request.args)
    tx_type = request.args.get('type')

    try:
        items, total = service.get_my_transactions(
            user['id'], transaction_type=tx_type,
            page=page, page_size=page_size
        )
    except AuthError as e:
        return error(e.message, e.code, e.status)

    return paginated(items, page, page_size, total, 'Transactions loaded.')