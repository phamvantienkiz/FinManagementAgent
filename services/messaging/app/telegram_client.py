("""Simple wrapper over Telegram Bot API using httpx AsyncClient.

Raises TelegramClientError on network or HTTP errors.
""")
from typing import Optional, Dict, Any
from app import __init__ as app_pkg
from app.config import settings
from app.logger import get_logger
import httpx

logger = get_logger("messaging.telegram_client")


class TelegramClientError(Exception):
	pass


def _make_url(method: str) -> str:
	return f"https://api.telegram.org/bot{settings.BOT_TOKEN}/{method}"


async def send_message(chat_id: int, text: str, parse_mode: Optional[str] = None) -> Dict[str, Any]:
	client = app_pkg.httpx_client
	if client is None:
		client = app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	url = _make_url("sendMessage")
	payload = {"chat_id": chat_id, "text": text}
	if parse_mode:
		payload["parse_mode"] = parse_mode
	try:
		resp = await client.post(url, json=payload)
		if resp.status_code >= 500 or resp.status_code == 429:
			logger.error("telegram send_message server error", {"status": resp.status_code, "text": resp.text})
			raise TelegramClientError(f"Telegram error {resp.status_code}")
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError as exc:
		logger.exception("telegram http error", {"error": str(exc)})
		raise TelegramClientError(str(exc))


async def send_typing(chat_id: int) -> Dict[str, Any]:
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	url = _make_url("sendChatAction")
	try:
		resp = await client.post(url, json={"chat_id": chat_id, "action": "typing"})
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError as exc:
		logger.exception("telegram typing error", {"error": str(exc)})
		raise TelegramClientError(str(exc))


async def set_webhook(url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	webhook_url = _make_url("setWebhook")
	payload = {"url": url}
	if secret_token:
		payload["secret_token"] = secret_token
	try:
		resp = await client.post(webhook_url, json=payload)
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError as exc:
		logger.exception("set_webhook error", {"error": str(exc)})
		raise TelegramClientError(str(exc))


async def delete_webhook() -> Dict[str, Any]:
	client = app_pkg.httpx_client or app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	url = _make_url("deleteWebhook")
	try:
		resp = await client.post(url)
		resp.raise_for_status()
		return resp.json()
	except httpx.HTTPError as exc:
		logger.exception("delete_webhook error", {"error": str(exc)})
		raise TelegramClientError(str(exc))

