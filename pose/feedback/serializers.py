from rest_framework import serializers
from .models import Feedback
from django.utils import timezone

class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="Unique identifier for the message")
    text = serializers.CharField(help_text="Message content text")
    isUser = serializers.BooleanField(help_text="True if the message is from the user, False if from system")

class RatingSerializer(serializers.Serializer):
    accuracy = serializers.IntegerField(
        min_value=1, 
        max_value=5, 
        help_text="Accuracy rating from 1 to 5"
    )
    fluency = serializers.IntegerField(
        min_value=1, 
        max_value=5, 
        help_text="Fluency rating from 1 to 5"
    )

class FeedbackSerializer(serializers.Serializer):
    rating = RatingSerializer(help_text="Rating information including accuracy and fluency scores")
    messages = MessageSerializer(
        many=True, 
        help_text="List of conversation messages"
    )
    date = serializers.DateField(required=False, help_text="Date when feedback was provided (automatically added if not specified)")
    
    def create(self, validated_data):
        rating_data = validated_data.get('rating', {})
        messages_data = validated_data.get('messages', [])
        # Auto-set date to today if not provided
        date = validated_data.get('date', timezone.now().date())
        
        # Create the feedback object
        feedback = Feedback.objects.create(
            accuracy_rating=rating_data.get('accuracy'),
            fluency_rating=rating_data.get('fluency'),
            date=date,
            messages_file=''  # Will be updated when messages are saved
        )
        
        # Save messages to a file
        feedback.save_messages(messages_data)
        
        return feedback