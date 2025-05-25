from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from pathlib import Path
import os
import shutil
from video_manager.models import VideoAsset

class VideoManagerTests(TestCase):
    
    def setUp(self):
        # Create temporary directories for testing
        self.temp_dir = Path(settings.BASE_DIR) / 'test_media'
        self.example_videos_dir = self.temp_dir / 'example_videos' / '01_tag1'
        self.explain_videos_dir = self.temp_dir / 'explain_videos'
        
        # Create directories
        self.example_videos_dir.mkdir(parents=True, exist_ok=True)
        self.explain_videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files (mock content)
        with open(self.example_videos_dir / '01_tag1.1.mp4', 'w') as f:
            f.write('mock mp4 content')
        with open(self.example_videos_dir / '01_tag1.1.webp', 'w') as f:
            f.write('mock webp content')
        
        with open(self.explain_videos_dir / '01.mp4', 'w') as f:
            f.write('mock explain video content')
    
    def tearDown(self):
        # Clean up test directories
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_video_import_with_explain_videos(self):
        # Create directories first
        call_command('create_directories')
        
        # Test importing videos and explain videos
        call_command('import_videos', 
                    path=str(self.temp_dir / 'example_videos'),
                    explain_path=str(self.temp_dir / 'explain_videos'),
                    clear=True)
        
        # Verify asset was created with correct data
        assets = VideoAsset.objects.all()
        self.assertEqual(assets.count(), 1)
        
        asset = assets.first()
        self.assertEqual(asset.numeric_id, "01_01")
        self.assertEqual(asset.tag1, "tag1")
        self.assertEqual(asset.tag2, "tag1.1")
        
        # Verify explain video path is set correctly
        self.assertIsNotNone(asset.explain_video_path)
        self.assertEqual(asset.explain_video_path, "standard/explain_video/01.mp4")
