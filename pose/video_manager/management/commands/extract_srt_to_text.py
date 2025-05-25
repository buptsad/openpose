import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Extract and concatenate all words from SRT files in a folder into description_{id:2d}.txt files.'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=str, default='standard/explain_videos',
                            help='Path to SRT files directory')
        parser.add_argument('--target', type=str, default='standard/explain_videos',
                            help='Path to save description files')

    def handle(self, *args, **options):
        source_path = Path(settings.BASE_DIR) / options['source']
        target_path = Path(settings.BASE_DIR) / options['target']
        target_path.mkdir(parents=True, exist_ok=True)

        count = 0
        for srt_file in source_path.glob('*.srt'):
            text = self.extract_text_from_srt(srt_file)
            if text:
                # Use only the numeric id part for output file name
                # e.g. 01_02.srt -> 02, 12.srt -> 12
                id_part = srt_file.stem.split('_')[-1]
                txt_path = target_path / f'description_{id_part}.txt'
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.stdout.write(f"Created {txt_path}")
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {count} SRT files"))

    def extract_text_from_srt(self, srt_path):
        """Extract and concatenate all text from an SRT file."""
        try:
            with open(srt_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception:
            return None

        # Remove SRT numbering and timestamps, keep only text lines
        lines = content.splitlines()
        text_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip lines that are just numbers or timestamps
            if re.match(r'^\d+$', line):
                continue
            if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} -->', line):
                continue
            # Remove HTML tags if any
            line = re.sub(r'<[^>]+>', '', line)
            text_lines.append(line)
        return ' '.join(text_lines)