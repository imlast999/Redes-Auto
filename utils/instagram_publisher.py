# -*- coding: utf-8 -*-
"""
Publicador de Instagram completo para Instagram Video Dashboard
Incluye publicación automática y manual
"""

import os
import requests
import json
import time
from datetime import datetime
from typing import Optional, Dict, Tuple
import tempfile
import shutil

class InstagramPublisher:
    def __init__(self):
        # Instagram Graph API
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.user_id = os.getenv('INSTAGRAM_USER_ID', '')
        self.graph_api_base = 'https://graph.instagram.com'
        
        # Instagrapi
        self.username = os.getenv('INSTAGRAM_USERNAME', '')
        self.password = os.getenv('INSTAGRAM_PASSWORD', '')
        
        # Estado de configuración
        self.configured = False
        self.api_type = None
        
        self._check_configuration()
    
    def _check_configuration(self):
        """Verificar configuración"""
        if self.access_token and self.user_id:
            if self._test_graph_api():
                self.configured = True
                self.api_type = 'graph_api'
        elif self.username and self.password:
            if self._test_instagrapi():
                self.configured = True
                self.api_type = 'instagrapi'
    
    def _test_graph_api(self):
        """Probar Graph API"""
        try:
            url = f"{self.graph_api_base}/me"
            params = {'access_token': self.access_token}
            response = requests.get(url, params=params, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _test_instagrapi(self):
        """Probar Instagrapi"""
        try:
            from instagrapi import Client
            return True
        except ImportError:
            return False
    
    def is_configured(self):
        """Verificar si está configurado"""
        return self.configured
    
    def configure(self, access_token=None, user_id=None, username=None, password=None):
        """Configurar credenciales"""
        if access_token and user_id:
            self.access_token = access_token
            self.user_id = user_id
            
            # Guardar en archivo de configuración
            config = {
                'access_token': access_token,
                'user_id': user_id,
                'configured_at': datetime.now().isoformat()
            }
            
            os.makedirs('config', exist_ok=True)
            with open('config/instagram_config.json', 'w') as f:
                json.dump(config, f, indent=2)
        
        elif username and password:
            self.username = username
            self.password = password
        
        self._check_configuration()
        return self.configured
    
    def get_account_type(self):
        """Obtener tipo de cuenta"""
        if not self.configured:
            return None
        
        if self.api_type == 'graph_api':
            return self._get_account_type_graph_api()
        else:
            return self._get_account_type_instagrapi()
    
    def _get_account_type_graph_api(self):
        """Obtener tipo de cuenta usando Graph API"""
        try:
            url = f"{self.graph_api_base}/{self.user_id}"
            params = {
                'fields': 'id,username,account_type',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error getting account type: {str(e)}")
            return None
    
    def _get_account_type_instagrapi(self):
        """Obtener tipo de cuenta usando Instagrapi"""
        try:
            from instagrapi import Client
            
            cl = Client()
            cl.login(self.username, self.password)
            
            user_info = cl.user_info_by_username(self.username)
            
            return {
                'id': str(user_info.pk),
                'username': user_info.username,
                'account_type': 'BUSINESS' if user_info.is_business else 'PERSONAL'
            }
        
        except Exception as e:
            print(f"Error getting account type with Instagrapi: {str(e)}")
            return None
    
    def upload_video_to_instagram(self, video_path, caption="", hashtags=None):
        """Subir video a Instagram"""
        if not self.configured:
            return False, "Instagram no configurado"
        
        if not os.path.exists(video_path):
            return False, "Video no encontrado"
        
        # Validar video
        is_valid, validation_msg = self.validate_video_for_instagram(video_path)
        if not is_valid:
            return False, f"Video no válido: {validation_msg}"
        
        # Agregar hashtags al caption
        if hashtags:
            if isinstance(hashtags, list):
                hashtags_str = ' '.join([f'#{tag}' if not tag.startswith('#') else tag for tag in hashtags])
            else:
                hashtags_str = hashtags
            
            caption = f"{caption}\n\n{hashtags_str}"
        
        if self.api_type == 'graph_api':
            return self._upload_video_graph_api(video_path, caption)
        else:
            return self._upload_video_instagrapi(video_path, caption)
    
    def _upload_video_graph_api(self, video_path, caption):
        """Subir video usando Graph API"""
        try:
            # Paso 1: Crear contenedor de media
            url = f"{self.graph_api_base}/{self.user_id}/media"
            
            # Subir video a un servicio temporal (esto es una simplificación)
            # En la práctica, necesitarías subir el video a un servidor accesible públicamente
            
            data = {
                'media_type': 'VIDEO',
                'video_url': 'URL_DEL_VIDEO',  # Aquí iría la URL pública del video
                'caption': caption,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=data, timeout=60)
            
            if response.status_code == 200:
                container_id = response.json()['id']
                
                # Paso 2: Publicar el contenedor
                publish_url = f"{self.graph_api_base}/{self.user_id}/media_publish"
                publish_data = {
                    'creation_id': container_id,
                    'access_token': self.access_token
                }
                
                publish_response = requests.post(publish_url, data=publish_data, timeout=60)
                
                if publish_response.status_code == 200:
                    return True, "Video publicado exitosamente"
                else:
                    return False, f"Error publicando: {publish_response.text}"
            else:
                return False, f"Error creando contenedor: {response.text}"
        
        except Exception as e:
            return False, f"Error con Graph API: {str(e)}"
    
    def _upload_video_instagrapi(self, video_path, caption):
        """Subir video usando Instagrapi"""
        try:
            from instagrapi import Client
            
            cl = Client()
            cl.login(self.username, self.password)
            
            # Subir video
            media = cl.video_upload(video_path, caption)
            
            if media:
                return True, f"Video publicado exitosamente (ID: {media.pk})"
            else:
                return False, "Error desconocido al publicar"
        
        except Exception as e:
            return False, f"Error con Instagrapi: {str(e)}"
    
    def upload_image_to_instagram(self, image_path, caption="", hashtags=None):
        """Subir imagen a Instagram"""
        if not self.configured:
            return False, "Instagram no configurado"
        
        if not os.path.exists(image_path):
            return False, "Imagen no encontrada"
        
        # Agregar hashtags al caption
        if hashtags:
            if isinstance(hashtags, list):
                hashtags_str = ' '.join([f'#{tag}' if not tag.startswith('#') else tag for tag in hashtags])
            else:
                hashtags_str = hashtags
            
            caption = f"{caption}\n\n{hashtags_str}"
        
        if self.api_type == 'instagrapi':
            return self._upload_image_instagrapi(image_path, caption)
        else:
            return False, "Subida de imágenes solo disponible con Instagrapi"
    
    def _upload_image_instagrapi(self, image_path, caption):
        """Subir imagen usando Instagrapi"""
        try:
            from instagrapi import Client
            
            cl = Client()
            cl.login(self.username, self.password)
            
            # Subir imagen
            media = cl.photo_upload(image_path, caption)
            
            if media:
                return True, f"Imagen publicada exitosamente (ID: {media.pk})"
            else:
                return False, "Error desconocido al publicar"
        
        except Exception as e:
            return False, f"Error con Instagrapi: {str(e)}"
    
    def schedule_post(self, media_path, caption, publish_time):
        """Programar publicación (simulado)"""
        # Instagram no permite programación directa via API
        # Esta función guardaría la información para publicación posterior
        
        schedule_data = {
            'media_path': media_path,
            'caption': caption,
            'publish_time': publish_time.isoformat(),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        # Guardar en archivo de programación
        os.makedirs('config', exist_ok=True)
        schedule_file = 'config/scheduled_posts.json'
        
        scheduled_posts = []
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                scheduled_posts = json.load(f)
        
        scheduled_posts.append(schedule_data)
        
        with open(schedule_file, 'w') as f:
            json.dump(scheduled_posts, f, indent=2)
        
        return True, "Post programado exitosamente"
    
    def get_scheduled_posts(self):
        """Obtener posts programados"""
        schedule_file = 'config/scheduled_posts.json'
        
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                return json.load(f)
        
        return []
    
    def validate_video_for_instagram(self, video_path):
        """Validar video para Instagram"""
        if not os.path.exists(video_path):
            return False, "Archivo no encontrado"
        
        # Verificar tamaño
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        if file_size > 100:
            return False, f"Archivo muy grande: {file_size:.1f}MB (máximo 100MB)"
        
        # Verificar extensión
        valid_extensions = ['.mp4', '.mov']
        file_ext = os.path.splitext(video_path)[1].lower()
        if file_ext not in valid_extensions:
            return False, f"Formato no válido: {file_ext} (usar MP4 o MOV)"
        
        return True, "Video válido"
    
    def validate_image_for_instagram(self, image_path):
        """Validar imagen para Instagram"""
        if not os.path.exists(image_path):
            return False, "Archivo no encontrado"
        
        # Verificar tamaño
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
        if file_size > 8:
            return False, f"Archivo muy grande: {file_size:.1f}MB (máximo 8MB)"
        
        # Verificar extensión
        valid_extensions = ['.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in valid_extensions:
            return False, f"Formato no válido: {file_ext} (usar JPG o PNG)"
        
        return True, "Imagen válida"
    
    def get_publishing_limits(self):
        """Obtener límites de publicación"""
        return {
            'video_duration_max': '60 segundos (Reels)',
            'video_size_max': '100 MB',
            'image_size_max': '8 MB',
            'caption_length_max': '2,200 caracteres',
            'hashtags_max': '30 por post',
            'posts_per_day_recommended': '1-2 posts',
            'video_formats': 'MP4, MOV',
            'image_formats': 'JPG, PNG',
            'aspect_ratios': '1.91:1 a 4:5'
        }
    
    def get_optimal_hashtags(self, theme):
        """Obtener hashtags óptimos para un tema"""
        hashtag_sets = {
            'luxury': [
                'luxury', 'lifestyle', 'wealth', 'rich', 'expensive',
                'millionaire', 'success', 'motivation', 'mindset', 'goals',
                'entrepreneur', 'business', 'money', 'investment', 'finance'
            ],
            'fitness': [
                'fitness', 'gym', 'workout', 'health', 'fit',
                'training', 'muscle', 'bodybuilding', 'cardio', 'strength'
            ],
            'travel': [
                'travel', 'vacation', 'adventure', 'explore', 'wanderlust',
                'trip', 'journey', 'destination', 'tourism', 'holiday'
            ],
            'food': [
                'food', 'foodie', 'delicious', 'yummy', 'cooking',
                'recipe', 'chef', 'restaurant', 'homemade', 'tasty'
            ]
        }
        
        return hashtag_sets.get(theme, hashtag_sets['luxury'])[:15]  # Máximo 15 hashtags
    
    def generate_caption(self, theme, custom_text=""):
        """Generar caption automático"""
        caption_templates = {
            'luxury': [
                "Vivir la vida que siempre soñaste no es un lujo, es una decisión. 💎",
                "El éxito no es casualidad, es el resultado de decisiones inteligentes. 🏆",
                "Mientras otros duermen, los millonarios construyen imperios. 🌟"
            ],
            'motivation': [
                "Tu única competencia eres tú mismo de ayer. 💪",
                "Los sueños no tienen fecha de caducidad. ✨",
                "El fracaso es solo una oportunidad para empezar de nuevo con más inteligencia. 🚀"
            ],
            'business': [
                "En el mundo de los negocios, la velocidad mata. ⚡",
                "No busques oportunidades, créalas. 💼",
                "El dinero es solo una herramienta, la mentalidad es el poder real. 🧠"
            ]
        }
        
        templates = caption_templates.get(theme, caption_templates['luxury'])
        base_caption = templates[0]  # Usar el primero por defecto
        
        if custom_text:
            return f"{custom_text}\n\n{base_caption}"
        
        return base_caption
    
    def get_api_status(self):
        """Obtener estado de la API"""
        return {
            'configured': self.configured,
            'api_type': self.api_type,
            'graph_api_available': bool(self.access_token and self.user_id),
            'instagrapi_available': bool(self.username and self.password),
            'last_check': datetime.now().isoformat()
        }