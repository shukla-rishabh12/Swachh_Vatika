"""
Verification module — placeholder blueprint.

Actual verification endpoints are implemented under:
  PATCH /api/v1/admin/tasks/<id>/verify

This blueprint exists to keep the module structure per the SRS.
"""
from flask import Blueprint

from backend.utils.auth import login_required
from backend.utils.response import success


verification_bp = Blueprint('verification_bp', __name__)


@verification_bp.route('/status', methods=['GET'])
@login_required
def status():
    return success(
        {
            'message': 'Verification is handled via /api/v1/admin/tasks/<id>/verify',
            'module': 'VERIFICATION',
            'status': 'active',
        },
        'Verification module ready.'
    )