# api/users.py
from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_current_user, get_password_hash
from database import get_db
from models import UserCreate

router = APIRouter(prefix="/users", tags=["users"])

def is_admin(user: dict):
    return user.get("role") == "admin"

@router.post("/", summary="Create user (admin only)")
def create_user(user_in: UserCreate, current_user: dict = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    hashed = get_password_hash(user_in.password)
    try:
        cur.execute("INSERT INTO users (username, password, role, manager) VALUES (%s, %s, %s, %s)",
                    (user_in.username, hashed, user_in.role, user_in.manager))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"msg": "User created by admin"}

@router.get("/", summary="List users (admin only)")
def list_users(current_user: dict = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, role, manager, created_at FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@router.delete("/{username}", summary="Delete user (admin only)")
def delete_user(username: str, current_user: dict = Depends(get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = %s", (username,))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "User deleted"}