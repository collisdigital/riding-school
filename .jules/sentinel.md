## 2024-05-22 - In-Memory Rate Limiting Pattern
**Vulnerability:** Lack of rate limiting on sensitive endpoints (brute-force risk).
**Learning:** For single-instance deployments without Redis, a simple in-memory `defaultdict` with timestamp tracking provides effective rate limiting. This avoids new dependencies but has per-worker state limitations.
**Prevention:** Use the `RateLimiter` dependency from `app.core.ratelimit` on all sensitive POST endpoints (login, register, password reset).
