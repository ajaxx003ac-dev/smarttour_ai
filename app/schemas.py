from pydantic import BaseModel, Field
from typing import List, Optional

class PlannerRequest(BaseModel):
    destination: str
    days: int = Field(ge=1, le=14)
    travelers: int = Field(ge=1, le=50)
    budget: float = Field(gt=0)
    interests: str = "history,food"
    pace: str = "relaxed"
    food_preferences: str = "local"
    transport: str = "public"
    accessibility: str = "none"
    travel_dates: Optional[str] = None

class EventRequest(BaseModel):
    event_type: str
    severity: str = "high"
    attraction_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    destination: str = "Jaipur"

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "tourist"
