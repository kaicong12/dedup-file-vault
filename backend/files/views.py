from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q
from .models import File
from .serializers import FileSerializer

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'file': file_obj,
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size
        }
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def list(self, request, *args, **kwargs):
        # Get query parameters
        search = request.query_params.get('search', '')
        sort_by = request.query_params.get('sortBy', 'uploaded_at')
        file_type = request.query_params.get('fileType', '')
        
        # Start with base queryset
        queryset = self.get_queryset()
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(original_filename__icontains=search) |
                Q(file_type__icontains=search)
            )
        
        # Apply file type filter
        if file_type and file_type != 'all':
            # Map frontend filter types to file extensions
            file_type_mapping = {
                'images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'],
                'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx'],
                'videos': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'],
                'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma'],
                'archives': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']
            }
            
            if file_type in file_type_mapping:
                print(file_type, "thijs ios file tyrpe")
                # Filter by file extensions
                file_extensions = file_type_mapping[file_type]
                print(file_extensions, "look for these extensions")
                queryset = queryset.filter(file_type__icontains=file_extensions)
            elif file_type == 'other':
                # Filter out known file types
                all_known_types = []
                for types in file_type_mapping.values():
                    all_known_types.extend(types)
                queryset = queryset.exclude(file_type__in=all_known_types)
        
        # Apply sorting
        sort_mapping = {
            'name': 'original_filename',
            'size': '-size',  # Descending by default
            'date': '-uploaded_at',  # Newest first
            'type': 'file_type'
        }
        
        if sort_by in sort_mapping:
            queryset = queryset.order_by(sort_mapping[sort_by])
        else:
            queryset = queryset.order_by('-uploaded_at')  # Default sort
        
        # Paginate if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Serialize and return
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
