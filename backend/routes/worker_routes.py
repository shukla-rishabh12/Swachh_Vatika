from flask import Blueprint, request

from backend.services.worker_service import WorkerService
from backend.services.dashboard_service import DashboardService
from backend.services.auth_service import AuthError
from backend.utils.auth import role_required, get_current_user
from backend.utils.constants import ROLE_WORKER, ROLE_ADMIN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


worker_bp = Blueprint('worker_bp', __name__)
service = WorkerService()
dashboard_service = DashboardService()


# ====================== WORKER: DASHBOARD ======================
@worker_bp.route('/dashboard', methods=['GET'])
@role_required(ROLE_WORKER)
def dashboard():
    user = get_current_user()
    data = dashboard_service.worker_dashboard(user['id'])
    return success(data, 'Dashboard loaded.')


# ====================== ADMIN: LIST WORKERS ======================
@worker_bp.route('', methods=['GET'])
@role_required(ROLE_ADMIN)
def list_workers():
    page, page_size = parse_pagination(request.args)
    items, total = service.list_all_workers(page, page_size)
    return paginated(items, page, page_size, total, 'Workers loaded.')


# ====================== ADMIN: WORKER DETAIL ======================
@worker_bp.route('/<int:worker_id>', methods=['GET'])
@role_required(ROLE_ADMIN)
def worker_detail(worker_id):
    try:
        data = service.get_worker_detail(worker_id)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(data, 'Worker loaded.')