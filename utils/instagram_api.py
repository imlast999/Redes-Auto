# -*- coding: utf-8 -*-
"""
API de Instagram completa para Instagram Video Dashboard
Incluye Instagram Graph API e Instagrapi
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import tempfile

class InstagramAPI:
    def __init__(self):
        # Instagram Graph API (oficial)
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.user_id = os.getenv('INSTAGRAM_USER_ID', '')
        self.graph_api_base = 'https://graph.instagram.com'
        
        # Instagrapi (no oficial)
        self.username = os.getenv('INSTAGRAM_USERNAME', '')
        self.password = os.getenv('INSTAGRAM_PASSWORD', '')
        
        # Estado de conexión
        self.graph_api_connected = False
        self.instagrapi_connected = False
        
        # Verificar conexiones
        self._check_connections()
    
    def _check_connections(self):
        """Verificar estado de las conexiones"""
        if self.access_token and self.user_id:
            self.graph_api_connected = self._test_graph_api()
        
        if self.username and self.password:
            self.instagrapi_connected = self._test_instagrapi()
    
    def _test_graph_api(self):
        """Probar conexión con Graph API"""
        try:
            url = f"{self.graph_api_base}/me"
            params = {'access_token': self.access_token}
            response = requests.get(url, params=params, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _test_instagrapi(self):
        """Probar conexión con Instagrapi"""
        try:
            from instagrapi import Client
            cl = Client()
            # Solo probar si las credenciales están configuradas
            return bool(self.username and self.password)
        except ImportError:
            print("⚠️  Instagrapi no está instalado. Instala con: pip install instagrapi")
            return False
        except Exception as e:
            print(f"Error probando Instagrapi: {str(e)}")
            return False
    
    def login_instagrapi(self):
        """Hacer login con Instagrapi"""
        try:
            from instagrapi import Client
            
            cl = Client()
            
            # Configurar el cliente para evitar detección
            cl.delay_range = [1, 3]  # Delay entre requests
            
            # Intentar login
            success = cl.login(self.username, self.password)
            
            if success:
                print(f"✅ Login exitoso con Instagrapi para @{self.username}")
                self.instagrapi_connected = True
                return cl
            else:
                print("❌ Error en login con Instagrapi")
                return None
                
        except ImportError:
            print("❌ Instagrapi no está instalado")
            return None
        except Exception as e:
            print(f"❌ Error en login Instagrapi: {str(e)}")
            return None
    
    def upload_video_instagrapi(self, video_path: str, caption: str = "") -> tuple[bool, str]:
        """Subir video usando Instagrapi (más confiable)"""
        try:
            if not os.path.exists(video_path):
                return False, "Archivo de video no encontrado"
            
            # Login
            cl = self.login_instagrapi()
            if not cl:
                return False, "Error en login de Instagram"
            
            # Subir video
            print(f"📤 Subiendo video: {video_path}")
            
            # Instagrapi detecta automáticamente si es Reel o video normal
            media = cl.video_upload(
                path=video_path,
                caption=caption
            )
            
            if media:
                print(f"✅ Video subido exitosamente! ID: {media.pk}")
                return True, f"Video publicado exitosamente. ID: {media.pk}"
            else:
                return False, "Error subiendo video"
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error subiendo video: {error_msg}")
            
            # Mensajes de error más específicos
            if "challenge_required" in error_msg.lower():
                return False, "Instagram requiere verificación. Inicia sesión manualmente en la app."
            elif "login_required" in error_msg.lower():
                return False, "Credenciales incorrectas o cuenta bloqueada temporalmente."
            elif "spam" in error_msg.lower():
                return False, "Instagram detectó actividad sospechosa. Espera unas horas."
            else:
                return False, f"Error: {error_msg}"
    
    def upload_reel_instagrapi(self, video_path: str, caption: str = "", cover_path: str = None) -> tuple[bool, str]:
        """Subir Reel usando Instagrapi"""
        try:
            if not os.path.exists(video_path):
                return False, "Archivo de video no encontrado"
            
            cl = self.login_instagrapi()
            if not cl:
                return False, "Error en login de Instagram"
            
            print(f"📤 Subiendo Reel: {video_path}")
            
            # Subir como Reel específicamente
            media = cl.clip_upload(
                path=video_path,
                caption=caption,
                thumbnail=cover_path if cover_path and os.path.exists(cover_path) else None
            )
            
            if media:
                print(f"✅ Reel subido exitosamente! ID: {media.pk}")
                return True, f"Reel publicado exitosamente. ID: {media.pk}"
            else:
                return False, "Error subiendo Reel"
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error subiendo Reel: {error_msg}")
            return False, f"Error: {error_msg}"
    
    def get_account_info_instagrapi(self) -> tuple[bool, dict]:
        """Obtener información de la cuenta con Instagrapi"""
        try:
            if not self.username or not self.password:
                print("❌ Credenciales de Instagram no configuradas")
                return False, {'error': 'Credenciales no configuradas'}
            
            cl = self.login_instagrapi()
            if not cl:
                return False, {'error': 'Error en login de Instagram'}
            
            print(f"📊 Obteniendo información de cuenta para @{self.username}...")
            
            # Obtener info del usuario
            user_info = cl.user_info(cl.user_id)
            
            account_data = {
                'username': user_info.username,
                'full_name': user_info.full_name or 'Sin nombre',
                'followers': self._format_number(user_info.follower_count),
                'following': self._format_number(user_info.following_count),
                'posts': self._format_number(user_info.media_count),
                'biography': user_info.biography or 'Sin biografía',
                'is_verified': user_info.is_verified,
                'is_business': user_info.is_business,
                'profile_pic_url': user_info.profile_pic_url,
                'external_url': user_info.external_url,
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            
            print(f"✅ Información obtenida: {account_data['followers']} seguidores, {account_data['posts']} posts")
            return True, account_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error obteniendo info de cuenta: {error_msg}")
            
            # Proporcionar información específica del error
            if "challenge_required" in error_msg.lower():
                return False, {'error': 'Instagram requiere verificación. Inicia sesión manualmente en la app.'}
            elif "login_required" in error_msg.lower():
                return False, {'error': 'Credenciales incorrectas o cuenta bloqueada.'}
            elif "rate limit" in error_msg.lower():
                return False, {'error': 'Límite de requests alcanzado. Intenta más tarde.'}
            else:
                return False, {'error': f'Error de conexión: {error_msg[:100]}'}
    
    def _format_number(self, number):
        """Formatear números grandes (ej: 1500 -> 1.5K)"""
        try:
            if number >= 1000000:
                return f"{number/1000000:.1f}M"
            elif number >= 1000:
                return f"{number/1000:.1f}K"
            else:
                return str(number)
        except:
            return "N/A"
    
    def get_recent_posts_info(self, limit=5) -> tuple[bool, list]:
        """Obtener información de posts recientes"""
        try:
            cl = self.login_instagrapi()
            if not cl:
                return False, []
            
            print(f"📱 Obteniendo últimos {limit} posts...")
            
            # Obtener posts recientes del usuario
            medias = cl.user_medias(cl.user_id, limit)
            
            posts_info = []
            for media in medias:
                post_data = {
                    'id': media.pk,
                    'caption': media.caption_text[:100] + '...' if media.caption_text and len(media.caption_text) > 100 else media.caption_text or 'Sin descripción',
                    'like_count': self._format_number(media.like_count),
                    'comment_count': self._format_number(media.comment_count),
                    'taken_at': media.taken_at.strftime('%d/%m/%Y'),
                    'media_type': 'Video' if media.media_type == 2 else 'Imagen',
                    'url': f"https://instagram.com/p/{media.code}"
                }
                posts_info.append(post_data)
            
            print(f"✅ Información de {len(posts_info)} posts obtenida")
            return True, posts_info
            
        except Exception as e:
            print(f"❌ Error obteniendo posts recientes: {str(e)}")
            return False, []
    
    def schedule_post_instagrapi(self, video_path: str, caption: str, schedule_time: datetime) -> tuple[bool, str]:
        """Programar publicación (simulado - Instagrapi no soporta programación nativa)"""
        # Nota: Instagram no permite programación directa via API no oficial
        # Esto sería para implementar un sistema de cola interno
        
        try:
            # Guardar en cola de programación
            scheduled_post = {
                'video_path': video_path,
                'caption': caption,
                'schedule_time': schedule_time.isoformat(),
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            
            # Aquí guardarías en base de datos o archivo
            print(f"📅 Post programado para: {schedule_time}")
            
            return True, f"Post programado para {schedule_time.strftime('%d/%m/%Y %H:%M')}"
            
        except Exception as e:
            return False, f"Error programando post: {str(e)}"
        """Probar conexión con Instagrapi"""
        try:
            # Intentar importar instagrapi
            from instagrapi import Client
            return True
        except ImportError:
            return False
    
    def is_configured(self):
        """Verificar si al menos una API está configurada"""
        return self.graph_api_connected or self.instagrapi_connected
    
    def get_account_info(self):
        """Obtener información de la cuenta"""
        if self.graph_api_connected:
            return self._get_account_info_graph_api()
        elif self.instagrapi_connected:
            return self._get_account_info_instagrapi()
        else:
            return None
    
    def _get_account_info_graph_api(self):
        """Obtener información usando Graph API"""
        try:
            url = f"{self.graph_api_base}/{self.user_id}"
            params = {
                'fields': 'id,username,account_type,media_count,followers_count',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error getting account info from Graph API: {str(e)}")
            return None
    
    def _get_account_info_instagrapi(self):
        """Obtener información usando Instagrapi"""
        try:
            from instagrapi import Client
            
            cl = Client()
            cl.login(self.username, self.password)
            
            user_info = cl.user_info_by_username(self.username)
            
            return {
                'id': str(user_info.pk),
                'username': user_info.username,
                'account_type': 'PERSONAL',  # Instagrapi no distingue tipos
                'media_count': user_info.media_count,
                'followers_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'biography': user_info.biography
            }
        
        except Exception as e:
            print(f"Error getting account info from Instagrapi: {str(e)}")
            return None
    
    def get_recent_media(self, limit=10):
        """Obtener medios recientes"""
        if self.graph_api_connected:
            return self._get_recent_media_graph_api(limit)
        elif self.instagrapi_connected:
            return self._get_recent_media_instagrapi(limit)
        else:
            return []
    
    def _get_recent_media_graph_api(self, limit):
        """Obtener medios recientes usando Graph API"""
        try:
            url = f"{self.graph_api_base}/{self.user_id}/media"
            params = {
                'fields': 'id,media_type,media_url,thumbnail_url,caption,timestamp,like_count,comments_count',
                'limit': limit,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                return []
        
        except Exception as e:
            print(f"Error getting recent media from Graph API: {str(e)}")
            return []
    
    def _get_recent_media_instagrapi(self, limit):
        """Obtener medios recientes usando Instagrapi"""
        try:
            from instagrapi import Client
            
            cl = Client()
            cl.login(self.username, self.password)
            
            user_id = cl.user_id_from_username(self.username)
            medias = cl.user_medias(user_id, limit)
            
            result = []
            for media in medias:
                result.append({
                    'id': str(media.pk),
                    'media_type': 'VIDEO' if media.media_type == 2 else 'IMAGE',
                    'media_url': media.video_url if media.video_url else media.thumbnail_url,
                    'thumbnail_url': media.thumbnail_url,
                    'caption': media.caption_text,
                    'timestamp': media.taken_at.isoformat(),
                    'like_count': media.like_count,
                    'comments_count': media.comment_count
                })
            
            return result
        
        except Exception as e:
            print(f"Error getting recent media from Instagrapi: {str(e)}")
            return []
    
    def get_insights(self, media_id=None):
        """Obtener insights/estadísticas"""
        if not self.graph_api_connected:
            return None
        
        try:
            if media_id:
                # Insights de un medio específico
                url = f"{self.graph_api_base}/{media_id}/insights"
                params = {
                    'metric': 'impressions,reach,likes,comments,shares,saves',
                    'access_token': self.access_token
                }
            else:
                # Insights de la cuenta
                url = f"{self.graph_api_base}/{self.user_id}/insights"
                params = {
                    'metric': 'impressions,reach,profile_views',
                    'period': 'day',
                    'since': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                    'until': datetime.now().strftime('%Y-%m-%d'),
                    'access_token': self.access_token
                }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error getting insights: {str(e)}")
            return None
    
    def search_hashtags(self, hashtag):
        """Buscar información de hashtags"""
        if not self.graph_api_connected:
            return None
        
        try:
            url = f"{self.graph_api_base}/ig_hashtag_search"
            params = {
                'user_id': self.user_id,
                'q': hashtag,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error searching hashtags: {str(e)}")
            return None
    
    def get_hashtag_media(self, hashtag_id, limit=10):
        """Obtener medios de un hashtag"""
        if not self.graph_api_connected:
            return []
        
        try:
            url = f"{self.graph_api_base}/{hashtag_id}/recent_media"
            params = {
                'user_id': self.user_id,
                'fields': 'id,media_type,media_url,caption,timestamp,like_count,comments_count',
                'limit': limit,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                return []
        
        except Exception as e:
            print(f"Error getting hashtag media: {str(e)}")
            return []
    
    def get_api_status(self):
        """Obtener estado de las APIs"""
        return {
            'graph_api': {
                'configured': bool(self.access_token and self.user_id),
                'connected': self.graph_api_connected,
                'type': 'Oficial'
            },
            'instagrapi': {
                'configured': bool(self.username and self.password),
                'connected': self.instagrapi_connected,
                'type': 'No oficial'
            }
        }
    
    def get_publishing_limits(self):
        """Obtener límites de publicación de Instagram"""
        return {
            'video_duration_max': '60 segundos (Reels)',
            'video_size_max': '100 MB',
            'image_size_max': '8 MB',
            'caption_length_max': '2,200 caracteres',
            'hashtags_max': '30 por post',
            'posts_per_day_recommended': '1-2 posts',
            'stories_per_day_max': 'Sin límite oficial',
            'aspect_ratios_supported': '1.91:1 a 4:5',
            'video_formats_supported': 'MP4, MOV',
            'image_formats_supported': 'JPG, PNG'
        }
    
    def validate_media_for_instagram(self, file_path):
        """Validar si un archivo cumple con los requisitos de Instagram"""
        if not os.path.exists(file_path):
            return False, "Archivo no encontrado"
        
        # Obtener información del archivo
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Validar extensión
        video_exts = ['.mp4', '.mov']
        image_exts = ['.jpg', '.jpeg', '.png']
        
        if file_ext in video_exts:
            # Validar video
            if file_size > 100:
                return False, f"Video muy grande: {file_size:.1f}MB (máximo 100MB)"
            
            # Aquí podrías agregar más validaciones usando FFprobe
            return True, "Video válido"
        
        elif file_ext in image_exts:
            # Validar imagen
            if file_size > 8:
                return False, f"Imagen muy grande: {file_size:.1f}MB (máximo 8MB)"
            
            return True, "Imagen válida"
        
        else:
            return False, f"Formato no soportado: {file_ext}"
    
    def get_optimal_posting_times(self):
        """Obtener horarios óptimos de publicación"""
        return {
            'weekdays': {
                'morning': '07:00 - 09:00',
                'lunch': '11:00 - 13:00',
                'evening': '17:00 - 19:00'
            },
            'weekends': {
                'morning': '09:00 - 11:00',
                'afternoon': '14:00 - 16:00'
            },
            'best_days': ['Martes', 'Miércoles', 'Jueves'],
            'avoid_times': ['00:00 - 06:00', '22:00 - 24:00']
        }
    
    def generate_hashtags(self, theme):
        """Generar hashtags relevantes para un tema"""
        hashtag_sets = {
            'luxury': [
                '#luxury', '#lifestyle', '#wealth', '#rich', '#expensive',
                '#millionaire', '#success', '#motivation', '#mindset', '#goals',
                '#entrepreneur', '#business', '#money', '#investment', '#finance'
            ],
            'fitness': [
                '#fitness', '#gym', '#workout', '#health', '#fit',
                '#training', '#muscle', '#bodybuilding', '#cardio', '#strength',
                '#nutrition', '#diet', '#wellness', '#healthy', '#exercise'
            ],
            'travel': [
                '#travel', '#vacation', '#adventure', '#explore', '#wanderlust',
                '#trip', '#journey', '#destination', '#tourism', '#holiday',
                '#backpacking', '#solo', '#nature', '#photography', '#culture'
            ],
            'food': [
                '#food', '#foodie', '#delicious', '#yummy', '#cooking',
                '#recipe', '#chef', '#restaurant', '#homemade', '#tasty',
                '#dinner', '#lunch', '#breakfast', '#healthy', '#organic'
            ]
        }
        
        return hashtag_sets.get(theme, hashtag_sets['luxury'])