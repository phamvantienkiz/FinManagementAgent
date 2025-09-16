("""app package initializer: provide a shared httpx AsyncClient instance and helpers.

Main creates the client at startup by calling `init_httpx_client()` and closes it on shutdown
by calling `close_httpx_client()`.
""")
from typing import Optional
import httpx

httpx_client: Optional[httpx.AsyncClient] = None

def init_httpx_client(timeout: float = 10.0) -> httpx.AsyncClient:
	"""Create and store a shared AsyncClient. Idempotent."""
	global httpx_client
	if httpx_client is None:
		httpx_client = httpx.AsyncClient(timeout=timeout)
	return httpx_client

async def close_httpx_client() -> None:
	global httpx_client
	if httpx_client is not None:
		await httpx_client.aclose()
		httpx_client = None

