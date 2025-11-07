from pydantic import BaseModel
from typing import Any


class SaveTripIn(BaseModel):
    city: str
    recommendation: str


class TripOut(BaseModel):
    id: int
    city: str
    recommendation: str
    created_at: Any


class Config:
    from_attributes = True