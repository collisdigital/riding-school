import pytest
from fastapi import HTTPException

from app.api.deps import RequirePermission
from app.schemas.token import TokenPayload


def test_require_permission_success():
    token = TokenPayload(sub="user", sid="school", perms=["riders:create"])
    dependency = RequirePermission("riders:create")
    result = dependency(token_data=token)
    assert result == token

def test_require_permission_failure():
    token = TokenPayload(sub="user", sid="school", perms=["riders:view"])
    dependency = RequirePermission("riders:create")
    with pytest.raises(HTTPException) as exc:
        dependency(token_data=token)
    assert exc.value.status_code == 403
