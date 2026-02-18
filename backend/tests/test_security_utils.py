import sys
from unittest.mock import MagicMock

# Mock dependencies that are not installed in this environment
sys.modules["jose"] = MagicMock()
sys.modules["passlib"] = MagicMock()
sys.modules["passlib.context"] = MagicMock()

# Mock settings since it might try to read env vars or config files that need other deps
mock_settings = MagicMock()
mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
mock_settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
mock_settings.SECRET_KEY = "secret"
mock_settings.ALGORITHM = "HS256"

sys.modules["app.core.config"] = MagicMock()
from app.core import config  # noqa: E402

config.settings = mock_settings

from app.core.security import get_token_hash, verify_token_hash  # noqa: E402


def test_verify_token_hash_success():
    token = "some-random-token-123"
    token_hash = get_token_hash(token)
    assert verify_token_hash(token, token_hash) is True


def test_verify_token_hash_failure():
    token = "some-random-token-123"
    token_hash = get_token_hash(token)
    assert verify_token_hash("wrong-token", token_hash) is False


def test_verify_token_hash_empty():
    assert verify_token_hash("", get_token_hash("")) is True
    assert verify_token_hash("a", get_token_hash("b")) is False


if __name__ == "__main__":
    test_verify_token_hash_success()
    test_verify_token_hash_failure()
    test_verify_token_hash_empty()
    print("All tests passed!")
