from flask import Blueprint

from backend.services.dashboard_service import DashboardService
from backend.utils.auth import role_required, get_current_user
from backend.utils.constants import ROLE_CITIZEN
from backend.utils.response import success


citizen_bp = Blueprint('citizen_bp', __name__)
service = DashboardService()


@citizen_bp.route('/dashboard', methods=['GET'])
@role_required(ROLE_CITIZEN)
def dashboard():
    user = get_current_user()
    data = service.citizen_dashboard(user['id'])
    return success(data, 'Dashboard loaded.')