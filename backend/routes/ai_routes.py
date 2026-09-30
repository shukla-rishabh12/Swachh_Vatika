from flask import Blueprint, request

from backend.services.ai_service import AIService
from backend.services.auth_service import AuthError
from backend.utils.auth import login_required, get_current_user
from backend.utils.validators import parse_pagination
from backend.utils.response import success, error, paginated


ai_bp = Blueprint('ai_bp', __name__)
service = AIService()


@ai_bp.route('/conversations', methods=['POST'])
@login_required
def create_conversation():
    user = get_current_user()
    body = request.get_json(silent=True) or {}
    title = body.get('title') or 'New conversation'
    cid = service.create_conversation(user['id'], title)
    return success({'conversation_id': cid}, 'Conversation created.', 201)


@ai_bp.route('/conversations', methods=['GET'])
@login_required
def list_conversations():
    user = get_current_user()
    page, page_size = parse_pagination(request.args)
    items, total = service.list_conversations(user['id'], page, page_size)
    return paginated(items, page, page_size, total, 'Conversations loaded.')


@ai_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    user = get_current_user()
    try:
        msgs = service.get_messages(conversation_id, user)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    return success(msgs, 'Messages loaded.')


@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    user = get_current_user()
    body = request.get_json(silent=True) or {}
    conversation_id = body.get('conversation_id')
    message = body.get('message')

    if not conversation_id:
        try:
            conversation_id = service.create_conversation(user['id'])
        except Exception:
            return error('Could not start conversation.',
                         'INTERNAL_ERROR', 500)

    try:
        conversation_id = int(conversation_id)
        result = service.chat(user, conversation_id, message)
    except AuthError as e:
        return error(e.message, e.code, e.status)
    except ValueError:
        return error('conversation_id must be an integer.',
                     'VALIDATION_ERROR', 422)

    return success(result, 'AI response generated successfully.')