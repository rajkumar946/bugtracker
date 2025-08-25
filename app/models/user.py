from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, func, VARCHAR
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base
from app.core.roles import UserRoles

class RoleEnum(str, enum.Enum):
    admin = UserRoles.ADMIN
    developer = UserRoles.DEVELOPER
    qa = UserRoles.QA
    project_manager = UserRoles.MANAGER
    user = UserRoles.USER

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)  # Added full_name field
    hashed_password = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(1024), nullable=True)
    reset_token = Column(String(1024), nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reported_bugs = relationship("Bug", foreign_keys="Bug.reported_by_id", back_populates="reported_by")
    assigned_bugs = relationship("Bug", foreign_keys="Bug.assigned_to_id", back_populates="assigned_to")
    projects = relationship("Project", secondary="project_user", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}', role='{self.role}')>"

    @property
    def display_name(self):
        """Return full_name if available, otherwise email"""
        return self.full_name if self.full_name else self.email

    @property
    def is_superuser(self):
        """Check if user has admin role (for backward compatibility with CLI)"""
        return self.role == RoleEnum.admin