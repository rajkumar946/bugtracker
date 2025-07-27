from fastapi import FastAPI
from app.api.v1 import auth, users, projects, bugs

app = FastAPI(title="Bug Tracker API")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(bugs.router, prefix="/api/projects", tags=["Bugs"])

@app.get("/")
async def root():
    return {"message": "Bug Tracker API is running"}
