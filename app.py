import os
import subprocess
import sys

from flask import Flask, jsonify, send_from_directory, render_template, request
from flask_cors import CORS

from config import get_config
from backend.utils.db import init_db, close_db, get_db
from backend.utils.logger import setup_logger
from backend.middleware.error_handler import register_error_handlers


BLUEPRINTS = [
    ('backend.routes.auth_routes',         'auth_bp',         '/api/v1/auth'),
    ('backend.routes.citizen_routes',      'citizen_bp',      '/api/v1/citizen'),
    ('backend.routes.user_routes',         'user_bp',         '/api/v1/users'),
    ('backend.routes.complaint_routes',    'complaint_bp',    '/api/v1/complaints'),
    ('backend.routes.pickup_routes',       'pickup_bp',       '/api/v1/pickups'),
    ('backend.routes.worker_routes',       'worker_bp',       '/api/v1/workers'),
    ('backend.routes.task_routes',         'task_bp',         '/api/v1/tasks'),
    ('backend.routes.verification_routes', 'verification_bp', '/api/v1/verification'),
    ('backend.routes.token_routes',        'token_bp',        '/api/v1/tokens'),
    # NOTE: notification_bp is registered DIRECTLY below (bypassing blueprint)
    ('backend.routes.ai_routes',           'ai_bp',           '/api/v1/ai'),
    ('backend.routes.analytics_routes',    'analytics_bp',    '/api/v1/analytics'),
    ('backend.routes.map_routes',          'map_bp',          '/api/v1/map'),
    ('backend.routes.admin_routes',        'admin_bp',        '/api/v1/admin'),
    ('backend.routes.audit_routes',        'audit_bp',        '/api/v1/audit'),
]


def register_blueprints(app):
    """Register only blueprints that currently exist (incremental dev)."""
    for module_name, bp_name, url_prefix in BLUEPRINTS:
        try:
            mod = __import__(module_name, fromlist=[bp_name])
            bp = getattr(mod, bp_name)
            app.register_blueprint(bp, url_prefix=url_prefix)
            app.logger.info(f'[OK]   {bp_name} -> {url_prefix}')
        except (ImportError, AttributeError) as e:
            app.logger.warning(f'[SKIP] {bp_name} ({url_prefix}): {e}')


def register_notification_routes(app):
    """
    Register notification routes DIRECTLY on the app.
    (Blueprint registration was failing due to empty route prefix conflict.)
    """
    from backend.services.notification_service import NotificationService
    from backend.utils.auth import login_required, get_current_user
    from backend.utils.validators import parse_pagination
    from backend.utils.response import success, error, paginated

    def _svc():
        return NotificationService()

    @app.route('/api/v1/notifications', methods=['GET'], strict_slashes=False)
    @login_required
    def _notif_list():
        user = get_current_user()
        page, page_size = parse_pagination(request.args)
        unread_only = request.args.get('unread_only', '').lower() in ('1', 'true', 'yes')
        try:
            items, total = _svc().get_my_notifications(
                user['id'], unread_only=unread_only, page=page, page_size=page_size
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
        return paginated(items, page, page_size, total, 'Notifications loaded.')

    @app.route('/api/v1/notifications/unread-count', methods=['GET'], strict_slashes=False)
    @login_required
    def _notif_unread_count():
        user = get_current_user()
        try:
            count = _svc().get_unread_count(user['id'])
        except Exception as e:
            import traceback
            traceback.print_exc()
            return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
        return success({'unread': count}, 'Unread count loaded.')

    @app.route('/api/v1/notifications/<int:notification_id>/read',
               methods=['POST', 'PATCH'], strict_slashes=False)
    @login_required
    def _notif_mark_read(notification_id):
        user = get_current_user()
        try:
            ok = _svc().mark_read(notification_id, user['id'])
        except Exception as e:
            import traceback
            traceback.print_exc()
            return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
        if not ok:
            return error('Notification not found.', 'NOT_FOUND', 404)
        return success({}, 'Notification marked as read.')

    @app.route('/api/v1/notifications/read-all',
               methods=['POST', 'PATCH'], strict_slashes=False)
    @login_required
    def _notif_mark_all_read():
        user = get_current_user()
        try:
            count = _svc().mark_all_read(user['id'])
        except Exception as e:
            import traceback
            traceback.print_exc()
            return error('Failed: ' + str(e), 'INTERNAL_ERROR', 500)
        return success({'updated': count}, 'All notifications marked as read.')

    app.logger.info('[OK]   notification routes registered directly on app')


def _auto_seed_if_empty(app):
    """
    If the database has zero users, run seed.py automatically.
    This is important for first-time deployment (Render/Fresh install).
    """
    try:
        with app.app_context():
            conn = get_db()
            cur = conn.cursor()
            row = cur.execute('SELECT COUNT(*) FROM users').fetchone()
            user_count = int(row[0]) if row else 0
            cur.close()

            if user_count > 0:
                app.logger.info(f'[INIT] DB already has {user_count} users — skipping seed')
                return

            app.logger.info('[INIT] Empty database detected — running seed.py...')
            seed_path = os.path.join(os.path.dirname(__file__), 'database', 'seed.py')
            if not os.path.exists(seed_path):
                app.logger.warning('[INIT] seed.py not found — skipping auto-seed')
                return

            # Run seed as subprocess to avoid nested app contexts
            result = subprocess.run(
                [sys.executable, seed_path],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.path.dirname(__file__),
            )
            if result.returncode == 0:
                app.logger.info('[INIT] Auto-seed completed successfully')
                if result.stdout:
                    for line in result.stdout.strip().split('\n')[-15:]:
                        app.logger.info(f'[SEED] {line}')
            else:
                app.logger.warning(f'[INIT] Auto-seed failed (rc={result.returncode})')
                if result.stderr:
                    app.logger.warning(f'[SEED-ERR] {result.stderr[:500]}')
    except Exception as e:
        import traceback
        traceback.print_exc()
        app.logger.warning(f'[INIT] Auto-seed skipped: {e}')


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(get_config())

    setup_logger(app)

    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # ---- Ensure required folders exist ----
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'complaints'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'task_proofs'), exist_ok=True)
    db_dir = os.path.dirname(app.config['DATABASE_PATH'])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # ---- Initialize database schema (idempotent) ----
    init_db(app.config['DATABASE_PATH'])
    app.teardown_appcontext(close_db)

    # ---- Auto-seed if empty (first deploy) ----
    _auto_seed_if_empty(app)

    # ---- Register API blueprints ----
    register_blueprints(app)

    # ---- Register notification routes DIRECTLY (bypass blueprint issue) ----
    register_notification_routes(app)

    # ---- Register error handlers ----
    register_error_handlers(app)

    # ---------- Frontend page routes (Jinja-rendered) ----------
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/auth/<path:filename>')
    def auth_pages(filename):
        return render_template(f'auth/{filename}')

    @app.route('/citizen/<path:filename>')
    def citizen_pages(filename):
        return render_template(f'citizen/{filename}')

    @app.route('/worker/<path:filename>')
    def worker_pages(filename):
        return render_template(f'worker/{filename}')

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        return render_template(f'admin/{filename}')

    # ---------- Uploaded files (static serving) ----------
    @app.route('/uploads/<path:filename>')
    def uploaded_files(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ---------- Health check ----------
    @app.route('/health')
    def health():
        return jsonify({'success': True, 'message': 'Swachh-Seva API is running.'})

    return app


# WSGI entry point for gunicorn
# WSGI entry points for gunicorn (both work)
app = create_app()
application = app


if __name__ == '__main__':
    # Local dev server
    port = int(os.getenv('PORT', '5000'))
    application.run(host='0.0.0.0', port=port, debug=True)