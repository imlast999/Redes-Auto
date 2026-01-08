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
            'published': os.path.join(self.base_path, 'published')
        }
        
        # Create folders if they don't exist
        self._ensure_folders()
        
        # Video file extensions
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm'}
    
    def _ensure_folders(self):
        """Create necessary folders if they don't exist"""
        for folder_path in self.folders.values():
            os.makedirs(folder_path, exist_ok=True)
        
        # Create assets folder for watermarks
        os.makedirs("assets/watermarks", exist_ok=True)
        os.makedirs("config", exist_ok=True)
    
    def get_pending_videos(self):
        """Get list of videos in pending folder"""
        return self._get_videos_in_folder(self.folders['pending'])
    
    def get_processed_videos(self):
        """Get list of videos in processed folder"""
        return self._get_videos_in_folder(self.folders['processed'])
    
    def get_published_videos(self):
        """Get list of videos in published folder"""
        return self._get_videos_in_folder(self.folders['published'])
    
    def _get_videos_in_folder(self, folder_path):
        """Get all video files in a specific folder"""
        videos = []
        
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file.lower())
                    if ext in self.video_extensions:
                        videos.append(file_path)
        
        return sorted(videos, key=lambda x: os.path.getmtime(x), reverse=True)
    
    def save_uploaded_file(self, uploaded_file):
        """Save an uploaded file to the pending folder"""
        try:
            file_path = os.path.join(self.folders['pending'], uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            return file_path
        
        except Exception as e:
            print(f"Error saving uploaded file: {str(e)}")
            return None
    
    def copy_video_to_pending(self, source_path):
        """Copy a video file to the pending folder"""
        try:
            filename = os.path.basename(source_path)
            destination = os.path.join(self.folders['pending'], filename)
            
            # Check if file already exists
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
        """Move video from pending to processed folder"""
        try:
            # Remove original from pending if it exists
            if os.path.exists(source_path):
                os.remove(source_path)
            
            return True
        
        except Exception as e:
            print(f"Error moving to processed: {str(e)}")
            return False
    
    def move_to_published(self, processed_path):
        """Move video from processed to published folder"""
        try:
            filename = os.path.basename(processed_path)
            published_path = os.path.join(self.folders['published'], filename)
            
            # Check if file already exists in published
            if os.path.exists(published_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(published_path):
                    new_filename = f"{base}_{counter}{ext}"
                    published_path = os.path.join(self.folders['published'], new_filename)
                    counter += 1
            
            shutil.move(processed_path, published_path)
            
            # Log the publication
            self._log_publication(filename)
            
            return True
        
        except Exception as e:
            print(f"Error moving to published: {str(e)}")
            return False
    
    def delete_video(self, video_path):
        """Delete a video file"""
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                return True
            return False
        
        except Exception as e:
            print(f"Error deleting video: {str(e)}")
            return False
    
    def scan_folder_for_videos(self, folder_path):
        """Scan a folder for video files"""
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
        """Get recent activity across all folders"""
        activity = []
        
        for folder_name, folder_path in self.folders.items():
            for video in self._get_videos_in_folder(folder_path):
                try:
                    stat = os.stat(video)
                    activity.append({
                        'filename': os.path.basename(video),
                        'folder': folder_name.title(),
                        'size_mb': round(stat.st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                        'path': video
                    })
                except:
                    continue
        
        activity.sort(key=lambda x: x['modified'], reverse=True)
        return activity[:limit]
    
    def clear_folder(self, folder_type):
        """Clear all files from a specific folder"""
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
        """Create a backup of all videos"""
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
        """Log when a video is published"""
        try:
            log_file = "config/publication_log.json"
            log_entry = {
                'filename': filename,
                'published_at': datetime.now().isoformat(),
                'timestamp': datetime.now().timestamp()
            }
            
            # Load existing log
            log_data = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            
            # Add new entry
            log_data.append(log_entry)
            
            # Keep only last 100 entries
            log_data = log_data[-100:]
            
            # Save log
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        except Exception as e:
            print(f"Error logging publication: {str(e)}")
    
    def get_folder_stats(self):
        """Get statistics about each folder"""
        stats = {}
        
        for folder_name, folder_path in self.folders.items():
            videos = self._get_videos_in_folder(folder_path)
            total_size = sum(os.path.getsize(v) for v in videos if os.path.exists(v))
            
            stats[folder_name] = {
                'count': len(videos),
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        
        return stats
    
    def organize_by_date(self, folder_type='processed'):
        """Organize videos in a folder by date"""
        try:
            folder_path = self.folders.get(folder_type)
            if not folder_path:
                return False
            
            videos = self._get_videos_in_folder(folder_path)
            
            for video in videos:
                # Get file modification date
                stat = os.stat(video)
                date_folder = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                
                # Create date subfolder
                date_path = os.path.join(folder_path, date_folder)
                os.makedirs(date_path, exist_ok=True)
                
                # Move file to date folder
                filename = os.path.basename(video)
                new_path = os.path.join(date_path, filename)
                shutil.move(video, new_path)
            
            return True
        
        except Exception as e:
            print(f"Error organizing by date: {str(e)}")
            return False
