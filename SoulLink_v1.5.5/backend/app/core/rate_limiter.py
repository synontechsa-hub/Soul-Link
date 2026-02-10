# /backend/app/core/rate_limiter.py
# /version.py v1.5.4 Arise
# "You shall not pass!" - Gandalf, Lord of the Rings

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("RateLimiter")

# Initialize the rate limiter
# Uses client IP address as the key for rate limiting
# Custom key function to support proxies (Docker/Nginx)
def get_real_ip(request: Request) -> str:
    # Build a list of potential headers: Cloudflare, Nginx, or standard XFF
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.headers.get("X-Real-IP") or get_remote_address(request)

# Initialize the rate limiter
# Uses client IP address as the key for rate limiting
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["100/minute"],  # Global default: 100 requests per minute
    storage_uri="memory://",  # In-memory storage (upgrade to Redis for production)
    headers_enabled=False,  # Disable headers to prevent "parameter `response` must be an instance of starlette.responses.Response" error
)

# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.
    Returns a friendly error message with retry information.
    """
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)} on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "message": "Neural Link Overloaded. Too many requests. Please slow down.",
            "retry_after": exc.detail.split("Retry after ")[1] if "Retry after" in exc.detail else "60 seconds",
            "hint": "The Legion Engine is protecting itself from overload. Take a breath, Linker."
        },
        headers={
            "Retry-After": "60"
        }
    )

# Rate limit configurations for different endpoint types
class RateLimits:
    """
    Centralized rate limit configurations.
    Adjust these based on your API usage patterns and infrastructure.
    """
    
    # Authentication endpoints (stricter limits to prevent brute force)
    AUTH = "5/minute"
    
    # Chat endpoints (moderate limits, energy system provides additional protection)
    CHAT = "30/minute"
    
    # Map/location endpoints (can be more permissive)
    MAP = "60/minute"
    MAP_LOCATIONS = "60/minute"  # Alias for map location queries
    
    # Soul browsing/discovery (moderate)
    SOULS = "40/minute"
    
    # User profile updates (stricter)
    USER_WRITE = "10/minute"
    
    # Read-only endpoints (more permissive)
    READ_ONLY = "100/minute"
    
    # Admin/Architect endpoints (very strict)
    ADMIN = "20/minute"
    
    # Time progression (strict to prevent abuse)
    TIME_ADVANCE = "10/minute"
