"""
Pickup business logic. Defensive — catches everything and logs.
"""
import traceback
from backend.repositories.pickup_repository import PickupRepository
from backend.services.auth_service import AuthError


VALID_PICKUP_STATUSES = {
    'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'ASSIGNED',
    'COMPLETED', 'REJECTED', 'CANCELLED'
}


class PickupService:

    def __init__(self):
        self.repo = PickupRepository()

    def create_pickup(self, citizen_id, data):
        try:
            waste_type = str(data.get('waste_type') or '').strip().upper()
            description = (data.get('description') or '').strip() or None
            address = (data.get('address') or '').strip() or None
            preferred_date = (data.get('preferred_date') or '').strip() or None

            # Parse coordinates safely
            latitude = None
            longitude = None

            lat_raw = data.get('latitude')
            lng_raw = data.get('longitude')

            if lat_raw not in (None, '', 'null', 'undefined'):
                try:
                    latitude = float(lat_raw)
                    if latitude < -90 or latitude > 90:
                        raise AuthError('Latitude must be between -90 and 90.',
                                        'VALIDATION_ERROR', 422)
                except (TypeError, ValueError):
                    raise AuthError('Invalid latitude.',
                                    'VALIDATION_ERROR', 422)

            if lng_raw not in (None, '', 'null', 'undefined'):
                try:
                    longitude = float(lng_raw)
                    if longitude < -180 or longitude > 180:
                        raise AuthError('Longitude must be between -180 and 180.',
                                        'VALIDATION_ERROR', 422)
                except (TypeError, ValueError):
                    raise AuthError('Invalid longitude.',
                                    'VALIDATION_ERROR', 422)

            if not waste_type:
                raise AuthError('Waste type is required.',
                                'VALIDATION_ERROR', 422)

            pid = self.repo.create(
                citizen_id=citizen_id,
                waste_type=waste_type,
                description=description,
                latitude=latitude,
                longitude=longitude,
                address=address,
                preferred_date=preferred_date,
            )
            return self.repo.find_by_id(pid)

        except AuthError:
            raise
        except Exception as e:
            print('[pickup_service] create_pickup FAILED:')
            traceback.print_exc()
            raise AuthError(
                'Could not create pickup: ' + str(e),
                'INTERNAL_ERROR', 500
            )

    def get_my_pickups(self, citizen_id, page=1, page_size=20):
        try:
            return self.repo.list_by_citizen(citizen_id, page, page_size)
        except Exception as e:
            print('[pickup_service] get_my_pickups FAILED:')
            traceback.print_exc()
            raise AuthError('Failed to load pickups: ' + str(e),
                            'INTERNAL_ERROR', 500)

    def get_pickup_detail(self, pickup_id, user):
        p = self.repo.find_by_id(pickup_id)
        if not p:
            raise AuthError('Pickup not found.', 'NOT_FOUND', 404)
        if user['role'] == 'CITIZEN' and p['citizen_id'] != user['id']:
            raise AuthError('Not allowed.', 'FORBIDDEN', 403)
        return p

    def change_status(self, pickup_id, new_status, user):
        if new_status not in VALID_PICKUP_STATUSES:
            raise AuthError('Invalid status.', 'VALIDATION_ERROR', 422)
        p = self.repo.find_by_id(pickup_id)
        if not p:
            raise AuthError('Pickup not found.', 'NOT_FOUND', 404)
        self.repo.update_status(pickup_id, new_status)
        return self.repo.find_by_id(pickup_id)