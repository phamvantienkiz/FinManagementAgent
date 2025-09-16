from fastapi import FastAPI, Header, HTTPException, BackgroundTasks, Request
from app.config import settings
from app.logger import get_logger
from app import __init__ as app_pkg
from app import utils, user_client, storage_retry
from app.background_tasks import process_message_flow

logger = get_logger("messaging.main")

app = FastAPI(title="Messaging Service")

@app.on_event("startup")
async def startup():
	# init shared httpx client
	app_pkg.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)
	# attempt to flush retries
	try:
		count = await storage_retry.flush_retries()
		logger.info("flush_retries completed", {"count": count})
	except Exception:
		logger.exception("startup flush_retries failed")

@app.on_event("shutdown")
async def shutdown():
	await app_pkg.close_httpx_client()

@app.get("/health")
async def health():
	return {"ok": True}

@app.post("/admin/flush-retries")
async def admin_flush_retries(x_admin_key: str | None = Header(None)):
	# in real app protect this endpoint
	count = await storage_retry.flush_retries()
	return {"flushed": count}

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks, x_telegram_bot_api_secret_token: str | None = Header(None)):
	# optional security: validate secret token
	if settings.WEBHOOK_SECRET_TOKEN and settings.WEBHOOK_SECRET_TOKEN != x_telegram_bot_api_secret_token:
		raise HTTPException(status_code=403, detail="Invalid secret token")

	data = await request.json()
	# set correlation id for logs
	utils.new_correlation_id()
	parsed = utils.parse_update(data)
	chat_id = parsed.get("chat_id")
	telegram_id = parsed.get("telegram_id")
	text = parsed.get("text")
	message_id = parsed.get("message_id")

	if not telegram_id or not chat_id:
		# nothing to do
		return {"ok": True}

	# get or create user first (needed for dedupe using user_id)
	try:
		user = await user_client.get_user_by_telegram(telegram_id)
	except Exception:
		logger.exception("get_user_by_telegram failed; attempting to register")
		user = None

	if not user:
		try:
			# build minimal chat object from parsed
			chat_obj = parsed.get("chat") or {}
			user = await user_client.register_user_from_telegram(telegram_id, chat_obj)
		except Exception:
			logger.exception("register_user_from_telegram failed")
			# quick response to Telegram; enqueue interaction for later
			return {"ok": True}

	# dedupe now that we have user_id
	if message_id:
		try:
			if await user_client.interaction_exists_by_telegram_message_id(user.get("id"), message_id):
				return {"ok": True}
		except Exception:
			logger.exception("dedupe check failed")

	# log incoming interaction; if fails, it will be enqueued
	try:
		await user_client.log_interaction(user.get("id"), text, direction="in", telegram_message_id=message_id, metadata=parsed.get("raw"))
	except Exception:
		logger.exception("log incoming failed; enqueued")

	# schedule background processing
	background_tasks.add_task(process_message_flow, user, chat_id, text, message_id, parsed.get("raw"))

	return {"ok": True}
