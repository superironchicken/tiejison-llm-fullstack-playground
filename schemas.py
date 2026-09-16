from pydantic import BaseModel
from typing import List,Optional

class ChatRequest(BaseModel):
    messages: List[dict]          # [{"role": "user", "content": "你好"}]
    model: Optional[str] = "qwen3.5:4b"
    stream: Optional[bool] = False
