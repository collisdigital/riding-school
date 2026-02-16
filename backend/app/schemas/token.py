from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str | None = None
    sid: str | None = None
    perms: list[str] = []
    roles: list[str] = []
