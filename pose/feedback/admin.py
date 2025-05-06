from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'accuracy_rating', 'fluency_rating', 'date', 'created_at')
    search_fields = ('id', 'date')
    readonly_fields = ('id', 'created_at', 'messages_file')
    list_filter = ('date', 'created_at')
