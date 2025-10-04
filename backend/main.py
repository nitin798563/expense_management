from fastapi import FastAPI
from api import auth, users, rules, expenses, utils

app = FastAPI(title="Expense Management API (MySQL)")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rules.router)
app.include_router(expenses.router)
app.include_router(utils.router)

@app.get("/")
def root():
    return {"msg": "Expense Management API - ready"}