from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Notification(BaseTableModel):
    __tablename__ = 'notifications'

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum('read', 'unread', name='notification_status'), server_default='unread')
    notification_type = Column(Enum('warning', 'info', 'success', name='notification_type'), server_default='success')
    receiver_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    user = relationship('User', back_populates='notifications')



