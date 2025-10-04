from fastapi import APIRouter, Depends, HTTPException, Body
from database import get_db
from api.auth import get_current_user
from models import ExpenseCreate
import json, datetime

router = APIRouter(prefix="/expenses", tags=["expenses"])

# ---------------------------------
# Helper: Load rule
# ---------------------------------
def load_rule(rule_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM rules WHERE id = %s AND is_active = 1", (rule_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if not r:
        return None
    try:
        r["approvers"] = json.loads(r.get("approvers") or "[]")
    except:
        r["approvers"] = []
    return r

# ---------------------------------
# Helper: Manager chain (up to 10 levels)
# ---------------------------------
def get_manager_chain(username):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    chain = []
    current = username
    for _ in range(10):
        cur.execute("SELECT manager FROM users WHERE username = %s", (current,))
        row = cur.fetchone()
        if not row or not row.get("manager"):
            break
        manager = row["manager"]
        if not manager or manager in chain:
            break
        chain.append(manager)
        current = manager
    cur.close()
    conn.close()
    return chain

# ---------------------------------
# Helper: Conditional Approvers
# ---------------------------------
def get_conditional_approvers(amount, category):
    """Auto-select approvers based on 'conditional_rules' table"""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM conditional_rules")
    rules = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rules:
        field = r.get("condition_field")
        op = r.get("operator")
        val = r.get("value")
        approver = r.get("approver")

        # Compare numeric (amount)
        if field == "amount":
            try:
                amt = float(amount)
                val_f = float(val)
                if op == ">" and amt > val_f: result.append(approver)
                elif op == "<" and amt < val_f: result.append(approver)
                elif op in ("=", "==") and amt == val_f: result.append(approver)
            except:
                continue

        # Compare text (category)
        if field == "category":
            if op in ("=", "==") and category.lower() == val.lower():
                result.append(approver)

    return list(set(result))

# ---------------------------------
# POST /expenses — Employee submits
# ---------------------------------
@router.post("/", summary="Submit expense (employee)")
def create_expense(exp: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only employees can submit expenses")

    approvers = []

    # Step 1️⃣ Manager chain
    approvers.extend(get_manager_chain(current_user["username"]))

    # Step 2️⃣ Rule-based approvers
    if exp.rule_id:
        rule = load_rule(exp.rule_id)
        if rule:
            for a in rule.get("approvers", []):
                if a not in approvers:
                    approvers.append(a)
            if rule.get("specific_approver") and rule["specific_approver"] not in approvers:
                approvers.append(rule["specific_approver"])

    # Step 3️⃣ Conditional approvers (auto rules)
    for a in get_conditional_approvers(exp.amount, exp.category):
        if a not in approvers:
            approvers.append(a)

    comments, votes = [], []

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO expenses (employee, amount, currency, category, description, status, approvers, comments, votes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            current_user["username"], exp.amount, exp.currency, exp.category, exp.description,
            "pending", json.dumps(approvers), json.dumps(comments), json.dumps(votes)
        ))
        conn.commit()
        expense_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

    return {
        "msg": "Expense submitted successfully",
        "expense_id": expense_id,
        "approvers": approvers
    }

# ---------------------------------
# GET /expenses — role filtered
# ---------------------------------
@router.get("/", summary="Get expenses (role filtered)")
def get_expenses(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    if current_user["role"] == "admin":
        cur.execute("SELECT * FROM expenses ORDER BY created_at DESC")
    elif current_user["role"] == "manager":
        # Managers see all expenses from their team
        cur.execute("""
            SELECT * FROM expenses 
            WHERE employee IN (SELECT username FROM users WHERE manager = %s)
            OR status IN ('pending','approved','rejected')
            ORDER BY created_at DESC
        """, (current_user["username"],))
    else:
        cur.execute("SELECT * FROM expenses WHERE employee = %s ORDER BY created_at DESC", (current_user["username"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    for r in rows:
        for key in ["approvers", "comments", "votes"]:
            try:
                r[key] = json.loads(r.get(key) or "[]")
            except:
                r[key] = []
    return rows

# ---------------------------------
# POST /approve
# ---------------------------------
@router.post("/{expense_id}/approve", summary="Approve an expense")
def approve_expense(expense_id: int, comment: str = Body(None), current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM expenses WHERE id=%s", (expense_id,))
    exp = cur.fetchone()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    approvers = json.loads(exp["approvers"]) if exp.get("approvers") else []
    comments = json.loads(exp["comments"]) if exp.get("comments") else []
    votes = json.loads(exp["votes"]) if exp.get("votes") else []

    username = current_user["username"]

    if username not in approvers and current_user["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Not authorized")

    comments.append(f"{username}: {comment or 'Approved'}")
    votes.append({"user": username, "decision": "approve", "at": datetime.datetime.utcnow().isoformat()})

    if username in approvers:
        approvers.remove(username)

    new_status = exp["status"]
    if not approvers:
        new_status = "approved"

    cur.execute("UPDATE expenses SET status=%s, approvers=%s, comments=%s, votes=%s WHERE id=%s",
                (new_status, json.dumps(approvers), json.dumps(comments), json.dumps(votes), expense_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Expense approved", "status": new_status, "remaining": approvers}

# ---------------------------------
# POST /reject
# ---------------------------------
@router.post("/{expense_id}/reject", summary="Reject an expense")
def reject_expense(expense_id: int, comment: str = Body(None), current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM expenses WHERE id=%s", (expense_id,))
    exp = cur.fetchone()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    approvers = json.loads(exp["approvers"]) if exp.get("approvers") else []
    comments = json.loads(exp["comments"]) if exp.get("comments") else []
    votes = json.loads(exp["votes"]) if exp.get("votes") else []

    username = current_user["username"]

    if username not in approvers and current_user["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Not authorized")

    comments.append(f"{username}: {comment or 'Rejected'}")
    votes.append({"user": username, "decision": "reject", "at": datetime.datetime.utcnow().isoformat()})

    cur.execute("UPDATE expenses SET status=%s, approvers=%s, comments=%s, votes=%s WHERE id=%s",
                ("rejected", json.dumps([]), json.dumps(comments), json.dumps(votes), expense_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Expense rejected"}