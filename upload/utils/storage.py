import boto3
from django.conf import settings
import uuid

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,  # e.g., http://localhost:9000 for MinIO
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)

BUCKET_NAME = settings.S3_BUCKET_NAME

def upload_to_s3(file_obj, folder="uploads"):
    """
    Upload file-like object to S3/MinIO and return public URL.
    file_obj can be:
      - Django InMemoryUploadedFile
      - BytesIO object
    """
    if hasattr(file_obj, "read"):
        data = file_obj.read()
    else:
        data = file_obj

    key = f"{folder}/{uuid.uuid4().hex}.jpg"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=data,
        ACL="public-read",
        ContentType="image/jpeg",
    )

    return f"{settings.S3_BASE_URL}/{key}"

