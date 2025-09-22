from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import json

class BraveSearchInput(BaseModel):
    query: str = Field(..., description="Search query to look up")

class BraveSearchTool(BaseTool):
    name: str = "Brave Search"
    description: str = "Search the web for current information using Brave Search API"
    args_schema: Type[BaseModel] = BraveSearchInput

    def _run(self, query: str) -> str:
        api_key = self.config.get("brave_api_key")
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": 10
        }
        
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params
        )
        
        results = response.json()
        return json.dumps(results.get('web', {}).get('results', []))