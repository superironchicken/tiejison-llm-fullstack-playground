from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from llm import get_client
from schemas import ChatRequest

router = APIRouter()
@router.post("/chat")
async def start_chat(request: ChatRequest):
    client = get_client()
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
