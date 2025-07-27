from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class RoleEnum(str, Enum):
    admin = "admin"
    developer = "developer"
    qa = "qa"
    project_manager = "project_manager"

class AdminCreateUser(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum

class AdminUpdateUser(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    role: Optional[RoleEnum]

class EmailSettings(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    from_email: EmailStr
