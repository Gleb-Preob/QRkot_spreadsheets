from sqlalchemy import Column, String, Text

from .base import BaseTableModel


class CharityProject(BaseTableModel):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
