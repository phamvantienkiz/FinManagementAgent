"""Background processing for message flow.

Runs in FastAPI BackgroundTasks to keep webhook responses fast.
"""
from typing import Dict, Any
from app.logger import get_logger
from app import user_client, agent_client, telegram_client, storage_retry

logger = get_logger("messaging.background_tasks")


async def process_message_flow(user: Dict[str, Any], chat_id: int, message_text: str, message_id: int, raw: Dict[str, Any]):
	"""Orchestrates agent call, logging and sending reply.

	- ask agent
	- log outgoing interaction
	- send message via telegram
	"""
	user_id = user.get("id")
	try:
		# get a reply from agent (or fallback)
		reply_text = await agent_client.ask_agent(user, message_text)
	except Exception as exc:
		logger.exception("agent processing failed", {"error": str(exc)})
		reply_text = "Agent tạm thời bận, vui lòng thử lại sau."

	# try to log outgoing interaction
	try:
		await user_client.log_interaction(user_id, reply_text, direction="out", telegram_message_id=None, metadata=raw)
	except Exception:
		logger.exception("failed to log outgoing interaction; enqueued")
		try:
			storage_retry.enqueue_failed_interaction({"type": "interaction", "payload": {"user_id": user_id, "message_text": reply_text, "direction": "out", "telegram_message_id": None, "metadata": {"raw": raw}}})
		except Exception:
			logger.exception("failed to enqueue outgoing interaction")

	# try to send message
	try:
		await telegram_client.send_message(chat_id, reply_text)
	except Exception:
		logger.exception("failed to send message to telegram");
		# optionally we could retry/send later; for now we log
