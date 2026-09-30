"""
Notification repository. All SQL for notifications table.
"""
from backend.utils.db import get_db, utc_now, row_to_dict


class NotificationRepository:

    def create(self, user_id, type_, title, message,
               related_entity_type=None, related_entity_id=None):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO notifications
               (user_id, type, title, message,
                related_entity_type, related_entity_id, is_read, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 0, ?)''',
            (user_id, type_, title, message,
             related_entity_type, related_entity_id, now)
        )
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        return nid

    def list_for_user(self, user_id, unread_only=False,
                      page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['user_id = ?']
        params = [user_id]
        if unread_only:
            where.append('is_read = 0')

        where_sql = ' AND '.join(where)
        count_row = cur.execute(
            f'SELECT COUNT(*) FROM notifications WHERE {where_sql}',
            params
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        offset = max(0, (page - 1) * page_size)
        rows = cur.execute(
            f'''SELECT * FROM notifications
                WHERE {where_sql}
                ORDER BY id DESC
                LIMIT ? OFFSET ?''',
            params + [int(page_size), offset]
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    def unread_count(self, user_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()
        cur.close()
        return int(row[0]) if row else 0

    def mark_read(self, notification_id, user_id):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?',
            (notification_id, user_id)
        )
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0

    def mark_all_read(self, user_id):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0',
            (user_id,)
        )
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected