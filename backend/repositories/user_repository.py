"""
User + Profile + Wallet DB operations.
Only SQL lives here — no business logic.
"""
from backend.utils.db import get_db, utc_now, row_to_dict


class UserRepository:

    # ====================== USERS ======================
    def find_by_email(self, email):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM users WHERE LOWER(email) = LOWER(?)',
            (email.strip(),)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def find_by_id(self, user_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def email_exists(self, email):
        return self.find_by_email(email) is not None

    def create_user(self, email, password_hash, role):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO users (email, password_hash, role, is_active,
                                  created_at, updated_at)
               VALUES (?, ?, ?, 1, ?, ?)''',
            (email.strip().lower(), password_hash, role, now, now)
        )
        conn.commit()
        user_id = cur.lastrowid
        cur.close()
        return user_id

    def update_last_login(self, user_id):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?',
            (now, now, user_id)
        )
        conn.commit()
        cur.close()

    def update_status(self, user_id, is_active):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            'UPDATE users SET is_active = ?, updated_at = ? WHERE id = ?',
            (1 if is_active else 0, now, user_id)
        )
        conn.commit()
        cur.close()

    def list_users(self, role=None, is_active=None, search=None,
                   page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['1=1']
        params = []

        if role:
            where.append('role = ?')
            params.append(role)
        if is_active is not None:
            where.append('is_active = ?')
            params.append(1 if is_active else 0)
        if search:
            where.append('(LOWER(email) LIKE ? OR id IN '
                         '(SELECT user_id FROM profiles WHERE LOWER(full_name) LIKE ?))')
            like = f'%{search.lower()}%'
            params.extend([like, like])

        where_sql = ' AND '.join(where)

        total = cur.execute(
            f'SELECT COUNT(*) AS c FROM users WHERE {where_sql}', params
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            f'''SELECT u.*, p.full_name, p.phone
                FROM users u
                LEFT JOIN profiles p ON p.user_id = u.id
                WHERE {where_sql}
                ORDER BY u.id DESC
                LIMIT ? OFFSET ?''',
            params + [page_size, offset]
        ).fetchall()

        cur.close()
        return [row_to_dict(r) for r in rows], total

    # ====================== PROFILES ======================
    def create_profile(self, user_id, full_name, phone=None,
                       address=None, city=None, ward_id=None):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO profiles
               (user_id, full_name, phone, address, city, ward_id,
                profile_image, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)''',
            (user_id, full_name, phone, address, city, ward_id, now, now)
        )
        conn.commit()
        cur.close()

    def get_profile(self, user_id):
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT p.*, w.name AS ward_name, w.code AS ward_code
               FROM profiles p
               LEFT JOIN wards w ON w.id = p.ward_id
               WHERE p.user_id = ?''',
            (user_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def update_profile(self, user_id, **fields):
        allowed = {'full_name', 'phone', 'address', 'city',
                   'ward_id', 'profile_image'}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        updates['updated_at'] = utc_now()
        cols = ', '.join(f'{k} = ?' for k in updates)
        values = list(updates.values()) + [user_id]
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f'UPDATE profiles SET {cols} WHERE user_id = ?', values)
        conn.commit()
        cur.close()

    # ====================== WALLET ======================
    def create_wallet(self, user_id):
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT OR IGNORE INTO token_wallets
               (user_id, balance, lifetime_earned, lifetime_spent, updated_at)
               VALUES (?, 0, 0, 0, ?)''',
            (user_id, now)
        )
        conn.commit()
        cur.close()

    def get_wallet(self, user_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM token_wallets WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)