from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routers.chat import router as chat_router
from routers.conversations import router as conversations_router

from database import init_db

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 解决前后端跨域问题

@app.get("/")
async def root():
    return {"message": "chat已经启动"}

app.include_router(chat_router)
app.include_router(conversations_router)
