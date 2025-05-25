from django.urls import path
from . import views

urlpatterns = [
    # Example video and cover by tag string or ID
    path('video/tags/<str:tag_string>/', views.VideoByTagsView.as_view(), name='get_video_by_tags'),
    path('cover/tags/<str:tag_string>/', views.CoverByTagsView.as_view(), name='get_cover_by_tags'),
    path('video/id/<str:video_id>/', views.VideoByIdView.as_view(), name='get_video_by_id'),
    path('cover/id/<str:cover_id>/', views.CoverByIdView.as_view(), name='get_cover_by_id'),

    # Explain video and cover by tag string or ID
    path('explain_video/id/<str:video_id>/', views.ExplainVideoByIdView.as_view(), name='get_explain_video_by_id'),
    path('explain_cover/id/<str:cover_id>/', views.ExplainCoverByIdView.as_view(), name='get_explain_cover_by_id'),

    # Get all video urls
    path('all/', views.AllVideosView.as_view(), name='get_all_videos'),
]