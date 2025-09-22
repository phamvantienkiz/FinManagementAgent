"""
Manages the shared httpx.AsyncClient instance for the application.
"""
from typing import Optional
import httpx

_httpx_client: Optional[httpx.AsyncClient] = None

def init_httpx_client(timeout: float = 10.0) -> httpx.AsyncClient:
    """Create and store a shared AsyncClient. Idempotent."""
    global _httpx_client
    if _httpx_client is None:
        _httpx_client = httpx.AsyncClient(timeout=timeout)
    return _httpx_client

async def close_httpx_client() -> None:
    """Close the shared AsyncClient."""
    global _httpx_client
    if _httpx_client is not None:
        await _httpx_client.aclose()
        _httpx_client = None

def get_httpx_client() -> httpx.AsyncClient:
    """Get the shared AsyncClient, initializing if needed."""
    global _httpx_client
    if _httpx_client is None:
        return init_httpx_client()
    return _httpx_client
