from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.utils.logger import get_logger

logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore
        logger.info({
            "msg": "Request",
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        })
        response = await call_next(request)
        logger.info({
            "msg": "Response",
            "status": response.status_code,
            "path": request.url.path,
        })
        return response
