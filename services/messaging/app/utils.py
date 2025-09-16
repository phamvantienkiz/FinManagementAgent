("""Utility helpers for parsing Telegram updates and small helpers used across the app.""")
from typing import Dict, Any, Optional
from uuid import uuid4
import threading

# simple thread-local storage for correlation id
_tls = threading.local()


def set_correlation_id(cid: Optional[str]) -> None:
	_tls.correlation_id = cid


def get_correlation_id() -> Optional[str]:
	return getattr(_tls, "correlation_id", None)


def new_correlation_id() -> str:
	cid = str(uuid4())
	set_correlation_id(cid)
	return cid


def safe_extract_text(message: Dict[str, Any]) -> str:
	"""Extract reasonable text content from various Telegram update shapes."""
	if not message:
		return ""
	# text message
	if "text" in message and message.get("text"):
		return message["text"]
	# captioned media
	if "caption" in message and message.get("caption"):
		return message["caption"]
	# callback_query
	if "callback_query" in message:
		cb = message["callback_query"]
		return cb.get("data", "")
	# fallback: indicate non-text content
	return "[non-text message]"


def build_display_name(chat: Dict[str, Any]) -> str:
	parts = []
	if chat.get("first_name"):
		parts.append(chat.get("first_name"))
	if chat.get("last_name"):
		parts.append(chat.get("last_name"))
	if chat.get("username") and not parts:
		parts.append(chat.get("username"))
	return " ".join(parts) if parts else "Unknown"


def parse_update(update_json: Dict[str, Any]) -> Dict[str, Any]:
	"""Normalize a Telegram update into a dict used by the app.

	Returns: {chat_id, telegram_id, text, message_id, raw, is_command, command, chat}
	"""
	result: Dict[str, Any] = {"raw": update_json}
	message = update_json.get("message") or update_json.get("edited_message") or {}
	# callback_query payload
	if "callback_query" in update_json:
		cq = update_json["callback_query"]
		message = cq.get("message") or {}
		result["is_callback"] = True

	chat = message.get("chat", {})
	from_user = message.get("from") or update_json.get("from") or {}
	text = safe_extract_text(update_json) or safe_extract_text(message)

	# commands start with '/'
	is_command = False
	command = None
	if text and text.startswith("/"):
		is_command = True
		command = text.split()[0]

	result.update({
		"chat_id": chat.get("id") or from_user.get("id"),
		"telegram_id": from_user.get("id"),
		"text": text,
		"message_id": message.get("message_id"),
		"is_command": is_command,
		"command": command,
		"chat": chat,
	})
	return result

