import os
import json
from pathlib import Path

# Default settings
DEFAULT_SETTINGS = {
    'default_watermark': '@yourusername',
    'default_quality': 'Medium',
    'max_file_size': 100,  # MB
    'supported_formats': ['.mp4', '.avi', '.mov', '.mkv'],
    'instagram_post_size': {
        'stories': (1080, 1920),
        'square': (1080, 1080),
        'portrait': (1080, 1350)
    },
    'video_bitrates': {
        'High': '8000k',
        'Medium': '4000k', 
        'Low': '2000k'
    },
    'watermark_settings': {
        'font_size': 50,
        'color': 'white',
        'stroke_color': 'black',
        'stroke_width': 2,
        'margin': 20
    },
    'auto_backup': True,
    'backup_retention_days': 30,
    'processing_threads': 2
}

def load_user_settings():
    """Load user settings from file"""
    settings_file = "config/user_settings.json"
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                user_settings = json.load(f)
                # Merge with defaults
                settings = DEFAULT_SETTINGS.copy()
                settings.update(user_settings)
                return settings
        except Exception as e:
            print(f"Error loading user settings: {str(e)}")
    
    return DEFAULT_SETTINGS

def save_user_settings(settings):
    """Save user settings to file"""
    settings_file = "config/user_settings.json"
    
    try:
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving user settings: {str(e)}")
        return False

# Load settings
SETTINGS = load_user_settings()

# Environment variables with fallbacks
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID', '')
INSTAGRAM_CLIENT_SECRET = os.getenv('INSTAGRAM_CLIENT_SECRET', '')

# Paths
BASE_DIR = Path(__file__).parent.parent
VIDEOS_DIR = BASE_DIR / "videos"
ASSETS_DIR = BASE_DIR / "assets"
CONFIG_DIR = BASE_DIR / "config"

# Create directories if they don't exist
VIDEOS_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

(VIDEOS_DIR / "pending").mkdir(exist_ok=True)
(VIDEOS_DIR / "processed").mkdir(exist_ok=True)
(VIDEOS_DIR / "published").mkdir(exist_ok=True)
(ASSETS_DIR / "watermarks").mkdir(exist_ok=True)
