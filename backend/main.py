from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.health import router as health_router
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.forms import router as forms_router
from routes.sessions import router as sessions_router
from routes.chat import router as chat_router


app = FastAPI(
    title="Government Form Assistant API",
    description="Backend API for the Government Form Assistant",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(forms_router)
app.include_router(sessions_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "Government Form Assistant Backend is running!"
    }