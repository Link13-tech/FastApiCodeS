import uuid
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from sqlalchemy.dialects.postgresql import UUID


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    title = Column(String, index=True)
    code = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)

    author = relationship("User")
