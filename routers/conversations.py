from fastapi import APIRouter

from schemas import ConversationCreate
from database import create_conversation, list_conversations, get_messages

router = APIRouter()


@router.post("/conversations")
async def create(payload: ConversationCreate):
    """新建一个会话，返回它的 id。前端发送消息前先调这个。"""
    conversation_id = create_conversation(payload.title)
    return {"id": conversation_id, "title": payload.title}


@router.get("/conversations")
async def list_all():
    """返回所有会话，供侧边栏渲染。"""
    return list_conversations()


@router.get("/conversations/{conversation_id}/messages")
async def messages(conversation_id: int):
    """返回某个会话的历史消息，供点击侧边栏时重建对话。"""
    return get_messages(conversation_id)
