from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    function = "function"

class Message(BaseModel):
    role: Role
    content: str

class AIRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    timeout: int = 30 # seconds

class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class AIResponse(BaseModel):
    content: str
    usage: Usage
    model: str
    provider: str
    latency_ms: float = 0.0
