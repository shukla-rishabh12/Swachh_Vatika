"""
Helper to read business settings from DB (system_settings table)
with fallback to config defaults.
"""
from flask import current_app
from backend.utils.db import get_db


def _get_setting(key, default=None):
    """Read a raw setting_value (string) from DB. Returns None on error/miss."""
    try:
        conn = get_db()
        cur = conn.cursor()
        row = cur.execute(
            'SELECT setting_value FROM system_settings WHERE setting_key = ?',
            (key,)
        ).fetchone()
        cur.close()
        if row:
            return row['setting_value']
    except Exception:
        pass
    return default


def _get_int_setting(key, fallback):
    val = _get_setting(key, None)
    if val is not None:
        try:
            return int(val)
        except (TypeError, ValueError):
            pass
    return fallback


def get_report_reward():
    """REPORT_REWARD default from config, override from DB if set."""
    try:
        default = current_app.config.get('DEFAULT_REPORT_REWARD', 5)
    except RuntimeError:
        default = 5
    return _get_int_setting('REPORT_REWARD', default)


def get_pickup_reward():
    try:
        default = current_app.config.get('DEFAULT_PICKUP_REWARD', 3)
    except RuntimeError:
        default = 3
    return _get_int_setting('PICKUP_REWARD', default)


def get_max_upload_mb():
    try:
        default = current_app.config.get('MAX_UPLOAD_SIZE_MB', 5)
    except RuntimeError:
        default = 5
    return _get_int_setting('MAX_IMAGE_SIZE_MB', default)


def get_duplicate_window_hours():
    return _get_int_setting('DUPLICATE_WINDOW_HOURS', 24)


def get_max_chat_message_length():
    return _get_int_setting('MAX_CHAT_MESSAGE_LENGTH', 1000)