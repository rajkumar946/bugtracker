import os
import shutil
from app.core.config import UPLOAD_DIR
from app.models.attachment import Attachment
from sqlalchemy.ext.asyncio import AsyncSession

async def save_file_local(file, context_type: str, context_id: int):
    folder = os.path.join(UPLOAD_DIR, context_type, str(context_id))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path
