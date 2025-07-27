import boto3
from app.core.config import AWS_BUCKET_NAME
import uuid

s3 = boto3.client('s3')

async def save_file_s3(file, context_type: str, context_id: int):
    key = f"{context_type}/{context_id}/{uuid.uuid4()}_{file.filename}"
    s3.upload_fileobj(file.file, AWS_BUCKET_NAME, key)
    url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"
    return url
