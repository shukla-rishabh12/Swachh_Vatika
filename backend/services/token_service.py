"""
Token business logic. Handles reward issuance, idempotency, wallet queries.
"""
from backend.repositories.token_repository import TokenRepository
from backend.services.notification_service import NotificationService
from backend.services.auth_service import AuthError
from backend.utils.constants import (
    TX_EARN, TX_SPEND, TX_ADJUSTMENT, TX_REVERSAL, TX_TYPES,
    SRC_COMPLAINT, SRC_PICKUP, SRC_ADMIN_ADJUSTMENT,
)


class TokenService:

    def __init__(self):
        self.repo = TokenRepository()
        self.notifs = NotificationService()

    # ====================== WALLET READ ======================
    def get_my_wallet(self, user_id):
        return self.repo.ensure_wallet(user_id)

    def get_my_transactions(self, user_id, transaction_type=None,
                            page=1, page_size=20):
        if transaction_type and transaction_type not in TX_TYPES:
            raise AuthError('Invalid transaction type.',
                            'VALIDATION_ERROR', 422)
        return self.repo.list_transactions(user_id, transaction_type,
                                           page, page_size)

    # ====================== REWARD (IDEMPOTENT) ======================
    def award_complaint_reward(self, citizen_id, complaint_id, amount,
                               description=None):
        return self._award(
            user_id=citizen_id,
            amount=amount,
            source_type=SRC_COMPLAINT,
            source_id=complaint_id,
            description=description or f'Complaint #{complaint_id} verified',
            notify_msg=f'You earned {amount} SwachhTokens for verified complaint #{complaint_id}.'
        )

    def award_pickup_reward(self, citizen_id, pickup_id, amount,
                            description=None):
        return self._award(
            user_id=citizen_id,
            amount=amount,
            source_type=SRC_PICKUP,
            source_id=pickup_id,
            description=description or f'Pickup #{pickup_id} completed',
            notify_msg=f'You earned {amount} SwachhTokens for pickup #{pickup_id}.'
        )

    def _award(self, user_id, amount, source_type, source_id,
               description, notify_msg):
        if not isinstance(amount, int) or amount <= 0:
            return {'awarded': False, 'reason': 'Invalid amount.',
                    'transaction_id': None}

        if self.repo.earning_exists(source_type, source_id, TX_EARN):
            return {'awarded': False,
                    'reason': 'Reward already issued for this source.',
                    'transaction_id': None}

        tx_id = self.repo.create_transaction_and_update_wallet(
            user_id=user_id,
            transaction_type=TX_EARN,
            amount=amount,
            source_type=source_type,
            source_id=source_id,
            description=description,
        )

        try:
            self.notifs.notify_tokens_credited(user_id, amount, notify_msg)
        except Exception as e:
            print(f'[WARN] token notify failed: {e}')

        return {'awarded': True, 'transaction_id': tx_id, 'reason': 'OK'}

    # ====================== ADMIN ADJUSTMENT ======================
    def admin_adjust(self, admin_id, target_user_id, amount, reason=None):
        if not isinstance(amount, int) or amount == 0:
            raise AuthError('Amount must be a non-zero integer.',
                            'VALIDATION_ERROR', 422)
        if abs(amount) > 10000:
            raise AuthError('Amount too large (max 10000).',
                            'VALIDATION_ERROR', 422)

        from backend.repositories.user_repository import UserRepository
        target = UserRepository().find_by_id(target_user_id)
        if not target:
            raise AuthError('Target user not found.', 'NOT_FOUND', 404)

        description = reason or f'Admin adjustment by user #{admin_id}'

        tx_id = self.repo.create_transaction_and_update_wallet(
            user_id=target_user_id,
            transaction_type=TX_ADJUSTMENT,
            amount=amount,
            source_type=SRC_ADMIN_ADJUSTMENT,
            source_id=admin_id,
            description=description,
        )

        try:
            from backend.services.audit_service import AuditService
            AuditService().log_token_adjusted(
                admin_id, target_user_id, amount, reason
            )
        except Exception as e:
            print(f'[WARN] token audit failed: {e}')

        try:
            sign = '+' if amount > 0 else ''
            self.notifs.notify_tokens_credited(
                target_user_id, amount,
                f'{sign}{amount} SwachhTokens: {description}'
            )
        except Exception as e:
            print(f'[WARN] token notify failed: {e}')

        return {
            'transaction_id': tx_id,
            'user_id': target_user_id,
            'amount': amount,
        }

    # ====================== ADMIN: READ ======================
    def admin_stats(self):
        stats = self.repo.get_global_stats()
        stats['total_balance'] = self.repo.get_balance_total()
        return stats

    def admin_list_wallets(self, page=1, page_size=20):
        return self.repo.list_all_wallets(page, page_size)