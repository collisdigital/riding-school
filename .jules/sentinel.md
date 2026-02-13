## 2024-05-22 - In-Memory Rate Limiting Pattern
**Vulnerability:** Lack of rate limiting on sensitive endpoints (brute-force risk).
**Learning:** For single-instance deployments without Redis, a simple in-memory `defaultdict` with timestamp tracking provides effective rate limiting. This avoids new dependencies but has per-worker state limitations.
**Prevention:** Use the `RateLimiter` dependency from `app.core.ratelimit` on all sensitive POST endpoints (login, register, password reset).

## 2024-05-23 - Security Headers Middleware
**Vulnerability:** Missing security headers (X-Frame-Options, X-Content-Type-Options) exposing users to clickjacking and MIME sniffing.
**Learning:** FastAPI/Starlette does not include these headers by default. A custom middleware is the cleanest way to enforce them globally.
**Prevention:** Implement `SecurityHeadersMiddleware` and register it in `app/main.py` to ensure all responses carry defensive headers.
