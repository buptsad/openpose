from django.urls import path
from .views import FeedbackListView, FeedbackDetailView

urlpatterns = [
    path('', FeedbackListView.as_view(), name='feedback_list'),
    path('<uuid:feedback_id>/', FeedbackDetailView.as_view(), name='feedback_detail'),
]