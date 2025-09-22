from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.utils.dispatcher import dispatcher
import uvicorn
import re

app = FastAPI(title="AI Agent Service")

class QueryRequest(BaseModel):
    user_id: str
    query: str

@app.post("/api/respond")
async def process_query(request: QueryRequest):
    """
    Main endpoint to receive queries from the messaging service.
    It determines the agent key from the query command and dispatches it.
    """

    # Check for command-based routing first
    command_match = re.match(r'/(\w+)', request.query)
    agent_key = None
    if command_match:
        command = command_match.group(1)
        # Map command to agent_key
        if command in ["financial_manager", "investment_advisor", "financial_analyst"]:
            agent_key = command

    try:
        # Dispatcher handles both command-based and LLM-based routing
        response = dispatcher(query=request.query, user_id=request.user_id, agent_key=agent_key)
        return {"reply": response}
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during dispatch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)