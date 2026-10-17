import unittest

from django.conf import settings


if not settings.configured:
    settings.configure(
        PASSWORD_HASHERS=[
            "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        ]
    )

from attendance.system.auth_utils import (  # noqa: E402
    hash_password,
    verify_password_and_upgrade,
)


class AuthenticationHelperTests(unittest.TestCase):
    def test_new_password_is_hashed_and_verifies(self):
        password = "CorrectHorseBatteryStaple"
        password_hash = hash_password(password)

        self.assertNotEqual(password_hash, password)
        self.assertNotEqual(password_hash, "plaintext")
        self.assertTrue(verify_password_and_upgrade(password, password_hash)[0])
        self.assertIsNone(
            verify_password_and_upgrade(password, password_hash)[1]
        )

    def test_legacy_plaintext_password_is_upgraded(self):
        password = "legacy-password"
        authenticated, upgraded_hash = verify_password_and_upgrade(
            password,
            password,
        )

        self.assertTrue(authenticated)
        self.assertIsNotNone(upgraded_hash)
        self.assertNotEqual(upgraded_hash, password)
        self.assertTrue(
            verify_password_and_upgrade(password, upgraded_hash)[0]
        )

    def test_wrong_password_is_rejected(self):
        password_hash = hash_password("correct-password")

        authenticated, upgraded_hash = verify_password_and_upgrade(
            "wrong-password",
            password_hash,
        )

        self.assertFalse(authenticated)
        self.assertIsNone(upgraded_hash)


if __name__ == "__main__":
    unittest.main()
