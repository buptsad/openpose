import os
import uuid
import json
from django.db import models
from django.conf import settings

class Feedback(models.Model):
    """Model to store feedback data with rating and reference to messages file"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    accuracy_rating = models.IntegerField()
    fluency_rating = models.IntegerField()
    date = models.DateField()
    messages_file = models.CharField(max_length=255)  # Path to the messages file
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save_messages(self, messages):
        """Save messages to a JSON file and store the file path"""
        # Create directory if it doesn't exist
        messages_dir = os.path.join(settings.MEDIA_ROOT, 'feedback_messages')
        os.makedirs(messages_dir, exist_ok=True)
        
        # Generate a filename based on the feedback ID
        filename = f"{self.id}.json"
        filepath = os.path.join(messages_dir, filename)
        
        # Save messages to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False)
        
        # Store the relative path in the database
        self.messages_file = os.path.join('feedback_messages', filename)
        self.save()
    
    def get_messages(self):
        """Retrieve messages from the file"""
        filepath = os.path.join(settings.MEDIA_ROOT, self.messages_file)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
