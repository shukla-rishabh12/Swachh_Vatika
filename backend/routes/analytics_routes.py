from flask import Blueprint, request

from backend.services.analytics_service import AnalyticsService
from backend.utils.auth import role_required
from backend.utils.constants import ROLE_ADMIN
from backend.utils.response import success


analytics_bp = Blueprint('analytics_bp', __name__)
service = AnalyticsService()


@analytics_bp.route('/summary', methods=['GET'])
@role_required(ROLE_ADMIN)
def summary():
    return success(service.get_summary(), 'Summary loaded.')


@analytics_bp.route('/complaints', methods=['GET'])
@role_required(ROLE_ADMIN)
def complaints_breakdown():
    data = {
        'by_status':   service.complaints_by_status(),
        'by_category': service.complaints_by_category(),
        'by_priority': service.complaints_by_priority(),
        'by_ward':     service.complaints_by_ward(),
        'by_date':     service.complaints_by_date(days=30),
        'resolution':  service.resolution_stats(),
    }
    return success(data, 'Complaint analytics loaded.')


@analytics_bp.route('/workers', methods=['GET'])
@role_required(ROLE_ADMIN)
def workers_breakdown():
    return success(service.worker_performance(), 'Worker performance loaded.')


@analytics_bp.route('/tokens', methods=['GET'])
@role_required(ROLE_ADMIN)
def tokens_breakdown():
    return success(service.token_trend(days=30), 'Token trend loaded.')