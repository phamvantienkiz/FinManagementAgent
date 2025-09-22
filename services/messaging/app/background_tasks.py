"""Background processing for message flow.

Runs in FastAPI BackgroundTasks to keep webhook responses fast.
"""

from app.logger import get_logger
from app import agent_client, telegram_client

logger = get_logger("messaging.background_tasks")


from fastapi import HTTPException
# ... (existing imports)

async def process_message_flow(user_id: str, chat_id: int, message_text: str):
	"""Orchestrates agent call and reply sending.

	- ask agent
	- send message via telegram
	"""
	try:
		# get a reply from agent (or fallback)
		reply_text = await agent_client.ask_agent(user_id, message_text)
	except Exception as exc:
		logger.exception("agent processing failed", {"error": str(exc)})
		reply_text = "Agent tạm thời bận, vui lòng thử lại sau."

	# try to send message
	try:
		await telegram_client.send_message(chat_id, reply_text)
	except Exception:
		logger.exception("failed to send message to telegram");
		# optionally we could retry/send later; for now we log
