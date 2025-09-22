"""
This tool is a placeholder for a more complex RAG (Retrieval-Augmented Generation) implementation.
It simulates retrieving relevant information from a vector database (like Pinecone)
to provide context for the LLM.
"""
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from app.utils.pinecone import rag_query

class RAGInput(BaseModel):
    query: str = Field(..., description="The query to search for in the vector database.")
    user_id: str = Field(..., description="The user's ID to filter the search.")
    agent_context: str = Field(..., description="The agent's context to search within.")

class RAGTool(BaseTool):
    name: str = "RAG Tool"
    description: str = "Retrieves relevant information from a vector database to provide context."
    args_schema: Type[BaseModel] = RAGInput

    def _run(self, query: str, user_id: str, agent_context: str) -> str:
        """
        Uses the rag_query function from pinecone.py to retrieve information.
        """
        return rag_query(query=query, agent_context=agent_context, user_id=user_id)
