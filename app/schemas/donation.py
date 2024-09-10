from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.types import PositiveInt


class ProjectBase(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt


class DonationCreate(ProjectBase):
    pass


class DonationDB(ProjectBase):
    id: int
    create_date: Optional[datetime]

    class Config:
        orm_mode = True


class DonationDBSuper(DonationDB):
    invested_amount: Optional[int]
    fully_invested: Optional[bool]
    close_date: Optional[datetime]
    user_id: Optional[int]
