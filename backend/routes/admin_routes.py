from flask import Blueprint, request

from backend.services.task_service import TaskService
from backend.services.complaint_service import ComplaintService
from backend.services.token_service import TokenService
from backend.services.dashboard_service import DashboardService
from backend.services.auth_service import AuthError
from backend.utils.auth import role_required, get_current_user
from backend.utils.constants import ROLE_ADMIN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


admin_bp = Blueprint('admin_bp', __name__)

task_service = TaskService()
complaint_service = ComplaintService()
token_service = TokenService()
dashboard_service = DashboardService()


# ====================== DASHBOARD ======================
@admin_bp.route('/dashboard', methods=['GET'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def admin_dashboard():
    data = dashboard_service.admin_dashboard()
    return success(data, 'Admin dashboard loaded.')


# ====================== COMPLAINTS ======================
@admin_bp.route('/complaints', methods=['GET'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def list_complaints():
    page, page_size = parse_pagination(request.args)
    filters = {
        'status':    request.args.get('status') or None,
        'category':  request.args.get('category') or None,
        'priority':  request.args.get('priority') or None,
        'ward_id':   request.args.get('ward_id') or None,
        'page':      page,
        'page_size': page_size,
    }
    try:
        items, total = complaint_service.list_all_for_admin(**filters)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed to load complaints: ' + str(e), 'INTERNAL_ERROR', 500)
    return paginated(items, page, page_size, total, 'Complaints loaded.')


@admin_bp.route('/complaints/<int:complaint_id>', methods=['GET'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def complaint_detail(complaint_id):
    admin = get_current_user()
    try:
        c = complaint_service.get_complaint_detail(complaint_id, admin)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return success(c, 'Complaint loaded.')


@admin_bp.route('/complaints/<int:complaint_id>/status', methods=['PATCH'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def update_complaint_status(complaint_id):
    admin = get_current_user()
    body = request.get_json(silent=True) or {}
    new_status = (body.get('status') or '').strip().upper()
    reason = body.get('reason')

    if not new_status:
        return error('status is required.', 'VALIDATION_ERROR', 422)

    try:
        c = complaint_service.change_status(complaint_id, new_status, admin, reason)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(c, 'Status updated.')


# ====================== VERIFY (single call, auto-chain) ======================
@admin_bp.route('/complaints/<int:complaint_id>/verify', methods=['POST'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def verify_complaint(complaint_id):
    admin = get_current_user()
    try:
        c = complaint_service.verify_complaint_chain(complaint_id, admin)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Verify failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return success(c, 'Complaint verified.')


# ====================== REJECT (single call, auto-chain) ======================
@admin_bp.route('/complaints/<int:complaint_id>/reject', methods=['POST'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def reject_complaint(complaint_id):
    admin = get_current_user()
    body = request.get_json(silent=True) or {}
    reason = body.get('reason') or 'Rejected by admin'
    try:
        c = complaint_service.reject_complaint_chain(complaint_id, admin, reason)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Reject failed: ' + str(e), 'INTERNAL_ERROR', 500)
    return success(c, 'Complaint rejected.')


# ====================== DELETE ======================
@admin_bp.route('/complaints/<int:complaint_id>', methods=['DELETE'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def delete_complaint(complaint_id):
    admin = get_current_user()
    try:
        ok = complaint_service.admin_delete(complaint_id, admin)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error('Delete failed: ' + str(e), 'INTERNAL_ERROR', 500)
    if not ok:
        return error('Delete failed.', 'NOT_FOUND', 404)
    return success({}, 'Complaint deleted.')


# ====================== TASKS ======================
@admin_bp.route('/tasks/assign', methods=['POST'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def assign_task():
    admin = get_current_user()
    body = request.get_json(silent=True) or {}
    complaint_id = body.get('complaint_id')
    worker_id    = body.get('worker_id')
    priority     = body.get('priority')

    if not complaint_id or not worker_id:
        return error('complaint_id and worker_id are required.',
                     'VALIDATION_ERROR', 422)

    try:
        task = task_service.assign_task(int(complaint_id), int(worker_id),
                                        admin, priority)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(task, 'Task assigned.', 201)


@admin_bp.route('/tasks', methods=['GET'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def list_tasks():
    page, page_size = parse_pagination(request.args)
    filters = {
        'status':    request.args.get('status') or None,
        'worker_id': request.args.get('worker_id') or None,
        'page':      page,
        'page_size': page_size,
    }
    items, total = task_service.list_all_tasks(**filters)
    return paginated(items, page, page_size, total, 'Tasks loaded.')


@admin_bp.route('/tasks/<int:task_id>', methods=['GET'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def task_detail(task_id):
    admin = get_current_user()
    try:
        t = task_service.get_task_detail(task_id, admin)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(t, 'Task loaded.')


@admin_bp.route('/tasks/<int:task_id>/verify', methods=['POST'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def verify_task(task_id):
    admin = get_current_user()
    body = request.get_json(silent=True) or {}
    approved = bool(body.get('approved'))
    reason   = body.get('reason')

    try:
        t = task_service.verify_task(task_id, admin, approved, reason)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(t, 'Verification recorded.')


# ====================== TOKENS ======================
@admin_bp.route('/tokens', methods=['GET'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def admin_list_tokens():
    page, page_size = parse_pagination(request.args)
    items, total = token_service.admin_list_wallets(page, page_size)
    stats = token_service.admin_stats()
    return success(
        {
            'stats': stats,
            'wallets': items,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size if page_size else 0,
            },
        },
        'Token data loaded.'
    )


@admin_bp.route('/tokens/adjust', methods=['POST'], strict_slashes=False)
@role_required(ROLE_ADMIN)
def admin_adjust_tokens():
    admin = get_current_user()
    body = request.get_json(silent=True) or {}
    user_id = body.get('user_id')
    amount  = body.get('amount')
    reason  = body.get('description') or body.get('reason')

    if not user_id or amount is None:
        return error('user_id and amount are required.',
                     'VALIDATION_ERROR', 422)

    try:
        user_id = int(user_id)
        amount = int(amount)
    except (TypeError, ValueError):
        return error('user_id and amount must be integers.',
                     'VALIDATION_ERROR', 422)

    try:
        result = token_service.admin_adjust(admin['id'], user_id, amount, reason)
    except AuthError as e:
        return error(e.message, e.code, e.status)

    return success(result, 'Token adjustment recorded.', 201)