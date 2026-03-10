import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import redirect_latency


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start = time.time()

        response: Response = await call_next(request)

        duration = time.time() - start

        # track redirect latency only
        if request.url.path.startswith("/") and request.method == "GET":
            redirect_latency.observe(duration)

        return response