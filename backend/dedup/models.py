from django.db import models
import uuid


# Create your models here.

class DedupJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)  # Mark as invalid when files change
    duplicates = models.JSONField(default=list, blank=True)  # Store duplicate file data as JSON

    def __str__(self):
        return f"DedupJob {self.id}"