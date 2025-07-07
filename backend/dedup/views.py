from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import DedupJob
from .serializers import DedupJobSerializer
from .tasks import deduplicate_files

class DedupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing deduplication jobs.
    """
    queryset = DedupJob.objects.all()
    serializer_class = DedupJobSerializer

    @action(detail=False, methods=['post'])
    def trigger(self, request):
        """
        Trigger a new deduplication job for the current user.
        """

        # Trigger the Celery task
        task = deduplicate_files.delay()

        return Response({
            'message': 'Deduplication task has been started.',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Get the latest valid deduplication job for the current user.
        """
        dedup_job = DedupJob.objects.filter(is_valid=True).first()

        if not dedup_job:
            return Response({'message': 'No valid deduplication job found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(dedup_job)
        return Response(serializer.data)