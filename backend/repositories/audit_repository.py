"""
Audit log repository. Append-only — no update, no delete.
"""
import json
from backend.utils.db import get_db, utc_now, row_to_dict


class AuditRepository:

    def create(self, actor_user_id, action, entity_type=None, entity_id=None,
               old_value=None, new_value=None, ip_address=None):
        # Serialize dict/list to JSON strings
        def _ser(v):
            if v is None or isinstance(v, str):
                return v
            try:
                return json.dumps(v, default=str)
            except Exception:
                return str(v)

        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO audit_logs
               (actor_user_id, action, entity_type, entity_id,
                old_value, new_value, ip_address, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (actor_user_id, action, entity_type, entity_id,
             _ser(old_value), _ser(new_value), ip_address, now)
        )
        conn.commit()
        aid = cur.lastrowid
        cur.close()
        return aid

    def list_logs(self, entity_type=None, actor_user_id=None,
                  action=None, page=1, page_size=50):
        conn = get_db()
        cur = conn.cursor()

        where = ['1=1']
        params = []
        if entity_type:
            where.append('entity_type = ?')
            params.append(entity_type)
        if actor_user_id:
            where.append('actor_user_id = ?')
            params.append(actor_user_id)
        if action:
            where.append('action = ?')
            params.append(action)

        where_sql = ' AND '.join(where)
        total = cur.execute(
            f'SELECT COUNT(*) AS c FROM audit_logs WHERE {where_sql}', params
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            f'''SELECT a.*, u.email AS actor_email,
                       p.full_name AS actor_name
                FROM audit_logs a
                LEFT JOIN users u ON u.id = a.actor_user_id
                LEFT JOIN profiles p ON p.user_id = a.actor_user_id
                WHERE {where_sql}
                ORDER BY a.created_at DESC, a.id DESC
                LIMIT ? OFFSET ?''',
            params + [page_size, offset]
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    def list_for_entity(self, entity_type, entity_id):
        cur = get_db().cursor()
        rows = cur.execute(
            '''SELECT a.*, u.email AS actor_email,
                      p.full_name AS actor_name
               FROM audit_logs a
               LEFT JOIN users u ON u.id = a.actor_user_id
               LEFT JOIN profiles p ON p.user_id = a.actor_user_id
               WHERE a.entity_type = ? AND a.entity_id = ?
               ORDER BY a.created_at ASC''',
            (entity_type, entity_id)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]