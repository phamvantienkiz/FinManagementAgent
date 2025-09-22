"""Client to call Agent service (AI) and return a string reply.

If AGENT_SERVICE_BASE not configured, fall back to simple echo logic.
"""
from typing import Dict, Any
from app import http_client
from app.markdown_utils import md_to_text
from app.config import settings
from app.logger import get_logger
import httpx

logger = get_logger("messaging.agent_client")


async def ask_agent(user_id: str, query: str) -> str:
    # simple fallback
    if not settings.AGENT_SERVICE_BASE:
        logger.info("AGENT_SERVICE_BASE not configured, using fallback")
        # echo with hint
        return f"Tạm thời không có agent; bạn nói: {query}\n(Thử lại sau hoặc dùng lệnh /help)"

    # Use the shared httpx client
    client = http_client.get_httpx_client()
    try:
        resp = await client.post(
            f"{settings.AGENT_SERVICE_BASE}/api/respond",
            json={"user_id": user_id, "query": query} # FIX: Changed 'message' to 'query'
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(f"Agent API request failed: Status {exc.response.status_code} - {exc.response.text}")
        raise
    except httpx.RequestError as exc:
        logger.error(f"Agent API request failed: {exc}")
        raise

    body = resp.json()
    reply = body.get("reply")

    if isinstance(reply, dict):
        # Prioritize 'raw', then 'text'/'content', then from 'tasks_output'
        if reply.get("raw"):
            return md_to_text(reply["raw"])  # convert markdown -> text
        if reply.get("text"):
            return md_to_text(reply["text"])  # convert markdown -> text
        if reply.get("content"):
            return md_to_text(reply["content"])  # convert markdown -> text
        
        tasks = reply.get("tasks_output")
        if isinstance(tasks, list) and len(tasks) > 0:
            first_task = tasks[0]
            if isinstance(first_task, dict):
                if first_task.get("raw"):
                    return md_to_text(first_task["raw"])  # convert markdown -> text
                if first_task.get("summary"):
                    return md_to_text(first_task["summary"])  # convert markdown -> text
        
        # Fallback to stringifying the whole reply object if no specific field is found
    return md_to_text(str(reply))
    
    if isinstance(reply, str):
        return md_to_text(reply)

    # if structured differently, try to stringify the whole body
    return md_to_text(str(body))
