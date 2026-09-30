"""
Standard API response formatter.
Every API response must follow this shape.
"""
from flask import jsonify


def success(data=None, message='Operation successful.', status=200):
    return jsonify({
        'success': True,
        'data': data if data is not None else {},
        'message': message,
    }), status


def error(message='Something went wrong.', code='INTERNAL_ERROR',
          status=400, details=None):
    body = {
        'success': False,
        'data': None,
        'message': message,
        'error': {'code': code},
    }
    if details is not None:
        body['error']['details'] = details
    return jsonify(body), status


def validation_error(errors, message='Validation failed.'):
    return jsonify({
        'success': False,
        'data': None,
        'message': message,
        'error': {
            'code': 'VALIDATION_ERROR',
            'details': errors,
        },
    }), 422


def paginated(items, page, page_size, total, message='Operation successful.'):
    return jsonify({
        'success': True,
        'data': {
            'items': items,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size if page_size else 0,
            },
        },
        'message': message,
    }), 200