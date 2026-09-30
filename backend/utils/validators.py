"""
Input validators. Pure functions — return (is_valid, error_message_or_None).
"""
import re


EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
PHONE_REGEX = re.compile(r'^[0-9]{10}$')


def is_valid_email(email):
    if not email or not isinstance(email, str):
        return False, 'Email is required.'
    email = email.strip().lower()
    if not EMAIL_REGEX.match(email):
        return False, 'Invalid email format.'
    return True, None


def is_valid_password(password):
    if not password or not isinstance(password, str):
        return False, 'Password is required.'
    if len(password) < 6:
        return False, 'Password must be at least 6 characters.'
    if len(password) > 128:
        return False, 'Password is too long.'
    return True, None


def is_valid_phone(phone):
    if phone in (None, ''):
        return True, None  # optional
    phone = str(phone).strip()
    if not PHONE_REGEX.match(phone):
        return False, 'Phone must be 10 digits.'
    return True, None


def is_valid_full_name(name):
    if not name or not isinstance(name, str):
        return False, 'Full name is required.'
    name = name.strip()
    if len(name) < 2 or len(name) > 120:
        return False, 'Full name must be 2-120 characters.'
    return True, None


def is_valid_latitude(lat):
    try:
        lat = float(lat)
    except (TypeError, ValueError):
        return False, 'Latitude must be a number.'
    if lat < -90 or lat > 90:
        return False, 'Latitude must be between -90 and 90.'
    return True, None


def is_valid_longitude(lng):
    try:
        lng = float(lng)
    except (TypeError, ValueError):
        return False, 'Longitude must be a number.'
    if lng < -180 or lng > 180:
        return False, 'Longitude must be between -180 and 180.'
    return True, None


def is_valid_category(category):
    from backend.utils.constants import CATEGORIES
    if category not in CATEGORIES:
        return False, f'Category must be one of: {", ".join(CATEGORIES)}'
    return True, None


def is_valid_priority(priority):
    from backend.utils.constants import PRIORITIES
    if priority not in PRIORITIES:
        return False, f'Priority must be one of: {", ".join(PRIORITIES)}'
    return True, None


def validate_required(data, fields):
    """Check that all fields exist and are non-empty. Returns (ok, errors_dict)."""
    errors = {}
    for field in fields:
        value = data.get(field) if isinstance(data, dict) else None
        if value is None or (isinstance(value, str) and not value.strip()):
            errors[field] = f'{field} is required.'
    return (len(errors) == 0), errors


def parse_pagination(args):
    """Extract safe page & page_size from request.args."""
    from backend.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
    try:
        page = int(args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(args.get('page_size', DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        page_size = DEFAULT_PAGE_SIZE
    page = max(1, page)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    return page, page_size