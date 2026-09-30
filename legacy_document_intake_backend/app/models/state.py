from typing import Optional, List, Literal
from pydantic import BaseModel, Field


FieldStatus = Literal["unknown", "confirmed", "unconfirmed"]


class Executor(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None


class DocumentState(BaseModel):
    full_name: Optional[str] = None
    home_address: Optional[str] = None

    covers_worldwide_assets: Optional[bool] = None

    has_children: Optional[bool] = None
    children: List[str] = Field(default_factory=list)

    executor: Executor = Field(default_factory=Executor)

    specific_gifts: List[str] = Field(default_factory=list)

    additional_wishes: List[str] = Field(default_factory=list)