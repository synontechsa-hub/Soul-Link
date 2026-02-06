# /backend/app/middleware/request_size_limit.py
# /version.py v1.5.4 Arise
# "Size matters not." - Yoda (but actually, it does for APIs)

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger("RequestSizeLimit")

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit the size of incoming requests.
    Prevents large payloads from overwhelming the server.
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
                    f"⚠️ Request too large: {content_length} bytes from {request.client.host}"
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "status": "error",
                        "message": "Request payload too large",
                        "max_size_bytes": self.max_request_size,
                        "your_size_bytes": content_length,
                        "hint": "The Legion Engine cannot process requests larger than 1MB."
                    }
                )
        
        response = await call_next(request)
        return response
