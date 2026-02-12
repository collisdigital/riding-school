import time
from collections import defaultdict

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, requests_limit: int = 5, time_window: int = 60):
        self.requests_limit = requests_limit
        self.time_window = time_window
        self.requests = defaultdict(list)

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean up old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if current_time - t < self.time_window
        ]

        if len(self.requests[client_ip]) >= self.requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )

        self.requests[client_ip].append(current_time)
