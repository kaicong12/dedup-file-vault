from django.db import models
import uuid
import os
import hashlib

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

def calculate_file_hash(file_obj):
    """Calculate SHA-256 hash of file content"""
    hash_sha256 = hashlib.sha256()
    # Reset file pointer to beginning
    file_obj.seek(0)
    # Read file in chunks to handle large files
    for chunk in iter(lambda: file_obj.read(4096), b""):
        hash_sha256.update(chunk)
    # Reset file pointer again
    file_obj.seek(0)
    return hash_sha256.hexdigest()

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)  # SHA-256 hash
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['size', 'file_hash']),
        ]
    
    def __str__(self):
        return self.original_filename
    
    def save(self, *args, **kwargs):
        # Calculate hash if not set and file exists
        if not self.file_hash and self.file:
            self.file_hash = calculate_file_hash(self.file)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to remove the actual file from storage"""
        # Delete the file from storage if it exists
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        
        # Call the parent delete method to remove from database
        super().delete(*args, **kwargs)

