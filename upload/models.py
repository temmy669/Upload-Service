from django.db import models
import uuid

# Create your models here
class Upload(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_file = models.URLField()
    resized_file = models.URLField(null=True, blank=True)
    compressed_file = models.URLField(null=True, blank=True)
    thumbnail_file = models.URLField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
