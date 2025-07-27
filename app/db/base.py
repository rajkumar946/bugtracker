from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models so Alembic sees them
from app.models import user, project, attachment, bug, comment, project_user