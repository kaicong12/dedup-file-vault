from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import File
from dedup.models import DedupJob

@receiver(post_save, sender=File)
@receiver(post_delete, sender=File)
def invalidate_dedup_jobs(sender, instance, **kwargs):
    """
    Invalidate deduplication jobs when files are added or deleted.
    """
    DedupJob.objects.filter(is_valid=True).update(is_valid=False)