import json
import logging
import time
import uuid

from starlette.requests import Request

logger = logging.getLogger("lifelink.audit")


SENSITIVE_QUERY_KEYS = {"token", "access_token", "password", "secret", "api_key"}


def _safe_query(request: Request) -> dict[str, str]:
    return {
        key: value
        for key, value in request.query_params.items()
        if key.lower() not in SENSITIVE_QUERY_KEYS
    }


async def audit_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.exception(
            json.dumps(
                {
                    "event": "request.error",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": _safe_query(request),
                    "duration_ms": duration_ms,
                },
                separators=(",", ":"),
            )
        )
        raise

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "event": "request.completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": _safe_query(request),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
            separators=(",", ":"),
        )
    )
    response.headers["X-Request-ID"] = request_id
    return response
