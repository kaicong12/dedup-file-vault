from rest_framework import serializers
from .models import DedupJob

class DedupJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = DedupJob
        fields = ['id', 'user', 'created_at', 'is_valid', 'duplicates']
        read_only_fields = ['id', 'created_at', 'duplicates']