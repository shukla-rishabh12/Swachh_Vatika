"""
Pickup repository. Simple, robust SQL.
"""
from backend.utils.db import get_db, utc_now, row_to_dict


class PickupRepository:

    def create(self, citizen_id, waste_type, description, latitude, longitude,
               address, preferred_date, status='SUBMITTED'):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO pickup_requests
               (citizen_id, waste_type, description, latitude, longitude,
                address, preferred_date, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (citizen_id, waste_type, description, latitude, longitude,
             address, preferred_date, status, now, now)
        )
        conn.commit()
        pid = cur.lastrowid
        cur.close()
        return pid

    def find_by_id(self, pickup_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM pickup_requests WHERE id = ?', (pickup_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def list_by_citizen(self, citizen_id, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()
        count_row = cur.execute(
            'SELECT COUNT(*) FROM pickup_requests WHERE citizen_id = ?',
            (citizen_id,)
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        offset = max(0, (page - 1) * page_size)
        rows = cur.execute(
            '''SELECT * FROM pickup_requests
               WHERE citizen_id = ?
               ORDER BY id DESC
               LIMIT ? OFFSET ?''',
            (citizen_id, int(page_size), offset)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    def list_all(self, status=None, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()
        where = '1=1'
        params = []
        if status:
            where += ' AND p.status = ?'
            params.append(status)
        count_row = cur.execute(
            f'SELECT COUNT(*) FROM pickup_requests p WHERE {where}', params
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        offset = max(0, (page - 1) * page_size)
        rows = cur.execute(
            f'''SELECT p.*, u.email, pr.full_name AS citizen_name
                FROM pickup_requests p
                LEFT JOIN users u ON u.id = p.citizen_id
                LEFT JOIN profiles pr ON pr.user_id = p.citizen_id
                WHERE {where}
                ORDER BY p.id DESC
                LIMIT ? OFFSET ?''',
            params + [int(page_size), offset]
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    def update_status(self, pickup_id, status):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE pickup_requests SET status = ?, updated_at = ? WHERE id = ?',
            (status, now, pickup_id)
        )
        conn.commit()
        cur.close()