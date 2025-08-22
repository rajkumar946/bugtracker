from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class BugStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"

class BugPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class BugSeverity(str, enum.Enum):
    trivial = "trivial"
    minor = "minor"
    major = "major"
    blocker = "blocker"

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(Enum(BugStatus), default=BugStatus.open, nullable=False)
    priority = Column(Enum(BugPriority), default=BugPriority.medium, nullable=False)
    severity = Column(Enum(BugSeverity), default=BugSeverity.minor, nullable=False)

    os = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    system_details = Column(Text, nullable=True)
    device_info = Column(String(255), nullable=True)

    module = Column(String(100), nullable=True)
    steps_to_reproduce = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    current_behavior = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)

    is_security_related = Column(Boolean, default=False)
    is_regression = Column(Boolean, default=False)

    replicated_on_mobile = Column(Boolean, default=False)
    replicated_on_tablet = Column(Boolean, default=False)
    replicated_on_desktop = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    comments = relationship("Comment", back_populates="bug", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="bug", cascade="all, delete-orphan")
    reported_by = relationship("User", foreign_keys=[reported_by_id], back_populates="reported_bugs")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_bugs")
    project = relationship("Project", back_populates="bugs")
