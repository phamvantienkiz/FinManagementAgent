("""Client wrapper for User Service HTTP API.

Provides methods to get/register users and log interactions.
Raises UserServiceError on unexpected failures.
""")
from typing import Optional, Dict, Any, List
from app import __init__ as app_pkg
from app.config import settings
from app.logger import get_logger
from app import storage_retry
import httpx

logger = get_logger("messaging.user_client")


class UserServiceError(Exception):
	pass


def _base_headers() -> Dict[str, str]:
	# if you have an internal API key, include here
	return {"content-type": "application/json"}


async def get_user_by_telegram(telegram_id: int) -> Optional[Dict[str, Any]]:
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	url = f"{settings.USER_SERVICE_BASE}/api/users/by-telegram/{telegram_id}"
	try:
		resp = await client.get(url, headers=_base_headers())
		if resp.status_code == 404:
			return None
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError as exc:
		logger.exception("user service get_user_by_telegram failed", {"error": str(exc)})
		raise UserServiceError(str(exc))


async def register_user_from_telegram(telegram_id: int, chat_obj: Dict[str, Any]) -> Dict[str, Any]:
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	display_name = chat_obj.get("first_name", "") + (" " + chat_obj.get("last_name", "") if chat_obj.get("last_name") else "")
	payload = {
		"telegram_id": telegram_id,
		"phone": None,
		"full_name": display_name.strip() or None,
		"email": None,
	}
	url = f"{settings.USER_SERVICE_BASE}/api/users/register"
	try:
		resp = await client.post(url, json=payload, headers=_base_headers())
		resp.raise_for_status()
		body = resp.json()
		# handle both shapes: {message, user} or direct user
		if isinstance(body, dict) and "user" in body:
			return body["user"]
		return body
	except httpx.HTTPError as exc:
		logger.exception("register user failed", {"error": str(exc)})
		raise UserServiceError(str(exc))


async def log_interaction(user_id: str, message_text: str, direction: str = "in", telegram_message_id: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	payload = {
		"user_id": user_id,
		"telegram_message_id": telegram_message_id,
		"direction": direction,
		"message_text": message_text,
		"metadata": metadata,  # already structured by caller
	}
	url = f"{settings.USER_SERVICE_BASE}/api/interactions/"
	try:
		resp = await client.post(url, json=payload, headers=_base_headers())
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError as exc:
		# enqueue to retry queue and return sentinel
		logger.exception("log_interaction failed, enqueuing", {"error": str(exc), "payload": payload})
		try:
			storage_retry.enqueue_failed_interaction({"type": "interaction", "payload": payload})
		except Exception:
			logger.exception("failed to enqueue interaction")
		raise UserServiceError(str(exc))


async def get_interactions(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
	"""Fetch recent interactions for a user for dedupe or context."""
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	url = f"{settings.USER_SERVICE_BASE}/api/interactions/{user_id}?limit={limit}"
	try:
		resp = await client.get(url, headers=_base_headers())
		if resp.status_code == 200:
			return resp.json() if isinstance(resp.json(), list) else []
		if resp.status_code == 404:
			return []
		resp.raise_for_status()
		return []
	except httpx.HTTPError:
		return []


async def interaction_exists_by_telegram_message_id(user_id: str, telegram_message_id: int, limit: int = 30) -> bool:
	"""Check within recent interactions if a telegram_message_id already logged."""
	interactions = await get_interactions(user_id, limit=limit)
	for it in interactions:
		if it.get("telegram_message_id") == telegram_message_id:
			return True
	return False

