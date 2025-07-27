from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: int
    created_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(ProjectInDBBase):
    pass


class ProjectUserAction(BaseModel):
    user_id: list[int]