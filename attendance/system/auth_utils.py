"""Authentication helpers for the legacy employee account table."""

from typing import Optional, Tuple

from django.contrib.auth.hashers import check_password, make_password


def hash_password(raw_password: str) -> str:
    """Return a Django-compatible password hash."""
    return make_password(raw_password)


def verify_password_and_upgrade(
    raw_password: str,
    stored_password: str,
) -> Tuple[bool, Optional[str]]:
    """Verify a password and return a replacement hash for legacy plaintext data.

    New accounts should store Django-compatible password hashes. Existing legacy
    accounts that still contain plaintext passwords are accepted once and
    transparently upgraded after successful authentication.
    """
    if not stored_password:
        return False, None

    if check_password(raw_password, stored_password):
        return True, None

    if stored_password == raw_password:
        return True, make_password(raw_password)

    return False, None
