from celery import shared_task
from django.conf import settings
from PIL import Image
from io import BytesIO
from .models import Upload
from .utils.storage import upload_to_s3, s3_client

@shared_task
def process_image(upload_id):
    upload = Upload.objects.get(id=upload_id)
    upload.status = "processing"
    upload.save()

    

    try:
        # Extract the S3 key from the stored URL
        # e.g., if original_file = http://minio:9000/uploads/originals/xyz.jpg
        # we want key = 'originals/xyz.jpg'
        original_key = upload.original_file.split(f"{settings.S3_BUCKET_NAME}/")[-1]

        # Download image from S3
        response = s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=original_key)
        image_bytes = response['Body'].read()
        image = Image.open(BytesIO(image_bytes))
        
        # RESIZE
        img_resized = image.copy()
        if img_resized.mode in ("RGBA", "P"):
            img_resized = img_resized.convert("RGB")
        img_resized.thumbnail((1024, 1024))
        resized_bytes = BytesIO()
        img_resized.save(resized_bytes, format="JPEG")
        resized_bytes.seek(0)  # <-- Reset pointer
        resized_url = upload_to_s3(resized_bytes, folder="resized")

        # COMPRESS
        compressed_bytes = BytesIO()
        img_to_compress = image.copy()
        if img_to_compress.mode in ("RGBA", "P"):
            img_to_compress = img_to_compress.convert("RGB")
        img_to_compress.save(compressed_bytes, format="JPEG", quality=60)
        compressed_bytes.seek(0)  # <-- Reset pointer
        compressed_url = upload_to_s3(compressed_bytes, folder="compressed")

        # THUMBNAIL
        img_thumb = image.copy()
        if img_thumb.mode in ("RGBA", "P"):
            img_thumb = img_thumb.convert("RGB")
        img_thumb.thumbnail((300, 300))
        thumb_bytes = BytesIO()
        img_thumb.save(thumb_bytes, format="JPEG")
        thumb_bytes.seek(0)  # <-- Reset pointer
        thumb_url = upload_to_s3(thumb_bytes, folder="thumbnails")

        # Save results
        upload.resized_file = resized_url
        upload.compressed_file = compressed_url
        upload.thumbnail_file = thumb_url
        upload.status = "completed"
        upload.save()

    except Exception as e:
        upload.status = "failed"
        upload.save()
        # Optional: log the error for debugging
        print(f"Image processing failed for upload {upload_id}: {e}")
