"""Client to call Agent service (AI) and return a string reply.

If AGENT_SERVICE_BASE not configured, fall back to simple echo logic.
"""
from typing import Dict, Any
from app import __init__ as app_pkg
from app.config import settings
from app.logger import get_logger
import httpx

logger = get_logger("messaging.agent_client")


async def ask_agent(user: Dict[str, Any], text: str) -> str:
    # simple fallback
    if not settings.AGENT_SERVICE_BASE:
        logger.info("AGENT_SERVICE_BASE not configured, using fallback")
        # echo with hint
        return f"Tạm thời không có agent; bạn nói: {text}\n(Thử lại sau hoặc dùng lệnh /help)"

    client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
    url = f"{settings.AGENT_SERVICE_BASE}/api/respond"
    payload = {"user": user, "text": text}
    try:
        resp = await client.post(url, json=payload, timeout=settings.REQUEST_TIMEOUT)
        resp.raise_for_status()
        body = resp.json()
        if isinstance(body, dict) and "reply" in body:
            return body.get("reply")
        # if structured differently, try to stringify
        return str(body)
    except httpx.HTTPError as exc:
        logger.exception("agent call failed", {"error": str(exc)})
        return "Agent tạm thời bận, vui lòng thử lại sau."
