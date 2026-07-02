"""
FastAPI service exposing /health and /chat.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from agent import generate_response

app = FastAPI(title="SHL Assessment Recommender")


class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1)


class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        msgs = [m.model_dump() for m in req.messages]
        result = generate_response(msgs)
        return ChatResponse(**result)
    except Exception as e:
        # Never let the endpoint crash — return a schema-valid fallback
        return ChatResponse(
            reply="Sorry, I encountered an error. Please try again.",
            recommendations=[],
            end_of_conversation=False
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)