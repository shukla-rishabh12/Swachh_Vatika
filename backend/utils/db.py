import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from flask import g, current_app


def _default_db_path():
    return os.getenv('DATABASE_PATH', 'database/swachh_seva.db')


def get_db_path():
    try:
        return current_app.config['DATABASE_PATH']
    except RuntimeError:
        return _default_db_path()


def get_connection():
    """Create a fresh SQLite connection with FK + WAL enabled."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    return conn


def get_db():
    """Request-scoped connection (reused within one request)."""
    if 'db' not in g:
        g.db = get_connection()
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


@contextmanager
def db_cursor(commit=False):
    """Cursor context manager."""
    conn = get_db()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


@contextmanager
def transaction():
    """Full transaction wrapper. Commits on success, rolls back on error."""
    conn = get_db()
    try:
        with conn:
            yield conn
    except Exception:
        raise


def init_db(db_path):
    """Initialize schema from database/schema.sql (idempotent)."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    schema_path = os.path.join(root, 'database', 'schema.sql')
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f'Schema not found: {schema_path}')

    conn = sqlite3.connect(db_path)
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row):
    return dict(row) if row is not None else None


def rows_to_list(rows):
    return [dict(r) for r in rows]


def utc_now():
    """Current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')