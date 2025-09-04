import unittest
from unittest.mock import AsyncMock, patch

from models.user import User
from services.auth_service import AuthService


class TestAuthService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_repo = AsyncMock()
        self.auth_service = AuthService(self.mock_repo)
        self.fake_user = User(
            id=1, nickname="nick", fio="TestFio", email="test@example.com",
            phone_number="123", password="pass"
        )
        self.fake_register_user = {
            "id": 1,
            "nickname": "nick",
            "fio": "TestFio",
            "email": "test@example.com",
            "phone_number": "123",
            "password": "pass",
            "repeat_password": "pass",
        }

    async def test_register_success(self):
        self.mock_repo.find_by_email.return_value = None
        self.mock_repo.create.return_value = self.fake_user

        result = await self.auth_service.register(object(), self.fake_register_user)
        self.assertEqual(result.email, "test@example.com")

    @patch("services.auth_service.JWTManager.create_access_token", return_value="fake.jwt.token")
    async def test_login_success(self, mock_jwt):
        self.mock_repo.find_by_email.return_value = self.fake_user

        token = await self.auth_service.login(object(), "test@example.com", "pass")
        self.assertEqual(token, "fake.jwt.token")
        mock_jwt.assert_called_once()

    @patch("services.auth_service.JWTManager.create_access_token")
    async def test_login_wrong_credentials(self, mock_jwt):
        self.mock_repo.find_by_email.return_value = self.fake_user
        with self.assertRaises(ValueError) as ctx:
            await self.auth_service.login(object(), "test@example.com", "wrong-pass")

        self.assertIn("Invalid credentials", str(ctx.exception))
        mock_jwt.assert_not_called()

    @patch("services.auth_service.JWTManager.create_access_token")
    async def test_login_user_not_found(self, mock_jwt):
        self.mock_repo.find_by_email.return_value = None
        with self.assertRaises(ValueError):
            await self.auth_service.login(object(), "no-user@example.com", "any")

        mock_jwt.assert_not_called()