"""Minimal file-backed retry queue for failed interactions.

This writes JSON lines to .failed_interactions.log inside the messaging folder.
"""
import json
from pathlib import Path
from typing import Dict, Any
from app.logger import get_logger
from app.user_client import log_interaction

logger = get_logger("messaging.storage_retry")

RETRY_FILE = Path(__file__).parent / ".failed_interactions.log"


def enqueue_failed_interaction(payload: Dict[str, Any]) -> None:
	try:
		with RETRY_FILE.open("a", encoding="utf-8") as f:
			f.write(json.dumps(payload, default=str) + "\n")
		logger.info("enqueued failed interaction", {"payload": payload})
	except Exception as exc:
		logger.exception("failed to write retry file", {"error": str(exc)})


async def flush_retries() -> int:
	"""Attempt to resend queued interactions. Returns number of items flushed successfully."""
	if not RETRY_FILE.exists():
		return 0
	flushed = 0
	tmp = RETRY_FILE.with_suffix('.log.tmp')
	remaining = []
	try:
		with RETRY_FILE.open("r", encoding="utf-8") as f:
			lines = f.readlines()
		for line in lines:
			try:
				item = json.loads(line)
				if item.get("type") == "interaction":
					payload = item.get("payload")
					# attempt to resend; payload should contain user_id etc.
					try:
						await log_interaction(payload.get("user_id"), payload.get("message_text"), payload.get("direction", "in"), payload.get("telegram_message_id"), payload.get("metadata"))
						flushed += 1
					except Exception:
						remaining.append(line)
				else:
					remaining.append(line)
			except Exception:
				# corrupt line; skip
				continue
		# rewrite file with remaining
		if remaining:
			with tmp.open("w", encoding="utf-8") as f:
				f.writelines(remaining)
			tmp.replace(RETRY_FILE)
		else:
			RETRY_FILE.unlink()
	except FileNotFoundError:
		return 0
	except Exception as exc:
		logger.exception("flush_retries error", {"error": str(exc)})
	return flushed

