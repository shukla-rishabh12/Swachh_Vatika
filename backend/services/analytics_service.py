"""
Analytics aggregation queries. All values computed from real DB records.
"""
from backend.utils.db import get_db, row_to_dict


class AnalyticsService:

    # ====================== SUMMARY ======================
    def get_summary(self):
        cur = get_db().cursor()

        complaints = cur.execute(
            '''SELECT
                 COUNT(*) AS total,
                 SUM(CASE WHEN status IN ('SUBMITTED','UNDER_REVIEW') THEN 1 ELSE 0 END) AS pending_review,
                 SUM(CASE WHEN status = 'VERIFIED' THEN 1 ELSE 0 END) AS verified,
                 SUM(CASE WHEN status = 'ASSIGNED' THEN 1 ELSE 0 END) AS assigned,
                 SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress,
                 SUM(CASE WHEN status = 'WORKER_COMPLETED' THEN 1 ELSE 0 END) AS pending_verification,
                 SUM(CASE WHEN status IN ('ADMIN_VERIFIED','CLOSED') THEN 1 ELSE 0 END) AS resolved,
                 SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) AS rejected
               FROM complaints'''
        ).fetchone()

        pickups = cur.execute(
            '''SELECT
                 COUNT(*) AS total,
                 SUM(CASE WHEN status IN ('SUBMITTED','UNDER_REVIEW') THEN 1 ELSE 0 END) AS pending,
                 SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed
               FROM pickup_requests'''
        ).fetchone()

        workers = cur.execute(
            'SELECT COUNT(*) AS total, SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) AS active FROM users WHERE role="WORKER"'
        ).fetchone()

        citizens = cur.execute(
            'SELECT COUNT(*) AS total FROM users WHERE role="CITIZEN"'
        ).fetchone()

        tasks = cur.execute(
            '''SELECT
                 COUNT(*) AS total,
                 SUM(CASE WHEN status = 'ASSIGNED' THEN 1 ELSE 0 END) AS active,
                 SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS pending_verification
               FROM tasks'''
        ).fetchone()

        tokens = cur.execute(
            "SELECT COALESCE(SUM(amount),0) AS issued FROM token_transactions WHERE transaction_type='EARN'"
        ).fetchone()

        cur.close()

        return {
            'total_complaints':     complaints['total'] or 0,
            'pending_review':       complaints['pending_review'] or 0,
            'verified_complaints':  complaints['verified'] or 0,
            'assigned_complaints':  complaints['assigned'] or 0,
            'in_progress':          complaints['in_progress'] or 0,
            'pending_proof_verification': complaints['pending_verification'] or 0,
            'resolved_complaints':  complaints['resolved'] or 0,
            'rejected_complaints':  complaints['rejected'] or 0,
            'total_pickups':        pickups['total'] or 0,
            'pending_pickups':      pickups['pending'] or 0,
            'completed_pickups':    pickups['completed'] or 0,
            'total_workers':        workers['total'] or 0,
            'active_workers':       workers['active'] or 0,
            'total_citizens':       citizens['total'] or 0,
            'total_tasks':          tasks['total'] or 0,
            'active_tasks':         tasks['active'] or 0,
            'tokens_issued':        tokens['issued'] or 0,
        }

    # ====================== BREAKDOWNS ======================
    def complaints_by_status(self):
        cur = get_db().cursor()
        rows = cur.execute(
            'SELECT status, COUNT(*) AS count FROM complaints GROUP BY status ORDER BY count DESC'
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    def complaints_by_category(self):
        cur = get_db().cursor()
        rows = cur.execute(
            'SELECT category, COUNT(*) AS count FROM complaints GROUP BY category ORDER BY count DESC'
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    def complaints_by_priority(self):
        cur = get_db().cursor()
        rows = cur.execute(
            'SELECT priority, COUNT(*) AS count FROM complaints GROUP BY priority ORDER BY count DESC'
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    def complaints_by_ward(self):
        cur = get_db().cursor()
        rows = cur.execute(
            '''SELECT w.id AS ward_id, w.name AS ward_name, w.code AS ward_code,
                      COUNT(c.id) AS count
               FROM wards w
               LEFT JOIN complaints c ON c.ward_id = w.id
               GROUP BY w.id, w.name, w.code
               ORDER BY count DESC'''
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    def complaints_by_date(self, days=30):
        cur = get_db().cursor()
        rows = cur.execute(
            f'''SELECT DATE(created_at) AS date, COUNT(*) AS count
                FROM complaints
                WHERE created_at >= DATE('now', '-{int(days)} days')
                GROUP BY DATE(created_at)
                ORDER BY date ASC'''
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    # ====================== RESOLUTION ======================
    def resolution_stats(self):
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT
                 COUNT(*) AS total_closed,
                 AVG(julianday(closed_at) - julianday(created_at)) AS avg_days
               FROM complaints
               WHERE closed_at IS NOT NULL'''
        ).fetchone()
        cur.close()
        d = row_to_dict(row) or {}
        avg = d.get('avg_days')
        return {
            'total_closed': d.get('total_closed') or 0,
            'avg_resolution_days': round(avg, 2) if avg else 0,
        }

    # ====================== TOKEN TRENDS ======================
    def token_trend(self, days=30):
        cur = get_db().cursor()
        rows = cur.execute(
            f'''SELECT DATE(created_at) AS date,
                       SUM(CASE WHEN transaction_type='EARN' THEN amount ELSE 0 END) AS earned,
                       SUM(CASE WHEN transaction_type='SPEND' THEN amount ELSE 0 END) AS spent
                FROM token_transactions
                WHERE created_at >= DATE('now', '-{int(days)} days')
                GROUP BY DATE(created_at)
                ORDER BY date ASC'''
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    # ====================== WORKER PERFORMANCE ======================
    def worker_performance(self, limit=10):
        cur = get_db().cursor()
        rows = cur.execute(
            f'''SELECT u.id AS worker_id, p.full_name AS worker_name,
                       COUNT(t.id) AS total_tasks,
                       SUM(CASE WHEN t.status='VERIFIED' THEN 1 ELSE 0 END) AS verified_tasks,
                       SUM(CASE WHEN t.status='COMPLETED' THEN 1 ELSE 0 END) AS completed_tasks,
                       SUM(CASE WHEN t.status='VERIFICATION_FAILED' THEN 1 ELSE 0 END) AS failed_tasks
                FROM users u
                LEFT JOIN profiles p ON p.user_id = u.id
                LEFT JOIN tasks t ON t.worker_id = u.id
                WHERE u.role = 'WORKER'
                GROUP BY u.id, p.full_name
                ORDER BY verified_tasks DESC
                LIMIT ?''',
            (limit,)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]