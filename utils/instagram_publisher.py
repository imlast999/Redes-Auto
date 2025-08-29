# -*- coding: utf-8 -*-
import requests
import json
import os
import time
from datetime import datetime

class InstagramPublisher:
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.user_id = os.getenv('INSTAGRAM_USER_ID', '')
        self.base_url = "https://graph.facebook.com/v18.0"
        self.config_file = "config/instagram_publisher.json"
        self.load_config()
    
    def load_config(self):
        """Cargar configuración del publicador"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.access_token = config.get('access_token', self.access_token)
                    self.user_id = config.get('user_id', self.user_id)
        except Exception as e:
            print(f"Error loading publisher config: {str(e)}")
    
    def configure(self, access_token, user_id):
        """Configurar credenciales de Instagram"""
        self.access_token = access_token
        self.user_id = user_id
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config = {
                'access_token': access_token,
                'user_id': user_id,
                'configured_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        except Exception as e:
            print(f"Error saving publisher config: {str(e)}")
    
    def is_configured(self):
        """Verificar si está configurado correctamente"""
        return bool(self.access_token and self.user_id)
    
    def upload_video_to_instagram(self, video_path, caption=""):
        """
        Publicar video a Instagram usando Graph API
        
        LIMITACIONES IMPORTANTES:
        - Requiere cuenta Business/Creator verificada
        - Videos deben ser MP4, duración 3-60 segundos para Reels
        - Tamaño máximo: 100MB
        - Aspect ratio recomendado: 9:16 para Reels
        """
        if not self.is_configured():
            return False, "Instagram API no está configurado"
        
        if not os.path.exists(video_path):
            return False, "Archivo de video no encontrado"
        
        try:
            # Paso 1: Crear container de media
            container_response = self._create_video_container(video_path, caption)
            if not container_response['success']:
                return False, container_response['message']
            
            container_id = container_response['container_id']
            
            # Paso 2: Verificar estado del container
            status_ok = self._wait_for_container_ready(container_id)
            if not status_ok:
                return False, "Error en procesamiento del video"
            
            # Paso 3: Publicar el container
            publish_response = self._publish_container(container_id)
            if publish_response['success']:
                return True, f"Video publicado exitosamente. ID: {publish_response['media_id']}"
            else:
                return False, publish_response['message']
        
        except Exception as e:
            return False, f"Error al publicar: {str(e)}"
    
    def _create_video_container(self, video_path, caption):
        """Crear container de video en Instagram"""
        try:
            # Subir video a un servicio temporal (necesario para Instagram API)
            video_url = self._upload_to_temporary_storage(video_path)
            if not video_url:
                return {'success': False, 'message': 'Error al subir video temporal'}
            
            url = f"{self.base_url}/{self.user_id}/media"
            
            params = {
                'media_type': 'REELS',
                'video_url': video_url,
                'caption': caption,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': True,
                'container_id': data.get('id'),
                'message': 'Container creado exitosamente'
            }
        
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Error en API: {str(e)}'}
    
    def _wait_for_container_ready(self, container_id, timeout=300):
        """Esperar a que el container esté listo para publicar"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                url = f"{self.base_url}/{container_id}"
                params = {
                    'fields': 'status_code',
                    'access_token': self.access_token
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                status = data.get('status_code')
                
                if status == 'FINISHED':
                    return True
                elif status == 'ERROR':
                    print(f"Error en container: {data}")
                    return False
                
                # Esperar antes de verificar nuevamente
                time.sleep(10)
            
            except Exception as e:
                print(f"Error verificando estado: {e}")
                time.sleep(10)
        
        return False
    
    def _publish_container(self, container_id):
        """Publicar el container creado"""
        try:
            url = f"{self.base_url}/{self.user_id}/media_publish"
            
            params = {
                'creation_id': container_id,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'success': True,
                'media_id': data.get('id'),
                'message': 'Video publicado exitosamente'
            }
        
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Error publicando: {str(e)}'}
    
    def _upload_to_temporary_storage(self, video_path):
        """
        NOTA: Esta función necesita implementación real
        Instagram requiere que el video esté disponible en una URL pública
        
        Opciones:
        1. Usar servicio como AWS S3, Google Cloud Storage
        2. Usar servidor temporal propio
        3. Usar servicio de hosting de archivos
        """
        # Por ahora devuelve None - necesita implementación real
        print("⚠️ Función de almacenamiento temporal no implementada")
        print("   Se necesita servicio de hosting para videos (AWS S3, etc.)")
        return None
    
    def get_account_type(self):
        """Verificar tipo de cuenta Instagram"""
        if not self.is_configured():
            return None
        
        try:
            url = f"{self.base_url}/{self.user_id}"
            params = {
                'fields': 'account_type,username',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            print(f"Error getting account type: {e}")
            return None
    
    def validate_video_for_instagram(self, video_path):
        """Validar si el video cumple los requisitos de Instagram"""
        if not os.path.exists(video_path):
            return False, "Archivo no encontrado"
        
        try:
            # Verificar tamaño
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            if file_size > 100:
                return False, f"Archivo muy grande: {file_size:.1f}MB (máximo 100MB)"
            
            # Verificar extensión
            if not video_path.lower().endswith(('.mp4', '.mov')):
                return False, "Formato no soportado. Usar MP4 o MOV"
            
            return True, "Video válido para Instagram"
        
        except Exception as e:
            return False, f"Error validando video: {str(e)}"
    
    def get_publishing_limits(self):
        """Obtener límites de publicación de Instagram"""
        return {
            'reels_per_day': 'No hay límite oficial, pero se recomienda máximo 1-3 por día',
            'video_duration': '3-90 segundos para Reels',
            'video_size': 'Máximo 100MB',
            'aspect_ratio': '9:16 recomendado para Reels',
            'formats': 'MP4, MOV',
            'account_requirements': 'Cuenta Business o Creator verificada'
        }