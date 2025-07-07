from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import File
from .serializers import FileSerializer

# Create your views here.

class FilePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    pagination_class = FilePagination

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
                'images': [
                    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
                    'image/bmp', 'image/svg+xml', 'image/webp', 'image/tiff'
                ],
                'documents': [
                    'application/pdf', 'application/msword', 
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain', 'application/rtf', 'application/vnd.oasis.opendocument.text',
                    'application/vnd.ms-excel', 
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.ms-powerpoint', 
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'text/csv', 'application/vnd.oasis.opendocument.spreadsheet',
                    'application/vnd.oasis.opendocument.presentation'
                ],
                'videos': [
                    'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
                    'video/x-flv', 'video/webm', 'video/x-matroska', 'video/mpeg',
                    'video/3gpp', 'video/x-ms-wmv'
                ],
                'audio': [
                    'audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac',
                    'audio/ogg', 'audio/x-ms-wma', 'audio/mp3', 'audio/x-wav',
                    'audio/vorbis', 'audio/mp4'
                ],
                'archives': [
                    'application/zip', 'application/x-rar-compressed', 
                    'application/x-7z-compressed', 'application/x-tar',
                    'application/gzip', 'application/x-bzip2', 'application/x-compress',
                    'application/x-compressed', 'application/x-zip-compressed'
                ]
            }
            
            if file_type in file_type_mapping:
                file_extensions = file_type_mapping[file_type]
                queryset = queryset.filter(file_type__in=file_extensions)
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
