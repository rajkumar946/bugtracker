from app.core.config import STORAGE_BACKEND
from .local_storage import save_file_local
from .s3_storage import save_file_s3
from .gcs_storage import save_file_gcs

async def save_attachment(file, context_type: str, context_id: int):
    """
    context_type = 'bugs' or 'comments'
    """
    if STORAGE_BACKEND == "local":
        return await save_file_local(file, context_type, context_id)
    elif STORAGE_BACKEND == "s3":
        return await save_file_s3(file, context_type, context_id)
    elif STORAGE_BACKEND == "gcs":
        return await save_file_gcs(file, context_type, context_id)
    else:
        raise ValueError(f"Unsupported storage backend: {STORAGE_BACKEND}")
