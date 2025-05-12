from drf_yasg import openapi

# Updated request schema to make date optional
feedback_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['rating', 'messages'],
    properties={
        'rating': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['accuracy', 'fluency'],
            properties={
                'accuracy': openapi.Schema(type=openapi.TYPE_INTEGER, description='Accuracy rating (1-5)'),
                'fluency': openapi.Schema(type=openapi.TYPE_INTEGER, description='Fluency rating (1-5)')
            }
        ),
        'messages': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'text', 'isUser'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Message ID'),
                    'text': openapi.Schema(type=openapi.TYPE_STRING, description='Message text'),
                    'isUser': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if user message')
                }
            )
        ),
        'date': openapi.Schema(
            type=openapi.TYPE_STRING, 
            format='date', 
            description='Date when feedback was provided (optional, defaults to current date)'
        ),
    }
)

# Existing response schemas
feedback_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Feedback UUID'),
        'rating': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'accuracy': openapi.Schema(type=openapi.TYPE_INTEGER, description='Accuracy rating (1-5)'),
                'fluency': openapi.Schema(type=openapi.TYPE_INTEGER, description='Fluency rating (1-5)')
            }
        ),
        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Feedback date'),
        'messages': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Message ID'),
                    'text': openapi.Schema(type=openapi.TYPE_STRING, description='Message text'),
                    'isUser': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='True if user message')
                }
            )
        )
    }
)

feedback_list_response_schema = openapi.Schema(
    type=openapi.TYPE_ARRAY,
    items=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, description='Feedback UUID'),
            'rating': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'accuracy': openapi.Schema(type=openapi.TYPE_INTEGER, description='Accuracy rating (1-5)'),
                    'fluency': openapi.Schema(type=openapi.TYPE_INTEGER, description='Fluency rating (1-5)')
                }
            ),
            'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Feedback date')
        }
    )
)