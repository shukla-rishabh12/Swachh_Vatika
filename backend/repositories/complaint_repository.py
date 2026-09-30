"""
Complaint repository. All SQL for complaints + complaint_images + history.
"""
from backend.utils.db import get_db, utc_now, row_to_dict


class ComplaintRepository:

    # ====================== CREATE ======================
    def create(self, citizen_id, category, description, latitude, longitude,
               address, ward_id, priority='MEDIUM', status='SUBMITTED',
               ai_category=None, ai_priority=None):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO complaints
               (citizen_id, category, description, latitude, longitude,
                address, ward_id, priority, status,
                ai_category_suggestion, ai_priority_suggestion,
                duplicate_status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NOT_CHECKED', ?, ?)''',
            (citizen_id, category, description, latitude, longitude,
             address, ward_id, priority, status,
             ai_category, ai_priority, now, now)
        )
        conn.commit()
        cid = cur.lastrowid
        cur.close()
        return cid

    # ====================== READ ======================
    def find_by_id(self, complaint_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM complaints WHERE id = ?', (complaint_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def list_by_citizen(self, citizen_id, status=None, category=None,
                        page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['citizen_id = ?']
        params = [citizen_id]

        if status:
            where.append('status = ?')
            params.append(status)
        if category:
            where.append('category = ?')
            params.append(category)

        where_sql = ' AND '.join(where)
        count_row = cur.execute(
            f'SELECT COUNT(*) FROM complaints WHERE {where_sql}', params
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        offset = max(0, (page - 1) * page_size)
        rows = cur.execute(
            f'''SELECT * FROM complaints
                WHERE {where_sql}
                ORDER BY id DESC
                LIMIT ? OFFSET ?''',
            params + [int(page_size), offset]
        ).fetchall()

        cur.close()
        return [row_to_dict(r) for r in rows], total

    def list_all(self, status=None, category=None, priority=None,
                 ward_id=None, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['1=1']
        params = []

        if status:
            where.append('c.status = ?')
            params.append(status)
        if category:
            where.append('c.category = ?')
            params.append(category)
        if priority:
            where.append('c.priority = ?')
            params.append(priority)
        if ward_id:
            where.append('c.ward_id = ?')
            params.append(ward_id)

        where_sql = ' AND '.join(where)
        count_row = cur.execute(
            f'SELECT COUNT(*) FROM complaints c WHERE {where_sql}', params
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        offset = max(0, (page - 1) * page_size)
        rows = cur.execute(
            f'''SELECT c.*, p.full_name AS citizen_name
                FROM complaints c
                LEFT JOIN profiles p ON p.user_id = c.citizen_id
                WHERE {where_sql}
                ORDER BY c.id DESC
                LIMIT ? OFFSET ?''',
            params + [int(page_size), offset]
        ).fetchall()

        cur.close()
        return [row_to_dict(r) for r in rows], total

    # ====================== UPDATE ======================
    def update_status(self, complaint_id, new_status, verified_at=None, closed_at=None):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''UPDATE complaints
               SET status = ?, updated_at = ?,
                   verified_at = COALESCE(?, verified_at),
                   closed_at = COALESCE(?, closed_at)
               WHERE id = ?''',
            (new_status, now, verified_at, closed_at, complaint_id)
        )
        conn.commit()
        cur.close()

    def update_fields(self, complaint_id, **fields):
        allowed = {'priority', 'duplicate_status', 'ward_id', 'address',
                   'ai_category_suggestion', 'ai_priority_suggestion'}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        updates['updated_at'] = utc_now()
        cols = ', '.join(f'{k} = ?' for k in updates)
        values = list(updates.values()) + [complaint_id]
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f'UPDATE complaints SET {cols} WHERE id = ?', values)
        conn.commit()
        cur.close()

    # ====================== DELETE ======================
    def delete(self, complaint_id):
        """Admin-only deletion. Cascades to images and history via FK."""
        conn = get_db()
        cur = conn.cursor()
        cur.execute('DELETE FROM complaints WHERE id = ?', (complaint_id,))
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected > 0

    # ====================== IMAGES ======================
    def add_image(self, complaint_id, file_info):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO complaint_images
               (complaint_id, file_path, original_filename, mime_type,
                file_size, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (complaint_id, file_info['file_path'], file_info['original_filename'],
             file_info['mime_type'], file_info['file_size'], now)
        )
        conn.commit()
        cur.close()

    def get_images(self, complaint_id):
        cur = get_db().cursor()
        rows = cur.execute(
            'SELECT * FROM complaint_images WHERE complaint_id = ? ORDER BY id',
            (complaint_id,)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    # ====================== HISTORY ======================
    def add_history(self, complaint_id, old_status, new_status,
                    changed_by, reason=None):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO complaint_status_history
               (complaint_id, old_status, new_status, changed_by, reason, created_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (complaint_id, old_status, new_status, changed_by, reason, now)
        )
        conn.commit()
        cur.close()

    def get_history(self, complaint_id):
        cur = get_db().cursor()
        rows = cur.execute(
            '''SELECT h.*, p.full_name AS changed_by_name
               FROM complaint_status_history h
               LEFT JOIN profiles p ON p.user_id = h.changed_by
               WHERE h.complaint_id = ?
               ORDER BY h.id ASC''',
            (complaint_id,)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    # ====================== STATS ======================
    def count_by_citizen(self, citizen_id):
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT
                 COUNT(*) AS total,
                 SUM(CASE WHEN status IN ('CLOSED','ADMIN_VERIFIED') THEN 1 ELSE 0 END) AS resolved,
                 SUM(CASE WHEN status NOT IN ('CLOSED','REJECTED','CANCELLED','ADMIN_VERIFIED') THEN 1 ELSE 0 END) AS open
               FROM complaints WHERE citizen_id = ?''',
            (citizen_id,)
        ).fetchone()
        cur.close()
        if not row:
            return {'total': 0, 'resolved': 0, 'open': 0}
        d = row_to_dict(row)
        return {
            'total': d.get('total') or 0,
            'resolved': d.get('resolved') or 0,
            'open': d.get('open') or 0,
        }