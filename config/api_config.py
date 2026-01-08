# -*- coding: utf-8 -*-
"""
Configuración completa de APIs para Instagram Video Dashboard
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class APIConfig:
    def __init__(self):
        # APIs de IA
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.cohere_api_key = os.getenv('COHERE_API_KEY', '')
        
        # APIs de TTS
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', '')
        self.google_tts_api_key = os.getenv('GOOGLE_TTS_API_KEY', '')
        self.azure_speech_key = os.getenv('AZURE_SPEECH_KEY', '')
        self.ibm_watson_api_key = os.getenv('IBM_WATSON_API_KEY', '')
        
        # APIs de generación de imágenes
        self.stability_ai_api_key = os.getenv('STABILITY_AI_API_KEY', '')
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY', '')
        self.deepai_api_key = os.getenv('DEEPAI_API_KEY', '')
        self.getimg_api_key = os.getenv('GETIMG_API_KEY', '')
        
        # APIs de almacenamiento
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', '')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        self.aws_s3_bucket = os.getenv('AWS_S3_BUCKET', '')
        self.cloudinary_url = os.getenv('CLOUDINARY_URL', '')
        self.imgur_client_id = os.getenv('IMGUR_CLIENT_ID', '')
        
        # APIs de Instagram
        self.instagram_access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.instagram_user_id = os.getenv('INSTAGRAM_USER_ID', '')
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME', '')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD', '')
        
        # APIs de notificaciones
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')
    
    def get_ai_apis_status(self):
        """Obtener estado de APIs de IA"""
        return {
            'openai': bool(self.openai_api_key),
            'huggingface': bool(self.huggingface_api_key),
            'groq': bool(self.groq_api_key),
            'cohere': bool(self.cohere_api_key)
        }
    
    def get_tts_apis_status(self):
        """Obtener estado de APIs de TTS"""
        return {
            'elevenlabs': bool(self.elevenlabs_api_key),
            'google_tts': bool(self.google_tts_api_key),
            'azure_speech': bool(self.azure_speech_key),
            'ibm_watson': bool(self.ibm_watson_api_key)
        }
    
    def get_image_apis_status(self):
        """Obtener estado de APIs de generación de imágenes"""
        return {
            'stability_ai': bool(self.stability_ai_api_key),
            'replicate': bool(self.replicate_api_key),
            'deepai': bool(self.deepai_api_key),
            'getimg': bool(self.getimg_api_key)
        }
    
    def get_storage_apis_status(self):
        """Obtener estado de APIs de almacenamiento"""
        return {
            'aws_s3': bool(self.aws_access_key_id and self.aws_secret_access_key and self.aws_s3_bucket),
            'cloudinary': bool(self.cloudinary_url),
            'imgur': bool(self.imgur_client_id)
        }
    
    def get_instagram_apis_status(self):
        """Obtener estado de APIs de Instagram"""
        return {
            'graph_api': bool(self.instagram_access_token and self.instagram_user_id),
            'instagrapi': bool(self.instagram_username and self.instagram_password)
        }
    
    def get_notification_apis_status(self):
        """Obtener estado de APIs de notificaciones"""
        return {
            'telegram': bool(self.telegram_bot_token and self.telegram_chat_id),
            'discord': bool(self.discord_webhook_url)
        }
    
    def get_all_apis_status(self):
        """Obtener estado de todas las APIs"""
        return {
            'ai': self.get_ai_apis_status(),
            'tts': self.get_tts_apis_status(),
            'image': self.get_image_apis_status(),
            'storage': self.get_storage_apis_status(),
            'instagram': self.get_instagram_apis_status(),
            'notifications': self.get_notification_apis_status()
        }

# Instancia global
api_config = APIConfig()