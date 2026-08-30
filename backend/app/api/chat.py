import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageOut
from app.ai.chat_assistant import handle_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == payload.session_id, ChatSession.user_id == current_user.id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = ChatSession(id=uuid.uuid4(), user_id=current_user.id)
        db.add(session)
        db.flush()

    db.add(
        ChatMessage(id=uuid.uuid4(), chat_session_id=session.id, role="user", content=payload.message)
    )

    reply = handle_message(current_user.id, payload.message, db)

    db.add(
        ChatMessage(id=uuid.uuid4(), chat_session_id=session.id, role="assistant", content=reply)
    )
    db.commit()

    return ChatResponse(session_id=session.id, reply=reply)


@router.get("/history", response_model=list[ChatMessageOut])
def history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .first()
    )
    if not session:
        return []
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
