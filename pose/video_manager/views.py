from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.conf import settings
from django.db.models import Q
from rest_framework.views import APIView
from pathlib import Path
from .models import VideoAsset
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import re
import logging

logger = logging.getLogger(__name__)

def read_description_file(description_path):
    """Read and return the content of the description file, or empty string if not found."""
    if not description_path:
        return ""
    file_path = Path(settings.BASE_DIR) / description_path
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Could not read description file {file_path}: {e}")
    return ""

def format_video_data(video):
    """Format a video asset for API response"""
    description_content = read_description_file(video.descriptions_path)
    return {
        'numeric_id': video.numeric_id,
        'tag_string': video.tag_string,
        'tags': {
            'tag1': video.tag1,
            'tag2': video.tag2,
            'tag3': video.tag3,
            'tag4': video.tag4,
            'tag5': video.tag5,
        },
        'example_video_path': video.mp4_path,
        'example_cover_path': video.cover_path,
        'explain_video_path': video.explain_video_path,
        'explain_cover_path': video.explain_cover_path,
        'description': description_content,
    }

class VideoByTagsView(APIView):
    @swagger_auto_schema(
        operation_description="Get videos matching the tag string prefix or tag parameters",
        manual_parameters=[
            openapi.Parameter(
                name='tag_string',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Tag string prefix to match videos',
                required=True
            ),
            openapi.Parameter(
                name='tag1',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag1',
                required=False
            ),
            openapi.Parameter(
                name='tag2',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag2',
                required=False
            ),
            openapi.Parameter(
                name='tag3',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag3',
                required=False
            ),
            openapi.Parameter(
                name='tag4',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag4',
                required=False
            ),
            openapi.Parameter(
                name='tag5',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag5',
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of matching videos",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'videos': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'numeric_id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tag_string': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tags': openapi.Schema(type=openapi.TYPE_OBJECT),
                                    'example_video_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'example_cover_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'explain_video_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'explain_cover_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            404: "No matching videos found"
        }
    )
    def get(self, request, tag_string=None):
        """Return all videos matching the tag string prefix or tag parameters"""
        videos = []
        
        # Check if we have query parameters for specific tags
        tag_params = {}
        for i in range(1, 6):
            tag_key = f'tag{i}'
            if tag_key in request.GET:
                tag_params[tag_key] = request.GET[tag_key]
        
        if tag_params:
            # Filter by specific tag parameters
            logger.info(f"Filtering videos by tag parameters: {tag_params}")
            query = Q()
            for tag_key, tag_value in tag_params.items():
                query &= Q(**{tag_key: tag_value})
            
            video_assets = VideoAsset.objects.filter(query)
        elif tag_string:
            # Filter by tag_string prefix
            logger.info(f"Filtering videos by tag string prefix: {tag_string}")
            video_assets = VideoAsset.objects.filter(tag_string__startswith=f"{tag_string}")
        else:
            # Return error if no filter criteria provided
            return JsonResponse({"error": "No tag criteria provided"}, status=400)
        
        # Convert query results to response format
        for video in video_assets:
            videos.append(format_video_data(video))
        
        if not videos:
            logger.warning(f"No videos found matching the criteria")
            return JsonResponse({"videos": []}, status=404)
        
        logger.info(f"Found {len(videos)} matching videos")
        return JsonResponse({"videos": videos})


class CoverByTagsView(APIView):
    @swagger_auto_schema(
        operation_description="Get covers matching the tag string prefix or tag parameters",
        manual_parameters=[
            openapi.Parameter(
                name='tag_string',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Tag string prefix to match covers',
                required=True
            ),
            openapi.Parameter(
                name='tag1',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag1',
                required=False
            ),
            openapi.Parameter(
                name='tag2',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag2',
                required=False
            ),
            openapi.Parameter(
                name='tag3',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag3',
                required=False
            ),
            openapi.Parameter(
                name='tag4',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag4',
                required=False
            ),
            openapi.Parameter(
                name='tag5',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Value for tag5',
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of matching covers",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'covers': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'numeric_id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tag_string': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tags': openapi.Schema(type=openapi.TYPE_OBJECT),
                                    'example_video_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'example_cover_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'explain_video_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'explain_cover_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            ),
            404: "No matching covers found"
        }
    )
    def get(self, request, tag_string=None):
        """Return all covers matching the tag string prefix or tag parameters"""
        covers = []
        
        # Check if we have query parameters for specific tags
        tag_params = {}
        for i in range(1, 6):
            tag_key = f'tag{i}'
            if tag_key in request.GET:
                tag_params[tag_key] = request.GET[tag_key]
        
        if tag_params:
            # Filter by specific tag parameters
            logger.info(f"Filtering covers by tag parameters: {tag_params}")
            query = Q()
            for tag_key, tag_value in tag_params.items():
                query &= Q(**{tag_key: tag_value})
            
            video_assets = VideoAsset.objects.filter(query)
        elif tag_string:
            # Filter by tag_string prefix
            logger.info(f"Filtering covers by tag string prefix: {tag_string}")
            video_assets = VideoAsset.objects.filter(tag_string__startswith=f"{tag_string}")
        else:
            # Return error if no filter criteria provided
            return JsonResponse({"error": "No tag criteria provided"}, status=400)
        
        # Convert query results to response format
        for video in video_assets:
            covers.append(format_video_data(video))
        
        if not covers:
            logger.warning(f"No covers found matching the criteria")
            return JsonResponse({"covers": []}, status=404)
        
        logger.info(f"Found {len(covers)} matching covers")
        return JsonResponse({"covers": covers})

class VideoByIdView(APIView):
    @swagger_auto_schema(
        operation_description="Get a video by its numeric ID (format: XX_YY)",
        manual_parameters=[
            openapi.Parameter(
                name='video_id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Numeric ID in format XX_YY',
                required=True
            )
        ],
        responses={
            200: "Video file (MP4)",
            404: "Video not found or invalid ID format"
        }
    )
    def get(self, request, video_id):
        """Return a video by its numeric ID (format: XX_YY)"""
        parts = video_id.split('_')
        if len(parts) != 2:
            logger.warning(f"Invalid video ID format: {video_id}")
            return HttpResponseNotFound("Invalid video ID format")
        
        try:
            logger.info(f"Received request for video with ID: {video_id}")
            video_asset = VideoAsset.objects.filter(
                numeric_id=video_id
            ).first()
            
            if not video_asset:
                logger.warning(f"Video with ID {video_id} not found")
                return HttpResponseNotFound("Video not found with the specified ID")
                
            file_path = Path(settings.BASE_DIR) / video_asset.original_mp4_path
            
            if file_path.exists():
                logger.info(f"Returning video file: {file_path}")
                return FileResponse(file_path.open('rb'), content_type='video/mp4')
            else:
                logger.warning(f"Video file not found: {file_path}")
                return HttpResponseNotFound("Video file not found")
        except Exception as e:
            logger.error(f"Error retrieving video: {str(e)}", exc_info=True)
            return HttpResponseNotFound(f"Error retrieving video: {str(e)}")


class CoverByIdView(APIView):
    @swagger_auto_schema(
        operation_description="Get a cover image by its numeric ID (format: XX_YY)",
        manual_parameters=[
            openapi.Parameter(
                name='cover_id',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description='Numeric ID in format XX_YY',
                required=True
            )
        ],
        responses={
            200: "Cover image (WebP)",
            404: "Cover image not found or invalid ID format"
        }
    )
    def get(self, request, cover_id):
        """Return a cover by its numeric ID (format: XX_YY)"""
        parts = cover_id.split('_')
        if len(parts) != 2:
            logger.warning(f"Invalid cover ID format: {cover_id}")
            return HttpResponseNotFound("Invalid cover ID format")
        
        try:
            logger.info(f"Received request for cover with ID: {cover_id}")
            video_asset = VideoAsset.objects.filter(
                numeric_id=cover_id
            ).first()
            
            if not video_asset:
                logger.warning(f"Cover with ID {cover_id} not found")
                return HttpResponseNotFound("Cover not found with the specified ID")
                
            file_path = Path(settings.BASE_DIR) / video_asset.original_cover_path
            
            if file_path.exists():
                logger.info(f"Returning cover file: {file_path}")
                return FileResponse(file_path.open('rb'), content_type='image/webp')
            else:
                logger.warning(f"Cover file not found: {file_path}")
                return HttpResponseNotFound("Cover file not found")
        except Exception as e:
            logger.error(f"Error retrieving cover: {str(e)}", exc_info=True)
            return HttpResponseNotFound(f"Error retrieving cover: {str(e)}")


class AllVideosView(APIView):
    @swagger_auto_schema(
        operation_description="Get all video assets with their metadata, including example and explain videos",
        responses={
            200: openapi.Response(
                description="List of all video assets",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'videos': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'numeric_id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tag_string': openapi.Schema(type=openapi.TYPE_STRING),
                                    'tags': openapi.Schema(type=openapi.TYPE_OBJECT),
                                    'example_video_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'example_cover_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'explain_video_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'explain_cover_path': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        """Return all video assets with their tags, IDs, file paths, and description content"""
        videos = VideoAsset.objects.all()
        video_list = []
        for video in videos:
            description_content = read_description_file(video.descriptions_path)
            video_data = {
                'numeric_id': video.numeric_id,
                'tag_string': video.tag_string,
                'tags': {
                    'tag1': video.tag1,
                    'tag2': video.tag2,
                    'tag3': video.tag3,
                    'tag4': video.tag4,
                    'tag5': video.tag5,
                },
                'example_video_path': video.mp4_path,
                'example_cover_path': video.cover_path,
                'explain_video_path': video.explain_video_path,
                'explain_cover_path': video.explain_cover_path,  # <-- Use the new field
                'description': description_content,
            }
            video_list.append(video_data)
        logger.info(f"Returning {len(video_list)} video assets")
        return JsonResponse({'videos': video_list})

class ExplainVideoByIdView(APIView):
    def get(self, request, video_id):
        video_asset = VideoAsset.objects.filter(numeric_id=video_id).first()
        if not video_asset or not video_asset.explain_video_path:
            return HttpResponseNotFound("Explain video not found")
        file_path = Path(settings.BASE_DIR) / video_asset.explain_video_path
        if file_path.exists():
            return FileResponse(file_path.open('rb'), content_type='video/mp4')
        else:
            return HttpResponseNotFound("Explain video file not found")

class ExplainCoverByIdView(APIView):
    def get(self, request, cover_id):
        video_asset = VideoAsset.objects.filter(numeric_id=cover_id).first()
        if not video_asset or not video_asset.explain_cover_path:
            return HttpResponseNotFound("Explain cover not found")
        cover_path = Path(settings.BASE_DIR) / video_asset.explain_cover_path
        if cover_path.exists():
            return FileResponse(cover_path.open('rb'), content_type='image/webp')
        else:
            return HttpResponseNotFound("Explain cover file not found")


# Update these function-based views for backward compatibility
def get_video_by_tags(request, tag_string=None):
    return VideoByTagsView().get(request, tag_string)

def get_cover_by_tags(request, tag_string=None):
    return CoverByTagsView().get(request, tag_string)

def get_video_by_id(request, video_id):
    return VideoByIdView().get(request, video_id)

def get_cover_by_id(request, cover_id):
    return CoverByIdView().get(request, cover_id)

def get_all_videos(request):
    return AllVideosView().get(request)