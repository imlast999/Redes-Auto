import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import tempfile
import zipfile

class FileManager:
    def __init__(self):
        self.base_path = "videos"
        self.folders = {
            'pending': os.path.join(self.base_path, 'pending'),
            'processed': os.path.join(self.base_path, 'processed'),
            'published': os.path.join(self.base_path, 'published'),
            'scripts': os.path.join(self.base_path, 'scripts')
        }
        
        self._ensure_folders()
        
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm'}
        self.script_extensions = {'.txt'}
    
    def _ensure_folders(self):
        for folder_path in self.folders.values():
            os.makedirs(folder_path, exist_ok=True)
        os.makedirs("assets/watermarks", exist_ok=True)
        os.makedirs("config", exist_ok=True)
    
    def get_pending_videos(self):
        return self._get_videos_in_folder(self.folders['pending'])
    
    def get_processed_videos(self):
        return self._get_videos_in_folder(self.folders['processed'])
    
    def get_published_videos(self):
        return self._get_videos_in_folder(self.folders['published'])
    
    def get_scripts(self):
        return self._get_files_in_folder(self.folders['scripts'], self.script_extensions)
    
    def _get_videos_in_folder(self, folder_path):
        return self._get_files_in_folder(folder_path, self.video_extensions)
    
    def _get_files_in_folder(self, folder_path, extensions):
        files = []
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file.lower())
                    if ext in extensions:
                        files.append(file_path)
        return sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    
    def save_uploaded_file(self, uploaded_file, folder='pending'):
        try:
            folder_path = self.folders.get(folder, self.folders['pending'])
            file_path = os.path.join(folder_path, uploaded_file.name if hasattr(uploaded_file, 'name') else os.path.basename(uploaded_file))
            with open(file_path, "wb") as f:
                if hasattr(uploaded_file, 'getbuffer'):
                    f.write(uploaded_file.getbuffer())
                else:
                    with open(uploaded_file, 'rb') as src:
                        f.write(src.read())
            return file_path
        except Exception as e:
            print(f"Error saving uploaded file: {str(e)}")
            return None
    
    def copy_video_to_pending(self, source_path):
        try:
            filename = os.path.basename(source_path)
            destination = os.path.join(self.folders['pending'], filename)
            if os.path.exists(destination):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(destination):
                    new_filename = f"{base}_{counter}{ext}"
                    destination = os.path.join(self.folders['pending'], new_filename)
                    counter += 1
            shutil.copy2(source_path, destination)
            return True
        except Exception as e:
            print(f"Error copying video to pending: {str(e)}")
            return False
    
    def move_to_processed(self, source_path, processed_path):
        try:
            os.remove(source_path)
            return True
        except Exception as e:
            print(f"Error moving to processed: {str(e)}")
            return False
    
    def move_to_published(self, processed_path):
        try:
            filename = os.path.basename(processed_path)
            published_path = os.path.join(self.folders['published'], filename)
            if os.path.exists(published_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(published_path):
                    new_filename = f"{base}_{counter}{ext}"
                    published_path = os.path.join(self.folders['published'], new_filename)
                    counter += 1
            shutil.move(processed_path, published_path)
            self._log_publication(filename)
            return True
        except Exception as e:
            print(f"Error moving to published: {str(e)}")
            return False
    
    def delete_video(self, video_path):
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting video: {str(e)}")
            return False
    
    def scan_folder_for_videos(self, folder_path):
        videos = []
        try:
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        _, ext = os.path.splitext(file.lower())
                        if ext in self.video_extensions:
                            full_path = os.path.join(root, file)
                            videos.append(full_path)
        except Exception as e:
            print(f"Error scanning folder: {str(e)}")
        return sorted(videos)
    
    def get_recent_activity(self, limit=10):
        activity = []
        for folder_name, folder_path in self.folders.items():
            extensions = self.video_extensions if folder_name != 'scripts' else self.script_extensions
            files = self._get_files_in_folder(folder_path, extensions)
            for file in files[:limit]:
                try:
                    stat = os.stat(file)
                    activity.append({
                        'filename': os.path.basename(file),
                        'folder': folder_name.title(),
                        'size_mb': round(stat.st_size / (1024 * 1024), 2) if folder_name != 'scripts' else 0,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                        'path': file
                    })
                except:
                    continue
        activity.sort(key=lambda x: x['modified'], reverse=True)
        return activity[:limit]
    
    def clear_folder(self, folder_type):
        try:
            folder_path = self.folders.get(folder_type)
            if not folder_path:
                return 0
            count = 0
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            return count
        except Exception as e:
            print(f"Error clearing folder: {str(e)}")
            return 0
    
    def create_backup(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"video_backup_{timestamp}.zip"
            backup_path = os.path.join(tempfile.gettempdir(), backup_filename)
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for folder_name, folder_path in self.folders.items():
                    if os.path.exists(folder_path):
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(folder_name, file)
                                zipf.write(file_path, arcname)
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return None
    
    def _log_publication(self, filename):
        try:
            log_file = "config/publication_log.json"
            log_entry = {
                'filename': filename,
                'published_at': datetime.now().isoformat(),
                'timestamp': datetime.now().timestamp()
            }
            log_data = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            log_data.append(log_entry)
            log_data = log_data[-100:]
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            print(f"Error logging publication: {str(e)}")
    
    def get_folder_stats(self):
        stats = {}
        for folder_name, folder_path in self.folders.items():
            extensions = self.video_extensions if folder_name != 'scripts' else self.script_extensions
            files = self._get_files_in_folder(folder_path, extensions)
            total_size = 0
            for file in files:
                try:
                    total_size += os.path.getsize(file)
                except:
                    continue
            stats[folder_name] = {
                'count': len(files),
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        return stats