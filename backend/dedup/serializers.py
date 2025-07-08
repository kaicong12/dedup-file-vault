from rest_framework import serializers
from .models import DedupJob

class DedupJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DedupJob
        fields = ['id', 'created_at', 'is_valid', 'duplicates', 'status']
        read_only_fields = ['id', 'created_at', 'duplicates']