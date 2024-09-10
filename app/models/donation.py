from sqlalchemy import Column, ForeignKey, Integer, Text

from .base import BaseTableModel


class Donation(BaseTableModel):
    user_id = Column(
        Integer,
        ForeignKey('user.id', name='fk_reservation_user_id_user')
    )
    comment = Column(Text)
