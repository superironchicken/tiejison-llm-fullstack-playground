from pydantic import BaseModel
from typing import List,Optional

class ChatRequest(BaseModel):
    messages: List[dict]          # [{"role": "user", "content": "你好"}]
    model: Optional[str] = "qwen3.5:4b"
    stream: Optional[bool] = False
    # 前端先调 POST /conversations 拿到 id，再带上来复用同一个会话
    conversation_id: Optional[int] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"
