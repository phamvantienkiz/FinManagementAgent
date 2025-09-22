from fastapi import FastAPI, Header, HTTPException, BackgroundTasks, Request
from app.config import settings
from app.logger import get_logger
from app import utils, http_client
from app.background_tasks import process_message_flow
import time
import cachetools

logger = get_logger("messaging.main")

app = FastAPI(title="Messaging Service")

# Simple in-memory cache for message deduplication
processed_messages = cachetools.TTLCache(maxsize=10000, ttl=300)

@app.on_event("startup")
async def startup():
	# init shared httpx client
	http_client.init_httpx_client(timeout=settings.REQUEST_TIMEOUT)

@app.on_event("shutdown")
async def shutdown():
	await http_client.close_httpx_client()

@app.get("/health")
async def health():
	return {"ok": True}

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

	if not telegram_id or not chat_id or not message_id:
		# nothing to do
		return {"ok": True}

	# Deduplication check
	if message_id in processed_messages:
		logger.info(f"Duplicate message_id received: {message_id}. Ignoring.")
		return {"ok": True}
	
	processed_messages[message_id] = time.time()

	# schedule background processing
	background_tasks.add_task(process_message_flow, str(telegram_id), chat_id, text)

	return {"ok": True}
