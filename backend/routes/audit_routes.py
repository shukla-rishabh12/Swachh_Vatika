from flask import Blueprint, request

from backend.services.audit_service import AuditService
from backend.utils.auth import role_required
from backend.utils.constants import ROLE_ADMIN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, paginated


audit_bp = Blueprint('audit_bp', __name__)
service = AuditService()


@audit_bp.route('', methods=['GET'])
@role_required(ROLE_ADMIN)
def list_audit_logs():
    page, page_size = parse_pagination(request.args)
    filters = {
        'entity_type':   request.args.get('entity_type'),
        'actor_user_id': request.args.get('actor_user_id'),
        'action':        request.args.get('action'),
        'page':          page,
        'page_size':     page_size,
    }
    # actor_user_id comes as string from query — cast
    if filters['actor_user_id']:
        try:
            filters['actor_user_id'] = int(filters['actor_user_id'])
        except (TypeError, ValueError):
            filters['actor_user_id'] = None

    items, total = service.list_logs(**filters)
    return paginated(items, page, page_size, total, 'Audit logs loaded.')