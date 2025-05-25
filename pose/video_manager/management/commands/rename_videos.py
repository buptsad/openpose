from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = "Rename .mp4 and .srt files in the given folder to two-digit numbers if their names are digits."

    def add_arguments(self, parser):
        parser.add_argument('folder_path', type=str, help='Path to the folder containing the videos')

    def handle(self, *args, **options):
        folder = options['folder_path']

        if not os.path.isdir(folder):
            self.stderr.write(f"Error: {folder} is not a valid directory.")
            return

        for filename in os.listdir(folder):
            if filename.endswith('.mp4') or filename.endswith('.srt'):
                name, ext = os.path.splitext(filename)
                if name.isdigit():
                    new_name = f"{int(name):02d}{ext}"
                    old_path = os.path.join(folder, filename)
                    new_path = os.path.join(folder, new_name)
                    if old_path != new_path:
                        os.rename(old_path, new_path)
                        self.stdout.write(f"Renamed: {filename} -> {new_name}")