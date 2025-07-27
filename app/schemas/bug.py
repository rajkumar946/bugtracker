from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class BugStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"

class BugPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class AttachmentOut(BaseModel):
    id: int
    file_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class CommentOut(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: datetime
    attachments: List[AttachmentOut] = []

    class Config:
        from_attributes = True

class BugSeverity(str, Enum):
    trivial = "trivial"
    minor = "minor"
    major = "major"
    blocker = "blocker"

class BugBase(BaseModel):
    title: str
    description: Optional[str]
    os: Optional[str]
    browser: Optional[str]
    system_details: Optional[str]
    device_info: Optional[str]
    module: Optional[str]
    expected_behavior: Optional[str]
    current_behavior: Optional[str]
    steps_to_reproduce: Optional[str]
    resolution: Optional[str] = None
    replicated_on_mobile: bool = False
    replicated_on_tablet: bool = False
    replicated_on_desktop: bool = False
    is_security_related: bool = False
    is_regression: bool = False
    priority: BugPriority = BugPriority.medium
    severity: BugSeverity = BugSeverity.minor

class BugCreate(BugBase):
    project_id: int
    assigned_to_id: Optional[int] = None

class BugOut(BugBase):
    id: int
    project_id: int
    reported_by_id: int
    assigned_to_id: Optional[int]
    status: BugStatus
    priority: BugPriority
    severity: BugSeverity
    created_at: datetime
    updated_at: Optional[datetime]
    closed_at: Optional[datetime]
    attachments: List[AttachmentOut] = []
    comments: List[CommentOut] = []

    class Config:
        from_attributes = True