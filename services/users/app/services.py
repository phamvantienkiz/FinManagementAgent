from app.database import supabase
from app.models import User, Interaction, UserCreate
from datetime import datetime

# ---------------- User ----------------
def create_user(user: UserCreate):
    payload = user.model_dump(exclude_none=True)
    # set server-managed fields
    now = datetime.utcnow().isoformat()
    payload.setdefault("created_at", now)
    payload.setdefault("updated_at", now)
    data = supabase.table("users").insert(payload).execute()
    return data.data[0] if data.data else None

def get_user_by_phone(phone: str):
    data = supabase.table("users").select("*").eq("phone", phone).execute()
    return data.data[0] if data.data else None

def get_user_by_telegram(tid: int):
    data = supabase.table("users").select("*").eq("telegram_id", tid).execute()
    return data.data[0] if data.data else None

def update_user(user_id: str, payload: dict):
    data = supabase.table("users").update(payload).eq("id", user_id).execute()
    return data.data[0] if data.data else None

# ---------------- Interaction ----------------
def add_interaction(inter: Interaction):
    data = supabase.table("interactions").insert(inter.model_dump(exclude_none=True)).execute()
    return data.data[0] if data.data else None

def get_interactions(user_id: str, limit: int = 10):
    data = (
        supabase.table("interactions")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return data.data
