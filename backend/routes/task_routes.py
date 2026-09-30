from flask import Blueprint, request, current_app

from backend.services.task_service import TaskService
from backend.services.auth_service import AuthError
from backend.utils.auth import role_required, login_required, get_current_user
from backend.utils.constants import ROLE_WORKER, ROLE_ADMIN
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


task_bp = Blueprint('task_bp', __name__)
service = TaskService()


# ====================== WORKER: MY TASKS ======================
@task_bp.route('/my', methods=['GET'])
@role_required(ROLE_WORKER)
def my_tasks():
    user = get_current_user()
    page, page_size = parse_pagination(request.args)
    status = request.args.get('status')
    items, total = service.get_my_tasks(user['id'], status, page, page_size)
    return paginated(items, page, page_size, total, 'Tasks loaded.')


# ====================== DETAIL ======================
@task_bp.route('/<int:task_id>', methods=['GET'])
@login_required
def task_detail(task_id):
    user = get_current_user()
    try:
        t = service.get_task_detail(task_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(t, 'Task loaded.')


# ====================== WORKER: LIFECYCLE ======================
@task_bp.route('/<int:task_id>/accept', methods=['POST'])
@role_required(ROLE_WORKER)
def accept_task(task_id):
    user = get_current_user()
    try:
        t = service.accept_task(task_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(t, 'Task accepted.')


@task_bp.route('/<int:task_id>/start', methods=['POST'])
@role_required(ROLE_WORKER)
def start_task(task_id):
    user = get_current_user()
    try:
        t = service.start_task(task_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(t, 'Task started.')


@task_bp.route('/<int:task_id>/proof', methods=['POST'])
@role_required(ROLE_WORKER)
def upload_proof(task_id):
    user = get_current_user()

    if 'image' not in request.files:
        return error('No file provided (field name must be "image").',
                     'VALIDATION_ERROR', 422)

    file = request.files['image']
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    try:
        lat = float(latitude) if latitude not in (None, '') else None
        lng = float(longitude) if longitude not in (None, '') else None
    except (TypeError, ValueError):
        lat = lng = None

    try:
        proofs = service.upload_proof(
            task_id, user, file,
            upload_root=current_app.config['UPLOAD_FOLDER'],
            latitude=lat, longitude=lng
        )
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(proofs, 'Proof uploaded.', 201)


@task_bp.route('/<int:task_id>/complete', methods=['POST'])
@role_required(ROLE_WORKER)
def complete_task(task_id):
    user = get_current_user()
    try:
        t = service.complete_task(task_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(t, 'Task marked complete.')