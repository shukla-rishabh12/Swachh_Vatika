"""
AI conversations + messages repository.
"""
from backend.utils.db import get_db, utc_now, row_to_dict


class AIRepository:

    # ====================== CONVERSATIONS ======================
    def create_conversation(self, user_id, title='New conversation'):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO ai_conversations (user_id, title, created_at, updated_at)
               VALUES (?, ?, ?, ?)''',
            (user_id, title, now, now)
        )
        conn.commit()
        cid = cur.lastrowid
        cur.close()
        return cid

    def find_conversation(self, conversation_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM ai_conversations WHERE id = ?',
            (conversation_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def list_conversations(self, user_id, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        total = cur.execute(
            'SELECT COUNT(*) AS c FROM ai_conversations WHERE user_id = ?',
            (user_id,)
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            '''SELECT * FROM ai_conversations
               WHERE user_id = ?
               ORDER BY updated_at DESC
               LIMIT ? OFFSET ?''',
            (user_id, page_size, offset)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    def touch_conversation(self, conversation_id):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE ai_conversations SET updated_at = ? WHERE id = ?',
            (now, conversation_id)
        )
        conn.commit()
        cur.close()

    def update_title(self, conversation_id, title):
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE ai_conversations SET title = ? WHERE id = ?',
            (title[:150], conversation_id)
        )
        conn.commit()
        cur.close()

    # ====================== MESSAGES ======================
    def add_message(self, conversation_id, sender_type, message):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO ai_messages
               (conversation_id, sender_type, message, created_at)
               VALUES (?, ?, ?, ?)''',
            (conversation_id, sender_type, message, now)
        )
        conn.commit()
        mid = cur.lastrowid
        cur.close()
        return mid

    def list_messages(self, conversation_id, limit=50):
        cur = get_db().cursor()
        rows = cur.execute(
            '''SELECT * FROM ai_messages
               WHERE conversation_id = ?
               ORDER BY id ASC
               LIMIT ?''',
            (conversation_id, limit)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]