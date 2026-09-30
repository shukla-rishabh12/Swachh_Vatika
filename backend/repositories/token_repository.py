"""
Token wallet + transaction repository. All SQL lives here.
"""
from backend.utils.db import get_db, utc_now, row_to_dict
from backend.utils.constants import TX_EARN


class TokenRepository:

    # ====================== WALLET ======================
    def get_wallet_by_user(self, user_id):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT * FROM token_wallets WHERE user_id = ?', (user_id,)
        ).fetchone()
        cur.close()
        return row_to_dict(row)

    def ensure_wallet(self, user_id):
        """Create wallet if missing. Returns wallet row."""
        wallet = self.get_wallet_by_user(user_id)
        if wallet:
            return wallet
        now = utc_now()
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO token_wallets
               (user_id, balance, lifetime_earned, lifetime_spent, updated_at)
               VALUES (?, 0, 0, 0, ?)''',
            (user_id, now)
        )
        conn.commit()
        cur.close()
        return self.get_wallet_by_user(user_id)

    # ====================== IDEMPOTENCY CHECK ======================
    def earning_exists(self, source_type, source_id, transaction_type=TX_EARN):
        """
        Check if an EARN transaction already exists for the given source.
        Prevents duplicate rewards for the same event.
        """
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT id FROM token_transactions
               WHERE source_type = ? AND source_id = ?
                 AND transaction_type = ?
               LIMIT 1''',
            (source_type, source_id, transaction_type)
        ).fetchone()
        cur.close()
        return row is not None

    # ====================== TRANSACTIONS ======================
    def create_transaction_and_update_wallet(
        self, user_id, transaction_type, amount, source_type,
        source_id=None, description=None
    ):
        """
        Atomically: insert transaction row + update wallet balance.
        Runs inside a single DB transaction; rolls back on any failure.
        Returns the created transaction id.
        """
        wallet = self.ensure_wallet(user_id)
        wallet_id = wallet['id']
        now = utc_now()

        conn = get_db()
        cur = conn.cursor()
        try:
            conn.execute('BEGIN')

            # Insert transaction
            cur.execute(
                '''INSERT INTO token_transactions
                   (wallet_id, user_id, transaction_type, amount,
                    source_type, source_id, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (wallet_id, user_id, transaction_type, amount,
                 source_type, source_id, description, now)
            )
            tx_id = cur.lastrowid

            # Update wallet balances
            if transaction_type == TX_EARN:
                cur.execute(
                    '''UPDATE token_wallets
                       SET balance = balance + ?,
                           lifetime_earned = lifetime_earned + ?,
                           updated_at = ?
                       WHERE id = ?''',
                    (amount, amount, now, wallet_id)
                )
            elif transaction_type == 'SPEND':
                cur.execute(
                    '''UPDATE token_wallets
                       SET balance = balance - ?,
                           lifetime_spent = lifetime_spent + ?,
                           updated_at = ?
                       WHERE id = ?''',
                    (amount, amount, now, wallet_id)
                )
            elif transaction_type == 'ADJUSTMENT':
                cur.execute(
                    '''UPDATE token_wallets
                       SET balance = balance + ?,
                           updated_at = ?
                       WHERE id = ?''',
                    (amount, now, wallet_id)
                )
            elif transaction_type == 'REVERSAL':
                cur.execute(
                    '''UPDATE token_wallets
                       SET balance = balance + ?,
                           lifetime_earned = MAX(0, lifetime_earned - ?),
                           updated_at = ?
                       WHERE id = ?''',
                    (amount, amount, now, wallet_id)
                )

            conn.commit()
            return tx_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    def list_transactions(self, user_id, transaction_type=None,
                          page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        where = ['user_id = ?']
        params = [user_id]
        if transaction_type:
            where.append('transaction_type = ?')
            params.append(transaction_type)

        where_sql = ' AND '.join(where)
        total = cur.execute(
            f'SELECT COUNT(*) AS c FROM token_transactions WHERE {where_sql}',
            params
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            f'''SELECT * FROM token_transactions
                WHERE {where_sql}
                ORDER BY created_at DESC, id DESC
                LIMIT ? OFFSET ?''',
            params + [page_size, offset]
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total

    # ====================== STATS ======================
    def get_global_stats(self):
        cur = get_db().cursor()
        row = cur.execute(
            '''SELECT
                 COUNT(*) AS total_transactions,
                 COALESCE(SUM(CASE WHEN transaction_type = 'EARN' THEN amount ELSE 0 END), 0) AS total_earned,
                 COALESCE(SUM(CASE WHEN transaction_type = 'SPEND' THEN amount ELSE 0 END), 0) AS total_spent,
                 COALESCE(SUM(CASE WHEN transaction_type = 'ADJUSTMENT' THEN amount ELSE 0 END), 0) AS total_adjusted
               FROM token_transactions'''
        ).fetchone()
        cur.close()
        return row_to_dict(row) or {}

    def get_balance_total(self):
        cur = get_db().cursor()
        row = cur.execute(
            'SELECT COALESCE(SUM(balance), 0) AS total_balance FROM token_wallets'
        ).fetchone()
        cur.close()
        return row['total_balance'] if row else 0

    def list_all_wallets(self, page=1, page_size=20):
        conn = get_db()
        cur = conn.cursor()

        total = cur.execute(
            'SELECT COUNT(*) AS c FROM token_wallets'
        ).fetchone()['c']

        offset = (page - 1) * page_size
        rows = cur.execute(
            '''SELECT w.*, u.email, p.full_name
               FROM token_wallets w
               LEFT JOIN users u ON u.id = w.user_id
               LEFT JOIN profiles p ON p.user_id = w.user_id
               ORDER BY w.balance DESC
               LIMIT ? OFFSET ?''',
            (page_size, offset)
        ).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows], total