""" The Profile model
"""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel


class Profile(BaseTableModel):
    __tablename__ = "profiles"

    user_id = Column(
        String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    username = Column(String, nullable=True)
    pronouns = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    social = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "pronouns": self.pronouns,
            "job_title": self.job_title,
            "social": self.social,
            "bio": self.bio,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user": self.user.to_dict() if self.user else None,
        }
