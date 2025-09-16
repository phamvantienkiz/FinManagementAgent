from fastapi import APIRouter, HTTPException
from app.models import User, Interaction, UserCreate
from app import services

router = APIRouter()

# -------- User --------
@router.post("/users/register")
def register_user(user: UserCreate):
    existing = None
    if user.phone:
        existing = services.get_user_by_phone(user.phone)
    elif user.telegram_id:
        existing = services.get_user_by_telegram(user.telegram_id)

    if existing:
        return {"message": "User already exists", "user": existing}

    new_user = services.create_user(user)
    return {"message": "User created", "user": new_user}

@router.get("/users/by-phone/{phone}")
def get_user_by_phone(phone: str):
    user = services.get_user_by_phone(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/by-telegram/{tid}")
def get_user_by_telegram(tid: int):
    user = services.get_user_by_telegram(tid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------- Interaction --------
@router.post("/interactions/")
def log_interaction(inter: Interaction):
    return {"message": "Interaction logged", "interaction": services.add_interaction(inter)}

@router.get("/interactions/{user_id}")
def get_interaction(user_id: str, limit: int = 10):
    return services.get_interactions(user_id, limit)
