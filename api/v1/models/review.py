from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Review(BaseTableModel):
    __tablename__ = 'reviews'

    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"))
    rating = Column(Float, default=1, nullable=False, comment='1-5')
    remark = Column(String, nullable=True)

    user = relationship('User', back_populates='reviews')
    