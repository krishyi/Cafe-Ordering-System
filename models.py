from typing import List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    message: str

class OrderLine(BaseModel):
    id: int
    item: str
    quantity: int
    modifiers: List[str] = []

class ChatResponse(BaseModel):
    reply: str
    message_type: Optional[str] = None
    order: List[OrderLine]
    discounts: List[str]
    warnings: List[str]
    total: float