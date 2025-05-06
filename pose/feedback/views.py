from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FeedbackSerializer
from .models import Feedback
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .schemas import feedback_response_schema, feedback_list_response_schema

class FeedbackListView(APIView):
    """API view for handling feedback submission and listing"""
    
    @swagger_auto_schema(
        operation_summary="Submit feedback",
        operation_description="Submit user feedback with rating and conversation messages",
        request_body=FeedbackSerializer,
        responses={
            201: openapi.Response(
                description="Feedback created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description="UUID of the created feedback")
                    }
                )
            ),
            400: "Bad request"
        },
        tags=['Feedback']
    )
    def post(self, request):
        """Handle feedback submission"""
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback = serializer.save()
            return Response({"id": str(feedback.id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="List all feedback",
        operation_description="Get a list of all feedback entries",
        responses={
            200: openapi.Response(
                description="Successful retrieval",
                schema=feedback_list_response_schema
            )
        },
        tags=['Feedback']
    )
    def get(self, request):
        """Get a list of all feedback entries"""
        feedbacks = Feedback.objects.all().order_by('-created_at')
        data = []
        for feedback in feedbacks:
            data.append({
                "id": str(feedback.id),
                "rating": {
                    "accuracy": feedback.accuracy_rating,
                    "fluency": feedback.fluency_rating
                },
                "date": feedback.date,
            })
        return Response(data)


class FeedbackDetailView(APIView):
    """API view for handling individual feedback retrieval"""
    
    @swagger_auto_schema(
        operation_summary="Retrieve feedback detail",
        operation_description="Get detailed feedback data by ID",
        responses={
            200: openapi.Response(
                description="Successful retrieval",
                schema=feedback_response_schema
            ),
            404: "Feedback not found"
        },
        tags=['Feedback']
    )
    def get(self, request, feedback_id):
        """Get feedback data by ID"""
        try:
            feedback = Feedback.objects.get(id=feedback_id)
            data = {
                "id": str(feedback.id),
                "rating": {
                    "accuracy": feedback.accuracy_rating,
                    "fluency": feedback.fluency_rating
                },
                "date": feedback.date,
                "messages": feedback.get_messages()
            }
            return Response(data)
        except Feedback.DoesNotExist:
            return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)
