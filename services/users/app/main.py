from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="User Service with Supabase")

app.include_router(router, prefix="/api", tags=["User Management"])

@app.get("/")
def root():
    return {"message": "User Service is running"}
