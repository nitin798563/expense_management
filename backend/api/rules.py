# api/rules.py
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from models import RuleCreate
from api.auth import get_current_user

import json

router = APIRouter(prefix="/rules", tags=["rules"])

def admin_only(user):
    return user.get("role") == "admin"

@router.post("/", summary="Create an approval rule (admin)")
def create_rule(rule: RuleCreate, current_user: dict = Depends(get_current_user)):
    if not admin_only(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO rules (name, type, threshold, approvers, specific_approver, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rule.name, rule.type, rule.threshold, json.dumps(rule.approvers or []), rule.specific_approver, int(rule.is_active)))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"msg": "Rule created"}

@router.get("/", summary="List rules (admin)")
def list_rules(current_user: dict = Depends(get_current_user)):
    if not admin_only(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM rules")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # parse JSON fields
    for r in rows:
        if r.get("approvers"):
            try:
                r["approvers"] = json.loads(r["approvers"])
            except:
                r["approvers"] = []
    return rows

@router.get("/{rule_id}", summary="Get rule by id (admin)")
def get_rule(rule_id: int, current_user: dict = Depends(get_current_user)):
    if not admin_only(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM rules WHERE id = %s", (rule_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="Rule not found")
    try:
        r["approvers"] = json.loads(r["approvers"]) if r.get("approvers") else []
    except:
        r["approvers"] = []
    return r

@router.put("/{rule_id}", summary="Update rule (admin)")
def update_rule(rule_id: int, rule: RuleCreate, current_user: dict = Depends(get_current_user)):
    if not admin_only(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE rules SET name=%s, type=%s, threshold=%s, approvers=%s, specific_approver=%s, is_active=%s
            WHERE id=%s
        """, (rule.name, rule.type, rule.threshold, json.dumps(rule.approvers or []), rule.specific_approver, int(rule.is_active), rule_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"msg": "Rule updated"}

@router.delete("/{rule_id}", summary="Delete rule (admin)")
def delete_rule(rule_id: int, current_user: dict = Depends(get_current_user)):
    if not admin_only(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM rules WHERE id = %s", (rule_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Rule deleted"}