from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Upload
from .tasks import process_image
import uuid
from .utils.storage import upload_to_s3  # you create this helper

class UploadView(APIView):
    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        # Upload original to S3
        original_url = upload_to_s3(file, folder="originals")

        # Create DB entry
        upload_obj = Upload.objects.create(
            original_file=original_url,
            status="pending"
        )

        # Trigger background task
        process_image.delay(str(upload_obj.id))

        return Response({
            "id": upload_obj.id,
            "status": upload_obj.status
        }, status=201)
        
        
class UploadStatusView(APIView):
    def get(self, request, id):
        try:
            upload = Upload.objects.get(id=id)
            return Response({"id": id, "status": upload.status})
        except Upload.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


class UploadResultView(APIView):
    def get(self, request, id):
        try:
            upload = Upload.objects.get(id=id)
            return Response({
                "id": id,
                "original": upload.original_file,
                "resized": upload.resized_file,
                "compressed": upload.compressed_file,
                "thumbnail": upload.thumbnail_file,
            })
        except Upload.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

