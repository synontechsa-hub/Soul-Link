# /backend/app/middleware/performance.py
# v1.5.6 Normandy-SR2 Fix
# "Slow is smooth, smooth is fast." - Navy SEALs

import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.app.core.logging_config import get_logger

logger = get_logger("Middleware.Performance")

class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Tracks request duration and logs slow requests.
    Adds X-Process-Time and X-Request-ID headers.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 1. Start Timer & Tag Request
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add ID to request state for use in logging/sentry
        request.state.request_id = request_id
        
        # 2. Process Request
        try:
            response = await call_next(request)
        except Exception as e:
            # Calculate time even on error
            process_time = time.time() - start_time
            logger.error(f"Request failed [{request_id}]: {e} ({process_time:.4f}s)")
            raise e
        
        # 3. Stop Timer
        process_time = time.time() - start_time
        
        # 4. Log Slow Requests (>1s)
        if process_time > 1.0:
            logger.warning(f"SLOW REQUEST [{request_id}]: {request.method} {request.url} took {process_time:.4f}s")
            
        # 5. Add Headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
