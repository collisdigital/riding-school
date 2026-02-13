from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_security_headers():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "0"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
