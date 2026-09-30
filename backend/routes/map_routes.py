from flask import Blueprint, request

from backend.services.map_service import MapService
from backend.utils.auth import role_required
from backend.utils.constants import ROLE_ADMIN
from backend.utils.response import success


map_bp = Blueprint('map_bp', __name__)
service = MapService()


@map_bp.route('/complaints', methods=['GET'])
@role_required(ROLE_ADMIN)
def complaints_map():
    status = request.args.get('status')
    category = request.args.get('category')
    data = service.get_complaints_map(status=status, category=category)
    return success(data, 'Complaint map data loaded.')


@map_bp.route('/hotspots', methods=['GET'])
@role_required(ROLE_ADMIN)
def hotspots():
    try:
        min_count = int(request.args.get('min_count', 2))
    except (TypeError, ValueError):
        min_count = 2
    data = service.get_hotspots(min_count=min_count)
    return success(data, 'Hotspots loaded.')


@map_bp.route('/ward-hotspots', methods=['GET'])
@role_required(ROLE_ADMIN)
def ward_hotspots():
    return success(service.get_ward_hotspots(), 'Ward hotspots loaded.')