"""
Re-export role_required + role shortcuts for convenience.
"""
from backend.utils.auth import role_required  # noqa: F401
from backend.utils.constants import ROLE_CITIZEN, ROLE_WORKER, ROLE_ADMIN


def citizen_required(fn):
    return role_required(ROLE_CITIZEN)(fn)


def worker_required(fn):
    return role_required(ROLE_WORKER)(fn)


def admin_required(fn):
    return role_required(ROLE_ADMIN)(fn)