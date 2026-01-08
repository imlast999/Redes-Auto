# -*- coding: utf-8 -*-
"""
Configuración optimizada del Instagram Video Dashboard
"""

import os
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path(__file__).parent.parent
VIDEOS_DIR = BASE_DIR / "videos"
CONFIG_DIR = BASE_DIR / "config"

# Directorios de videos
PENDING_DIR = VIDEOS_DIR / "pending"
PROCESSED_DIR = VIDEOS_DIR / "processed"
PUBLISHED_DIR = VIDEOS_DIR / "published"

# Asegurar que los directorios existan
for directory in [VIDEOS_DIR, CONFIG_DIR, PENDING_DIR, PROCESSED_DIR, PUBLISHED_DIR]:
    directory.mkdir(exist_ok=True)

# Configuración por defecto
DEFAULT_SETTINGS = {
    'default_watermark': '@yourusername',
    'default_quality': 'Medium',
    'max_file_size': 100,  # MB
    'auto_watermark': True,
    'auto_resize': True,
    'preferred_format': '9:16 (Stories/Reels)',
    'watermark_position': 'bottom-right',
    'video_formats': ['.mp4', '.avi', '.mov', '.mkv'],
    'luxury_keywords': [
        'luxury', 'lujo', 'rich', 'wealth', 'expensive', 'mansion', 
        'supercar', 'yacht', 'dubai', 'monaco', 'millionaire', 
        'billionaire', 'lifestyle', 'exclusive', 'premium'
    ]
}

# Configuración de horarios
SCHEDULER_CONFIG = {
    'enabled': False,
    'weekday_slots': {
        'morning': {'start': '07:00', 'end': '09:00'},
        'evening': {'start': '18:00', 'end': '21:00'}
    },
    'weekend_slots': {
        'midday': {'start': '10:00', 'end': '13:00'}
    },
    'posts_per_day': {
        'weekdays': 2,
        'weekends': 1
    }
}

# Configuración de Instagram API
INSTAGRAM_CONFIG = {
    'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
    'user_id': os.getenv('INSTAGRAM_USER_ID', ''),
    'username': os.getenv('INSTAGRAM_USERNAME', ''),
    'password': os.getenv('INSTAGRAM_PASSWORD', '')
}

# Configuración de APIs de IA
AI_CONFIG = {
    'huggingface_api_key': os.getenv('HUGGINGFACE_API_KEY', ''),
    'groq_api_key': os.getenv('GROQ_API_KEY', ''),
    'cohere_api_key': os.getenv('COHERE_API_KEY', ''),
    'google_tts_api_key': os.getenv('GOOGLE_TTS_API_KEY', ''),
    'replicate_api_key': os.getenv('REPLICATE_API_KEY', ''),
    'deepai_api_key': os.getenv('DEEPAI_API_KEY', '')
}

# Configuración de notificaciones
NOTIFICATION_CONFIG = {
    'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
    'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL', '')
}

# Configuración de almacenamiento
STORAGE_CONFIG = {
    'cloudinary_url': os.getenv('CLOUDINARY_URL', ''),
    'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', ''),
    'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
    'aws_s3_bucket': os.getenv('AWS_S3_BUCKET', '')
}

# Configuración global
SETTINGS = DEFAULT_SETTINGS