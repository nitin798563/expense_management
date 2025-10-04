
from pydantic import BaseModel
from typing import Optional, List

# Auth / Users
class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # admin, manager, employee, cfo, etc
    manager: Optional[str] = None

# Expense creation
class ExpenseCreate(BaseModel):
    amount: float
    currency: str
    category: Optional[str] = None
    description: Optional[str] = None
    rule_id: Optional[int] = None  # optional, to tie a rule to this expense

# Basic expense out
class ExpenseOut(BaseModel):
    id: int
    employee: str
    amount: float
    currency: str
    category: Optional[str]
    description: Optional[str]
    status: str
    approvers: Optional[List[str]]
    comments: Optional[List[str]]
    votes: Optional[List[dict]]

# Rule create/update
class RuleCreate(BaseModel):
    name: str
    type: str  # 'percentage' | 'specific' | 'hybrid' | 'sequential'
    threshold: Optional[int] = None
    approvers: Optional[List[str]] = None
    specific_approver: Optional[str] = None
    is_active: Optional[bool] = True