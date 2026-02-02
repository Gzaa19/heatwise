"""
WISE AI Chatbot Controller
Provides AI-powered chat interface using Google Gemini
"""

from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.gemini import get_gemini_service


# Request/Response Models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    context: Optional[Dict] = None


class ChatResponse(BaseModel):
    response: str
    success: bool


# Create router
router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message to WISE AI chatbot
    """
    try:
        gemini_service = get_gemini_service()
        
        if not gemini_service.is_available():
            return ChatResponse(
                response="I apologize, but the AI service is currently unavailable. Please check the API configuration.",
                success=False
            )
        
        # Convert history to expected format
        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        # Get response from Gemini
        response = await gemini_service.chat(
            message=request.message,
            context=request.context,
            history=history
        )
        
        return ChatResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"I encountered an error: {str(e)}. Please try again.",
            success=False
        )


@router.get("/health")
async def chat_health():
    """Check chatbot service health"""
    gemini_service = get_gemini_service()
    return {
        "status": "ok" if gemini_service.is_available() else "unavailable",
        "service": "WISE AI Chatbot",
        "model": "gemini-3.0-pro"
    }
