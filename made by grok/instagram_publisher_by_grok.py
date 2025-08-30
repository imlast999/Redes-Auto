import requests
import json
import os
import time
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

class InstagramPublisher:
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.user_id = os.getenv('INSTAGRAM_USER_ID', '')
        self.base_url = "https://graph.facebook.com/v18.0"
        self.config_file = "config/instagram_publisher.json"
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', ''),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', '')
        )
        self.s3_bucket = os.getenv('AWS_S3_BUCKET', 'your-bucket-name')
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.access_token = config.get('access_token', self.access_token)
                    self.user_id = config.get('user_id', self.user_id)
        except Exception as e:
            print(f"Error loading publisher config: {str(e)}")
    
    def configure(self, access_token, user_id):
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
        return bool(self.access_token and self.user_id)
    
    def upload_video_to_instagram(self, video_path, caption=""):
        if not self.is_configured():
            return False, "Instagram API no está configurado"
        if not os.path.exists(video_path):
            return False, "Archivo de video no encontrado"
        try:
            container_response = self._create_video_container(video_path, caption)
            if not container_response['success']:
                return False, container_response['message']
            container_id = container_response['container_id']
            status_ok = self._wait_for_container_ready(container_id)
            if not status_ok:
                return False, "Error en procesamiento del video"
            publish_response = self._publish_container(container_id)
            if publish_response['success']:
                return True, f"Video publicado exitosamente. ID: {publish_response['media_id']}"
            else:
                return False, publish_response['message']
        except Exception as e:
            return False, f"Error al publicar: {str(e)}"
    
    def _create_video_container(self, video_path, caption):
        try:
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
                time.sleep(10)
            except Exception as e:
                print(f"Error verificando estado: {e}")
                time.sleep(10)
        return False
    
    def _publish_container(self, container_id):
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
        try:
            filename = os.path.basename(video_path)
            s3_key = f"temp_videos/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            self.s3_client.upload_file(
                video_path,
                self.s3_bucket,
                s3_key,
                ExtraArgs={'ACL': 'public-read', 'ContentType': 'video/mp4'}
            )
            video_url = f"https://{self.s3_bucket}.s3.amazonaws.com/{s3_key}"
            return video_url
        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            return None
    
    def get_account_type(self):
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
        if not os.path.exists(video_path):
            return False, "Archivo no encontrado"
        try:
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            if file_size > 100:
                return False, f"Archivo muy grande: {file_size:.1f}MB (máximo 100MB)"
            if not video_path.lower().endswith(('.mp4', '.mov')):
                return False, "Formato no soportado. Usar MP4 o MOV"
            return True