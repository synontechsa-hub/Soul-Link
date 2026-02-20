# /backend/app/middleware/request_size_limit.py
# v1.5.6 Normandy-SR2 Fix
# "Size matters not." - Yoda (but actually, it does for APIs)

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.app.core.logging_config import get_logger

logger = get_logger("Middleware.SizeLimit")

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the size of incoming requests.
    Prevents large payloads from Scrambling the neural link.
    """
    
    def __init__(self, app, max_request_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_request_size:
                logger.warning(
                    f"⚠️ Request too large: {content_length} bytes from {request.client.host if request.client else 'unknown'}"
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "status": "error",
                        "message": "Payload too large",
                        "max_size_bytes": self.max_request_size,
                        "your_size_bytes": content_length,
                        "hint": "The Legion Engine cannot process neural bursts larger than the configured limit."
                    }
                )
        
        return await call_next(request)
