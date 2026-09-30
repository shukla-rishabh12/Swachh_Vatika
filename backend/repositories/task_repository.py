"""
Task repository. All SQL for tasks + task_proofs.
"""
from backend.utils.db import get_db, utc_now, row_to_dict


class TaskRepository:

    # ====================== CREATE ======================
    def create(self, worker_id, assigned_by, complaint_id=None,
               pickup_request_id=None, status='ASSIGNED'):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO tasks
               (complaint_id, pickup_request_id, worker_id, assigned_by,
                status, assigned_at, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (complaint_id, pickup_request_id, worker_id, assigned_by,
             status, now, now, now)
        )
        conn.commit()
        tid = cur.lastrowid
        cur.close()
        return tid

    # ====================== READ ======================
    def find_by_id(self, task_id):
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT t.*,
                      c.category AS complaint_category,
                      c.description AS complaint_description,
                      c.latitude AS complaint_latitude,
                      c.longitude AS complaint_longitude,
                      c.address AS complaint_address,
                      c.status AS complaint_status,
                      c.priority AS complaint_priority,
                      p.full_name AS worker_name,
                      p.phone AS worker_phone,
                      pr.full_name AS citizen_name
               FROM tasks t
               LEFT JOIN complaints c ON c.id = t.complaint_id
               LEFT JOIN profiles p ON p.user_id = t.worker_id
               LEFT JOIN complaints cc ON cc.id = t.complaint_id
               LEFT JOIN profiles pr ON pr.user_id = cc.citizen_id
               WHERE t.id = ?''',
            (task_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def list_by_worker(self, worker_id, status=None, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['t.worker_id = ?']
        params = [worker_id]
        if status:
            where.append('t.status = ?')
            params.append(status)

        where_sql = ' AND '.join(where)
        total = cur.execute(
            f'SELECT COUNT(*) AS c FROM tasks t WHERE {where_sql}', params
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            f'''SELECT t.*,
                      c.category AS complaint_category,
                      c.address AS complaint_address,
                      c.priority AS complaint_priority,
                      c.latitude AS complaint_latitude,
                      c.longitude AS complaint_longitude
                FROM tasks t
                LEFT JOIN complaints c ON c.id = t.complaint_id
                WHERE {where_sql}
                ORDER BY t.created_at DESC
                LIMIT ? OFFSET ?''',
            params + [page_size, offset]
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    def list_all(self, status=None, worker_id=None, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['1=1']
        params = []
        if status:
            where.append('t.status = ?')
            params.append(status)
        if worker_id:
            where.append('t.worker_id = ?')
            params.append(worker_id)

        where_sql = ' AND '.join(where)
        total = cur.execute(
            f'SELECT COUNT(*) AS c FROM tasks t WHERE {where_sql}', params
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            f'''SELECT t.*,
                       c.category AS complaint_category,
                       c.address AS complaint_address,
                       c.priority AS complaint_priority,
                       p.full_name AS worker_name
                FROM tasks t
                LEFT JOIN complaints c ON c.id = t.complaint_id
                LEFT JOIN profiles p ON p.user_id = t.worker_id
                WHERE {where_sql}
                ORDER BY t.created_at DESC
                LIMIT ? OFFSET ?''',
            params + [page_size, offset]
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    # ====================== UPDATE ======================
    def update_status(self, task_id, new_status, timestamps=None):
        """
        timestamps: dict like {'accepted_at': '...', 'started_at': '...',
                               'completed_at': '...', 'verified_at': '...'}
        """
        now = utc_now()
        sets = ['status = ?', 'updated_at = ?']
        params = [new_status, now]

        if timestamps:
            for k, v in timestamps.items():
                if k in ('accepted_at', 'started_at', 'completed_at', 'verified_at'):
                    sets.append(f'{k} = COALESCE(?, {k})')
                    params.append(v)

        params.append(task_id)
        sql = f'UPDATE tasks SET {", ".join(sets)} WHERE id = ?'

        conn = get_db()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        cur.close()

    # ====================== PROOFS ======================
    def add_proof(self, task_id, uploaded_by, file_info):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO task_proofs
               (task_id, uploaded_by, file_path, original_filename,
                mime_type, file_size, latitude, longitude, uploaded_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (task_id, uploaded_by,
             file_info.get('file_path'), file_info.get('original_filename'),
             file_info.get('mime_type'), file_info.get('file_size'),
             file_info.get('latitude'), file_info.get('longitude'), now)
        )
        conn.commit()
        cur.close()

    def get_proofs(self, task_id):
        cur = get_db().cursor()
        rows = cur.execute(
            'SELECT * FROM task_proofs WHERE task_id = ? ORDER BY id',
            (task_id,)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    # ====================== STATS ======================
    def count_by_worker(self, worker_id):
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT
                 COUNT(*) AS total,
                 SUM(CASE WHEN status = 'ASSIGNED' THEN 1 ELSE 0 END) AS assigned,
                 SUM(CASE WHEN status = 'ACCEPTED' THEN 1 ELSE 0 END) AS accepted,
                 SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress,
                 SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
                 SUM(CASE WHEN status = 'VERIFIED' THEN 1 ELSE 0 END) AS verified
               FROM tasks WHERE worker_id = ?''',
            (worker_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row) or {}