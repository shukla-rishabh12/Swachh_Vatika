from flask import Blueprint, request, current_app

from backend.services.complaint_service import ComplaintService
from backend.services.auth_service import AuthError
from backend.utils.auth import login_required, role_required, get_current_user
from backend.utils.constants import ROLE_CITIZEN, ROLE_ADMIN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


complaint_bp = Blueprint('complaint_bp', __name__)
service = ComplaintService()


@complaint_bp.route('', methods=['POST'])
@role_required(ROLE_CITIZEN)
def create_complaint():
    user = get_current_user()

    # multipart/form-data OR JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
        images = request.files.getlist('image') + request.files.getlist('image[]')
    else:
        data = request.get_json(silent=True) or {}
        images = []

    try:
        c = service.create_complaint(
            user['id'], data, image_files=images,
            upload_root=current_app.config['UPLOAD_FOLDER']
        )
    except AuthError as e:
        return error(e.message, e.code, e.status)

    return success(
        {'complaint_id': c['id'], 'status': c['status']},
        'Complaint submitted successfully.', 201
    )


@complaint_bp.route('/my', methods=['GET'])
@role_required(ROLE_CITIZEN)
def my_complaints():
    user = get_current_user()
    page, page_size = parse_pagination(request.args)
    status = request.args.get('status')
    category = request.args.get('category')

    items, total = service.get_my_complaints(
        user['id'], status=status, category=category,
        page=page, page_size=page_size
    )
    return paginated(items, page, page_size, total, 'Complaints loaded.')


@complaint_bp.route('/<int:complaint_id>', methods=['GET'])
@login_required
def complaint_detail(complaint_id):
    user = get_current_user()
    try:
        c = service.get_complaint_detail(complaint_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(c, 'Complaint loaded.')