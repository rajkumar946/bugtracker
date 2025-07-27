from google.cloud import storage
import uuid

client = storage.Client()
bucket = client.bucket('your-gcs-bucket')

async def save_file_gcs(file, context_type: str, context_id: int):
    blob_path = f"{context_type}/{context_id}/{uuid.uuid4()}_{file.filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_file(file.file, content_type=file.content_type)
    return blob.public_url
