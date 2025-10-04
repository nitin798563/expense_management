from fastapi import FastAPI
from api import auth, users, rules, expenses, utils
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Expense Management API (MySQL)")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rules.router)
app.include_router(expenses.router)
app.include_router(utils.router)

@app.get("/")
def root():
    return {"msg": "Expense Management API - ready"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # this allows OPTIONS, POST, GET, etc.
    allow_headers=["*"],  # allows Authorization, Content-Type, etc.
)