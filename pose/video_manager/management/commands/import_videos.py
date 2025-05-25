import re
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from video_manager.models import VideoAsset
from django.conf import settings
from standard.gif_to_mp4_converter import extract_middle_frame_from_mp4

class Command(BaseCommand):
    help = 'Import videos and covers into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, default='standard/example_videos',
                           help='Path to the videos directory')
        parser.add_argument('--explain-path', type=str, default='standard/explain_videos',
                           help='Path to the explanation videos directory')
        parser.add_argument('--clear', action='store_true',
                           help='Clear existing database entries')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing database entries...')
            VideoAsset.objects.all().delete()

        videos_path = Path(settings.BASE_DIR) / options['path']
        explain_path = Path(settings.BASE_DIR) / options['explain_path']
        
        # First import regular videos
        self.import_videos(videos_path)
        
        # Then process explain videos
        self.process_explain_videos(explain_path)
        
        self.stdout.write(self.style.SUCCESS('Successfully imported videos'))

    def extract_file_id_and_tags(self, filename):
        """Extract file ID and tags from filename like 01_tag1.1_tag1.1.1_tag1.1.1.1"""
        # Remove extension
        base_name = filename.stem
        
        # Split by underscore
        parts = base_name.split('_')
        
        # First part is file ID, rest are file tags
        file_id = parts[0]
        file_tags = parts[1:] if len(parts) > 1 else []
        
        return file_id, file_tags

    def extract_folder_id_and_tag(self, folder_name):
        """Extract folder ID and tag from folder name like 01_tag1"""
        parts = folder_name.split('_', 1)
        
        if len(parts) > 1:
            folder_id = parts[0]
            folder_tag = parts[1]
        else:
            folder_id = folder_name
            folder_tag = None
            
        return folder_id, folder_tag
    
    def to_unix_path(self, path):
        """Convert a path to Unix format (forward slashes)"""
        return str(path).replace('\\', '/')

    def import_videos(self, root_path):
        """Scan directory structure and import videos with their covers"""
        count = 0
        
        for folder_path in root_path.glob('**'):
            if not folder_path.is_dir():
                continue
                
            # Extract folder info
            folder_name = folder_path.name
            folder_id, folder_tag = self.extract_folder_id_and_tag(folder_name)
            
            mp4_files = {f for f in folder_path.glob('*.mp4')}
            webp_files = {f.name for f in folder_path.glob('*.webp')}
            
            for mp4_file in mp4_files:
                base_name = mp4_file.stem
                webp_file = f"{base_name}.webp"
                
                if webp_file in webp_files:
                    # Get relative paths
                    rel_folder = folder_path.relative_to(settings.BASE_DIR)
                    mp4_rel_path = rel_folder / mp4_file.name
                    webp_rel_path = rel_folder / webp_file
                    
                    # Convert to Unix-like paths
                    mp4_rel_path_unix = self.to_unix_path(mp4_rel_path)
                    webp_rel_path_unix = self.to_unix_path(webp_rel_path)
                    
                    # Extract file ID and tags
                    file_id, file_tags = self.extract_file_id_and_tags(mp4_file)
                    
                    # Create combined ID in format "folder_id_file_id"
                    combined_id = f"{folder_id}_{file_id}"
                    
                    # Combine tags: folder tag first, then file tags
                    all_tags = [folder_tag] + file_tags if folder_tag else file_tags
                    
                    # Ensure we have at most 5 tags
                    all_tags = all_tags[:5]
                    
                    # Pad with None if needed
                    while len(all_tags) < 5:
                        all_tags.append(None)
                    
                    # Create tag string (e.g., "tag1_tag1.1_tag1.1.2")
                    tag_string = "_".join([t for t in all_tags if t])
                    
                    # Create standard paths with Unix format for client access
                    standard_mp4_path = f"standard/video/tags/{tag_string}/{combined_id}.mp4"
                    standard_webp_path = f"standard/cover/tags/{tag_string}/{combined_id}.webp"
                    
                    # Create or update database entry
                    VideoAsset.objects.create(
                        original_mp4_path=mp4_rel_path_unix,
                        original_cover_path=webp_rel_path_unix,
                        mp4_path=standard_mp4_path,
                        cover_path=standard_webp_path,
                        tag1=all_tags[0],
                        tag2=all_tags[1],
                        tag3=all_tags[2],
                        tag4=all_tags[3],
                        tag5=all_tags[4],
                        tag_string=tag_string,
                        numeric_id=combined_id
                    )
                    count += 1
                    
                    self.stdout.write(f"Imported: {mp4_rel_path_unix} with ID: {combined_id}, tags: {tag_string}")
                else:
                    self.stdout.write(self.style.WARNING(f"No cover found for {mp4_file.name}"))
                    
        self.stdout.write(f"Total videos imported: {count}")

    def process_explain_videos(self, root_path):
        """Record paths for explanation videos, covers, SRTs, and descriptions in the database."""
        self.stdout.write(f"Recording explain video paths from: {root_path}")
        count = 0

        for folder_path in root_path.glob('**'):
            if not folder_path.is_dir():
                continue

            folder_name = folder_path.name
            folder_id, _ = self.extract_folder_id_and_tag(folder_name)

            for explain_file in folder_path.glob('[0-9][0-9].mp4'):
                file_id = explain_file.stem  # e.g., "01"
                numeric_id = f"{folder_id}_{file_id}"

                # Find the matching VideoAsset
                try:
                    asset = VideoAsset.objects.get(numeric_id=numeric_id)
                except VideoAsset.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"No VideoAsset found for explain video: {explain_file} (numeric_id={numeric_id})"
                    ))
                    continue

                # Paths relative to BASE_DIR, using forward slashes
                rel_dir = folder_path.relative_to(settings.BASE_DIR)
                explain_video_path = f"{rel_dir.as_posix()}/{explain_file.name}"

                # Explain cover path (same file id, .webp)
                explain_cover_file = folder_path / f"{file_id}.webp"
                explain_cover_path = f"{rel_dir.as_posix()}/{explain_cover_file.name}" if explain_cover_file.exists() else None

                srt_file = explain_file.with_suffix('.srt')
                explain_srt_path = f"{rel_dir.as_posix()}/{srt_file.name}" if srt_file.exists() else None

                desc_file = folder_path / f"description_{file_id}.txt"
                descriptions_path = f"{rel_dir.as_posix()}/{desc_file.name}" if desc_file.exists() else None

                asset.explain_video_path = explain_video_path
                asset.explain_cover_path = explain_cover_path
                asset.explain_srt_path = explain_srt_path
                asset.descriptions_path = descriptions_path
                asset.save()

                self.stdout.write(f"Recorded: {explain_video_path} (cover: {explain_cover_path}, srt: {explain_srt_path}, desc: {descriptions_path})")
                count += 1

        self.stdout.write(f"Total explain videos processed: {count}")