from fastapi import APIRouter, Depends, HTTPException, Body
from database import get_db
from api.auth import get_current_user
from models import ExpenseCreate
import json

router = APIRouter(prefix="/expenses", tags=["expenses"])

def load_rule(rule_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM rules WHERE id = %s AND is_active = 1", (rule_id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if not r:
        return None
    # parse approvers
    try:
        r["approvers"] = json.loads(r["approvers"]) if r.get("approvers") else []
    except:
        r["approvers"] = []
    return r

def get_manager_chain(username):
    """
    Return manager chain upwards (simple: manager, manager's manager, ...).
    Avoid infinite loops by limiting depth.
    """
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    chain = []
    current = username
    depth = 0
    while depth < 10:
        cur.execute("SELECT manager FROM users WHERE username = %s", (current,))
        row = cur.fetchone()
        if not row or not row.get("manager"):
            break
        manager = row["manager"]
        if not manager or manager in chain:
            break
        chain.append(manager)
        current = manager
        depth += 1
    cur.close()
    conn.close()
    return chain

@router.post("/", summary="Submit expense (employee)")
def create_expense(exp: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only employees can submit expenses")

    # Build approvers list:
    approvers = []
    # 1. manager chain (sequential)
    manager_chain = get_manager_chain(current_user["username"])
    if manager_chain:
        approvers.extend(manager_chain)

    # 2. If rule_id is provided, fetch rule and merge approvers (not duplicates)
    if exp.rule_id:
        rule = load_rule(exp.rule_id)
        if rule:
            # for 'specific' rule the specific_approver is required -> add if provided
            if rule["type"] in ("specific", "hybrid") and rule.get("specific_approver"):
                if rule["specific_approver"] not in approvers:
                    approvers.append(rule["specific_approver"])
            # for percentage/hybrid add approvers list (voting pool)
            if rule.get("approvers"):
                for a in rule["approvers"]:
                    if a not in approvers:
                        approvers.append(a)

    # initial comments and votes
    comments = []
    votes = []  # list of {"user": "...", "decision": "approve"|"reject"}

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO expenses (employee, amount, currency, category, description, status, approvers, comments, votes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (current_user["username"], exp.amount, exp.currency, exp.category, exp.description,
              "pending", json.dumps(approvers), json.dumps(comments), json.dumps(votes)))
        conn.commit()
        inserted_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"msg": "Expense submitted", "expense_id": inserted_id}

@router.get("/", summary="Get expenses (role filtered)")
def get_expenses(current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    if current_user["role"] == "admin":
        cur.execute("SELECT * FROM expenses ORDER BY created_at DESC")
        rows = cur.fetchall()
    elif current_user["role"] == "manager":
        # those where manager is in approvers array
        cur.execute("SELECT * FROM expenses WHERE JSON_CONTAINS(approvers, JSON_QUOTE(%s)) ORDER BY created_at DESC", (current_user["username"],))
        rows = cur.fetchall()
    else:  # employee
        cur.execute("SELECT * FROM expenses WHERE employee = %s ORDER BY created_at DESC", (current_user["username"],))
        rows = cur.fetchall()
    cur.close()
    conn.close()
    # parse json fields
    for r in rows:
        try:
            r["approvers"] = json.loads(r["approvers"]) if r.get("approvers") else []
            r["comments"] = json.loads(r["comments"]) if r.get("comments") else []
            r["votes"] = json.loads(r["votes"]) if r.get("votes") else []
        except:
            pass
    return rows

@router.post("/{expense_id}/approve", summary="Approve an expense")
def approve_expense(expense_id: int, comment: str = Body(None), current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
    exp = cur.fetchone()
    if not exp:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found")

    approvers = json.loads(exp["approvers"]) if exp.get("approvers") else []
    comments = json.loads(exp["comments"]) if exp.get("comments") else []
    votes = json.loads(exp["votes"]) if exp.get("votes") else []

    username = current_user["username"]
    # check authorization: user must be in approvers OR be admin
    if username not in approvers and current_user["role"] != "admin":
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized to approve this expense")

    # Append comment
    if comment:
        comments.append(f"{username}: {comment}")
    else:
        comments.append(f"{username}: Approved")

    # Add a vote
    votes.append({"user": username, "decision": "approve"})

    # Find any rule that might apply: simple approach - check rules table for matching approvers containing this user or sequential rules (advanced logic can be extended)
    cur.execute("SELECT * FROM rules WHERE is_active = 1")
    rules = cur.fetchall()
    active_rules = []
    for r in rules:
        try:
            r["approvers"] = json.loads(r["approvers"]) if r.get("approvers") else []
        except:
            r["approvers"] = []
        active_rules.append(r)

    # Determine final status:
    new_status = exp["status"]
    # If approvers list is sequential (manager chain) we remove current approver and move to next
    if username in approvers:
        approvers.remove(username)

    # Check for percentage rule that uses a voting pool which includes voters (if any)
    percentage_rules = [r for r in active_rules if r["type"] == "percentage"]
    specific_rules = [r for r in active_rules if r["type"] == "specific"]
    hybrid_rules = [r for r in active_rules if r["type"] == "hybrid"]

    # Helper: compute percentage approvals among a rule's approvers (based on votes recorded on expense)
    def compute_percentage(rule):
        pool = rule.get("approvers", [])
        if not pool:
            return 0
        # count approvals in votes where user is in pool
        approved = sum(1 for v in votes if v["decision"] == "approve" and v["user"] in pool)
        percent = int((approved / len(pool)) * 100)
        return percent

    # Apply specific-rule auto-approval if the approver was the specific approver
    auto_approved = False
    for r in specific_rules:
        sp = r.get("specific_approver")
        if sp and (username == sp or current_user.get("role") == sp):
            # specific approver approved -> auto-approve expense
            new_status = "approved"
            auto_approved = True
            break

    # Check percentage rules
    if not auto_approved:
        for r in percentage_rules:
            percent = compute_percentage(r)
            thr = r.get("threshold") or 0
            if percent >= thr:
                new_status = "approved"
                break

    # Check hybrid: either percent OR specific approver
    if not auto_approved:
        for r in hybrid_rules:
            thr = r.get("threshold") or 0
            percent = compute_percentage(r)
            sp = r.get("specific_approver")
            if percent >= thr:
                new_status = "approved"
                break
            # if specific approver approved in votes
            if any(v for v in votes if v["user"] == sp and v["decision"] == "approve"):
                new_status = "approved"
                break

    # If no rules apply and approvers list is empty => approve
    if not approvers and new_status == "pending":
        new_status = "approved"

    # Update DB
    cur.execute("UPDATE expenses SET status = %s, approvers = %s, comments = %s, votes = %s WHERE id = %s",
                (new_status, json.dumps(approvers), json.dumps(comments), json.dumps(votes), expense_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Approved", "status": new_status, "approvers_remaining": approvers}

@router.post("/{expense_id}/reject", summary="Reject an expense")
def reject_expense(expense_id: int, comment: str = Body(None), current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM expenses WHERE id = %s", (expense_id,))
    exp = cur.fetchone()
    if not exp:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found")

    approvers = json.loads(exp["approvers"]) if exp.get("approvers") else []
    comments = json.loads(exp["comments"]) if exp.get("comments") else []
    votes = json.loads(exp["votes"]) if exp.get("votes") else []

    username = current_user["username"]
    if username not in approvers and current_user["role"] != "admin":
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorized to reject this expense")

    if comment:
        comments.append(f"{username}: {comment}")
    else:
        comments.append(f"{username}: Rejected")

    votes.append({"user": username, "decision": "reject"})

    # For rejection, we set approvers to empty and status to rejected
    cur.execute("UPDATE expenses SET status=%s, approvers=%s, comments=%s, votes=%s WHERE id=%s",
                ("rejected", json.dumps([]), json.dumps(comments), json.dumps(votes), expense_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Expense rejected"}