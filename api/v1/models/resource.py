#!/usr/bin/env python3
"""The Blog Post Model."""

from sqlalchemy import Column, String, Boolean, ARRAY
from api.v1.models.base_model import BaseTableModel


class Resource(BaseTableModel):
    __tablename__ = "resources"

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String)
    cover_image_url = Column(String)
    tags = Column(ARRAY(String))
    category = Column(String, nullable=False, default="General")
    is_deleted = Column(Boolean, server_default="false")
    is_published = Column(Boolean, server_default="false")
