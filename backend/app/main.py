from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, requests, users  # импортируем users

app = FastAPI(title="Repair Requests Service")

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(requests.router)
app.include_router(users.router)  # теперь app уже определён

@app.get("/")
async def root():
    return {"message": "Repair Requests API"}