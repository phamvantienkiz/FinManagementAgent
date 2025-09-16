("""Simple logger factory that returns preconfigured logging.Logger.

It reads LOG_LEVEL from config and emits a compact JSON-like message to console.
""")
import logging
import json
from typing import Any
from app.config import settings
from app import utils


class SimpleJSONFormatter(logging.Formatter):
	def format(self, record: logging.LogRecord) -> str:
		payload = {
			"level": record.levelname,
			"name": record.name,
			"message": record.getMessage(),
		}
		# include correlation id if present in record
		cid = getattr(record, "correlation_id", None) or utils.get_correlation_id()
		if cid:
			payload["correlation_id"] = cid
		# include extra fields if any
		if record.args and isinstance(record.args, dict):
			payload.update(record.args)
		return json.dumps(payload, default=str)


def get_logger(name: str) -> logging.Logger:
	level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
	logger = logging.getLogger(name)
	logger.setLevel(level)
	if not logger.handlers:
		ch = logging.StreamHandler()
		ch.setLevel(level)
		ch.setFormatter(SimpleJSONFormatter())
		logger.addHandler(ch)
	return logger

