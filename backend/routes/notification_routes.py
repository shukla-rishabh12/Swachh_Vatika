from flask import Blueprint, request

from backend.services.notification_service import NotificationService
from backend.utils.auth import login_required, get_current_user
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


notification_bp = Blueprint('notification_bp', __name__)


def _svc():
    return NotificationService()


# ====================== LIST ======================
@notification_bp.route('/notifications', methods=['GET'], strict_slashes=False)
@login_required
def list_notifications():
    user = get_current_user()
    page, page_size = parse_pagination(request.args)
    unread_only = request.args.get('unread_only', '').lower() in ('1', 'true', 'yes')

    try:
        items, total = _svc().get_my_notifications(
            user['id'], unread_only=unread_only, page=page, page_size=page_size
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return paginated(items, page, page_size, total, 'Notifications loaded.')


# ====================== UNREAD COUNT ======================
@notification_bp.route('/notifications/unread-count', methods=['GET'], strict_slashes=False)
@login_required
def unread_count():
    user = get_current_user()
    try:
        count = _svc().get_unread_count(user['id'])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return success({'unread': count}, 'Unread count loaded.')


# ====================== MARK ONE READ ======================
@notification_bp.route('/notifications/<int:notification_id>/read', methods=['POST', 'PATCH'], strict_slashes=False)
@login_required
def mark_read(notification_id):
    user = get_current_user()
    try:
        ok = _svc().mark_read(notification_id, user['id'])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
    if not ok:
        return error('Notification not found.', 'NOT_FOUND', 404)
    return success({}, 'Notification marked as read.')


# ====================== MARK ALL READ ======================
@notification_bp.route('/notifications/read-all', methods=['POST', 'PATCH'], strict_slashes=False)
@login_required
def mark_all_read():
    user = get_current_user()
    try:
        count = _svc().mark_all_read(user['id'])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return success({'updated': count}, 'All notifications marked as read.')