from pydantic import BaseModel
from typing import List

class Entity(BaseModel):
    text: str
    start: int
    end: int
    label: str

class ClassificationResponse(BaseModel):
    request:str
    intent: str
    entities: List[Entity]