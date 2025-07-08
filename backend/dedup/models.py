from django.db import models
import uuid


# Create your models here.

class DedupJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)  # Mark as invalid when files change
    duplicates = models.JSONField(default=list, blank=True)  # Store duplicate file data as JSON
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"DedupJob {self.id}"