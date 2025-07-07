from celery import shared_task
from .models import DedupJob
from files.models import File
from django.db.models import Count

@shared_task
def deduplicate_files():
    """
    Task to find duplicate files for a specific user.
    """
    duplicates = []

    # Find duplicate files by hash and size
    duplicate_groups = (
        File.objects.exclude(file_hash__isnull=True)
        .values('file_hash', 'size')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )

    for group in duplicate_groups:
        file_hash = group['file_hash']
        size = group['size']

        # Get all files in this duplicate group
        group_files = File.objects.filter(file_hash=file_hash, size=size).order_by('uploaded_at')

        # Keep the first file as the original
        original = group_files.first()
        duplicate_list = list(group_files.exclude(id=original.id))

        duplicates.append({
            'original_file': {
                'id': str(original.id),
                'url': original.file.url,
                'name': original.original_filename,
                'size': original.size,
                'uploaded_at': original.uploaded_at.isoformat(),
            },
            'duplicate_files': [
                {
                    'id': str(dup.id),
                    'url': dup.file.url,
                    'name': dup.original_filename,
                    'size': dup.size,
                    'uploaded_at': dup.uploaded_at.isoformat(),
                } for dup in duplicate_list
            ],
        })

    # Invalidate previous dedup jobs for this user
    DedupJob.objects.filter(is_valid=True).update(is_valid=False)

    # Create a new dedup job
    print(f"Creating Deduplication record: {duplicates}")
    dedup_job = DedupJob.objects.create(duplicates=duplicates)
    print(f"Dedup job created: {dedup_job}")
    return {
        'dedup_job_id': str(dedup_job.id),
        'duplicates_found': len(duplicates),
    }