import json
import os
from django.core.management.base import BaseCommand, CommandError
from evalpose.models import VideoConfig
from django.conf import settings

class Command(BaseCommand):
    help = 'Manage video configurations with CRUD operations'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')
        
        # Create command
        create_parser = subparsers.add_parser('create', help='Create a new video configuration')
        create_parser.add_argument('--numeric-id', required=True, help='Numeric ID for the video config')
        create_parser.add_argument('--description', default='', help='Description of the video')
        create_parser.add_argument('--key-angles', type=json.loads, default={}, help='Key angles as JSON string')
        create_parser.add_argument('--normalization-joints', type=json.loads, default=[], help='Normalization joints as JSON array')
        
        # Read command
        read_parser = subparsers.add_parser('read', help='Read video configuration(s)')
        read_parser.add_argument('--numeric-id', help='Numeric ID to filter by (optional)')
        read_parser.add_argument('--export', help='Export to JSON file path (optional)')
        read_parser.add_argument('--format', choices=['pretty', 'compact'], default='pretty', help='JSON output format')
        
        # Update command
        update_parser = subparsers.add_parser('update', help='Update an existing video configuration')
        update_parser.add_argument('--numeric-id', required=True, help='Numeric ID of the config to update')
        update_parser.add_argument('--description', help='New description (optional)')
        update_parser.add_argument('--key-angles', type=json.loads, help='New key angles as JSON string (optional)')
        update_parser.add_argument('--normalization-joints', type=json.loads, help='New normalization joints as JSON array (optional)')
        
        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a video configuration')
        delete_parser.add_argument('--numeric-id', required=True, help='Numeric ID of the config to delete')
        delete_parser.add_argument('--confirm', action='store_true', help='Confirm deletion without prompting')
        
        # Import command (similar to the original script)
        import_parser = subparsers.add_parser('import', help='Import configurations from JSON file')
        import_parser.add_argument('--file', default=os.path.join(settings.BASE_DIR, '..', '..', '..', 'Config', 'Config.json'),
                            help='Path to the JSON configuration file')

    def handle(self, *args, **options):
        action = options.get('action')
        
        if not action:
            self.stdout.write(self.style.ERROR('No action specified. Use --help for available actions.'))
            return
            
        if action == 'create':
            self._handle_create(options)
        elif action == 'read':
            self._handle_read(options)
        elif action == 'update':
            self._handle_update(options)
        elif action == 'delete':
            self._handle_delete(options)
        elif action == 'import':
            self._handle_import(options)
    
    def _handle_create(self, options):
        numeric_id = options['numeric_id']
        description = options['description']
        key_angles = options['key_angles']
        normalization_joints = options['normalization_joints']
        
        # Check if config already exists
        if VideoConfig.objects.filter(numeric_id=numeric_id).exists():
            self.stdout.write(self.style.WARNING(f"Configuration with ID {numeric_id} already exists. Use update instead."))
            return
        
        # Create new config
        config = VideoConfig.objects.create(
            numeric_id=numeric_id,
            description=description,
            key_angles=key_angles,
            normalization_joints=normalization_joints
        )
        
        self.stdout.write(self.style.SUCCESS(f"Created configuration with ID: {numeric_id}"))
    
    def _handle_read(self, options):
        numeric_id = options.get('numeric_id')
        export_path = options.get('export')
        json_format = options.get('format', 'pretty')
        
        # Filter configs
        if numeric_id:
            configs = VideoConfig.objects.filter(numeric_id=numeric_id)
            if not configs.exists():
                self.stdout.write(self.style.ERROR(f"No configuration found with ID: {numeric_id}"))
                return
        else:
            configs = VideoConfig.objects.all()
            
        # Convert to dictionary
        result = {}
        for config in configs:
            result[config.numeric_id] = {
                'description': config.description,
                'key_angles': config.key_angles,
                'normalization_joints': config.normalization_joints
            }
        
        # Export to file or print to console
        json_kwargs = {'indent': 4} if json_format == 'pretty' else {}
        
        if export_path:
            try:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, **json_kwargs)
                self.stdout.write(self.style.SUCCESS(f"Exported {len(result)} configurations to {export_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error exporting to file: {str(e)}"))
        else:
            self.stdout.write(json.dumps(result, **json_kwargs))
    
    def _handle_update(self, options):
        numeric_id = options['numeric_id']
        
        try:
            config = VideoConfig.objects.get(numeric_id=numeric_id)
        except VideoConfig.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No configuration found with ID: {numeric_id}"))
            return
        
        # Update only specified fields
        update_fields = []
        
        if options.get('description') is not None:
            config.description = options['description']
            update_fields.append('description')
            
        if options.get('key_angles') is not None:
            config.key_angles = options['key_angles']
            update_fields.append('key_angles')
            
        if options.get('normalization_joints') is not None:
            config.normalization_joints = options['normalization_joints']
            update_fields.append('normalization_joints')
        
        if update_fields:
            config.save(update_fields=update_fields)
            self.stdout.write(self.style.SUCCESS(f"Updated configuration with ID: {numeric_id}"))
        else:
            self.stdout.write(self.style.WARNING("No fields specified for update"))
    
    def _handle_delete(self, options):
        numeric_id = options['numeric_id']
        confirmed = options.get('confirm', False)
        
        try:
            config = VideoConfig.objects.get(numeric_id=numeric_id)
        except VideoConfig.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No configuration found with ID: {numeric_id}"))
            return
        
        if not confirmed:
            user_input = input(f"Are you sure you want to delete configuration with ID {numeric_id}? (y/N): ").lower()
            if user_input != 'y':
                self.stdout.write("Deletion cancelled.")
                return
        
        config.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted configuration with ID: {numeric_id}"))
    
    def _handle_import(self, options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            count = 0
            for filename, config in configs.items():
                # Extract the numeric part from the filename (e.g., "Actions\1.mp4" -> "01")
                video_number = filename.split('\\')[-1].split('.')[0]
                # Format the numeric_id as "01_XX" where XX is the video number padded to 2 digits
                numeric_id = f"01_{int(video_number):02d}"
                
                # Create or update the configuration
                obj, created = VideoConfig.objects.update_or_create(
                    numeric_id=numeric_id,
                    defaults={
                        'key_angles': config.get('KEY_ANGLES', {}),
                        'normalization_joints': config.get('NORMALIZATION_JOINTS', []),
                        'description': config.get('Describe', '')
                    }
                )
                
                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{action} config for {numeric_id}: {obj.description}"))
                count += 1
            
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} configurations"))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing configurations: {str(e)}'))