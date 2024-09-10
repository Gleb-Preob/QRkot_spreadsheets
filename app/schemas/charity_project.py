from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, validator
from pydantic.types import PositiveInt

from app.core.config import settings


class ProjectBase(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, max_length=settings.max_name_length
    )
    description: Optional[str] = Field(None, min_length=1)


class ProjectCreate(ProjectBase):
    name: str = Field(
        ..., min_length=1, max_length=settings.max_name_length
    )
    description: str = Field(..., min_length=1)
    full_amount: PositiveInt


class ProjectUpdate(ProjectBase):
    full_amount: Optional[PositiveInt]

    @validator('name')
    def name_cannott_be_null(cls, value):
        if value is None:
            raise ValueError('Нельзя удалить имя')
        return value

    class Config:
        extra = Extra.forbid


class ProjectDB(ProjectCreate):
    id: int
    invested_amount: Optional[int]
    full_amount: PositiveInt
    fully_invested: Optional[bool]
    create_date: Optional[datetime]
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
