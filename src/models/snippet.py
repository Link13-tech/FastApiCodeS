import uuid
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=str(uuid.uuid4()))
    title = Column(String, index=True)
    code = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=True)

    author = relationship("User")
