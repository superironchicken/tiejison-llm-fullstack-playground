from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List,Optional
from openai import OpenAI

from fastapi.middleware.cors import CORSMiddleware

import os
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 解决跨域问题

@app.get("/")
async def root():
    return {"message": "chat已经启动"}

class ChatRequest(BaseModel):
    messages: List[dict]          # [{"role": "user", "content": "你好"}]
    model: Optional[str] = "qwen3.5:4b"
    stream: Optional[bool] = False

@app.post("/chat")
async def start_chat(request: ChatRequest):
    api_key = os.environ.get("OLLAMA_API_KEY", "ollama")
    client = OpenAI(
        base_url='http://localhost:11434/v1/',
        api_key='ollama',  
    )
    if not request.stream :
        try:
            response = client.chat.completions.create(
                messages=request.messages,
                model=request.model,  # 使用你下载的模型
                stream= False
            )
            return {
                "result": response.choices[0].message.content
            }
        except Exception as e:
            print(f"[error]:{e}")
            raise HTTPException(status_code=500, detail=str(e))


    else:
        try:
            response = client.chat.completions.create(
                messages=request.messages,
                model=request.model,
                stream=True
            )

            def generate():
                for chunk in response:
                    content = chunk.choices[0].delta.content

                    if content:
                        yield content
            return StreamingResponse(
                    generate(),
                    media_type="text/plain"
                )

                
            
        except Exception as e:
            print(f"[error]:{e}")
            raise HTTPException(status_code=500, detail=str(e))


