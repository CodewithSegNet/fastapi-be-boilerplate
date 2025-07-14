from sqlalchemy import Column, Text
from api.v1.models.base_model import BaseTableModel


class PrivacyPolicy(BaseTableModel):
    __tablename__ = "privacy_policies"
    
    content = Column(Text, nullable=False)
    