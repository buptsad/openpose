# Generated by Django 5.1.7 on 2025-05-06 05:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('accuracy_rating', models.IntegerField()),
                ('fluency_rating', models.IntegerField()),
                ('date', models.DateField()),
                ('messages_file', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
