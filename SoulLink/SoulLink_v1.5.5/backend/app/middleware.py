# /backend/app/middleware.py
# v1.5.5 - System Middleware
# "I'm watching you... always watching." - Roz, Monsters Inc.

"""
System Middleware Components
Handles request processing, performance tracking, and security headers.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.app.core.logging_config import get_logger
import time
import uuid

logger = get_logger("Middleware")

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Limits the size of the request body to prevent DoS attacks.
    """
    def __init__(self, app, max_request_size: int = 1024 * 1024):
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            if int(content_length) > self.max_request_size:
                logger.warning(f"Request too large: {content_length} bytes")
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    content={"status": "error", "message": "Payload too large"},
                    status_code=413
                )
        return await call_next(request)


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
        else:
            # Debug log for normal requests (can be noisy)
            pass 
            # logger.debug(f"{request.method} {request.url} took {process_time:.4f}s")
            
        # 5. Add Headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
