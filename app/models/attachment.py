from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255), nullable=False)
    bug_id = Column(Integer, ForeignKey("bugs.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    bug = relationship("Bug", back_populates="attachments")
    comment = relationship("Comment", back_populates="attachments")
