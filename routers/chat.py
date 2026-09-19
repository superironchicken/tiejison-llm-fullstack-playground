from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from llm import get_client
from schemas import ChatRequest
from database import create_conversation, save_message

router = APIRouter()


@router.post("/chat")
async def start_chat(request: ChatRequest):
    client = get_client()

    if not request.messages:
        raise HTTPException(status_code=400, detail="messages 不能为空")

    last_user_message = request.messages[-1]["content"]

    # 方案 B：前端先建好会话再带 conversation_id 过来，这里直接复用
    if request.conversation_id is None:
        # 兼容旧调用：没传会话 id 就临时新建一个
        conversation_id = create_conversation(last_user_message[:30])
    else:
        conversation_id = request.conversation_id

    save_message(conversation_id, "user", last_user_message)

    if not request.stream:
        try:
            response = client.chat.completions.create(
                messages=request.messages,
                model=request.model,
                stream=False,
            )
            content = response.choices[0].message.content
            save_message(conversation_id, "assistant", content)
            return {
                "result": content,
                "conversation_id": conversation_id,
            }
        except Exception as e:
            print(f"[error]:{e}")
            raise HTTPException(status_code=500, detail=str(e))

    else:
        try:
            response = client.chat.completions.create(
                messages=request.messages,
                model=request.model,
                stream=True,
            )

            def generate():
                # 流式边吐边攒，结束后一次性写入
                full = ""
                for chunk in response:
                    content = chunk.choices[0].delta.content

                    if content:
                        full += content
                        yield content

                save_message(conversation_id, "assistant", full)

            return StreamingResponse(
                generate(),
                media_type="text/plain",
            )

        except Exception as e:
            print(f"[error]:{e}")
            raise HTTPException(status_code=500, detail=str(e))
