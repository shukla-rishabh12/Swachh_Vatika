from flask import jsonify
from werkzeug.exceptions import HTTPException


def _err(message, code, status):
    return jsonify({
        'success': False,
        'data': None,
        'message': message,
        'error': {'code': code}
    }), status


def register_error_handlers(app):

    @app.errorhandler(400)
    def _400(e):
        return _err('Bad request.', 'BAD_REQUEST', 400)

    @app.errorhandler(401)
    def _401(e):
        return _err('Authentication required.', 'AUTH_REQUIRED', 401)

    @app.errorhandler(403)
    def _403(e):
        return _err('Forbidden.', 'FORBIDDEN', 403)

    @app.errorhandler(404)
    def _404(e):
        return _err('Resource not found.', 'NOT_FOUND', 404)

    @app.errorhandler(405)
    def _405(e):
        return _err('Method not allowed.', 'METHOD_NOT_ALLOWED', 405)

    @app.errorhandler(409)
    def _409(e):
        return _err('Conflict.', 'DUPLICATE_RESOURCE', 409)

    @app.errorhandler(413)
    def _413(e):
        return _err('File too large.', 'FILE_TOO_LARGE', 413)

    @app.errorhandler(422)
    def _422(e):
        return _err('Validation failed.', 'VALIDATION_ERROR', 422)

    @app.errorhandler(500)
    def _500(e):
        app.logger.exception('Internal server error')
        return _err('Internal server error.', 'INTERNAL_ERROR', 500)

    @app.errorhandler(Exception)
    def _unhandled(e):
        if isinstance(e, HTTPException):
            return e
        app.logger.exception('Unhandled exception')
        return _err('An unexpected error occurred.', 'INTERNAL_ERROR', 500)