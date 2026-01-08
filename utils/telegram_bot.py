# -*- coding: utf-8 -*-
"""
Sistema completo de notificaciones de Telegram para Instagram Video Dashboard
"""

import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, List

class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.config_file = "config/telegram_config.json"
        
        # Cargar configuración guardada
        self.load_config()
    
    def load_config(self):
        """Cargar configuración del bot"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.bot_token = config.get('bot_token', self.bot_token)
                    self.chat_id = config.get('chat_id', self.chat_id)
        except Exception as e:
            print(f"Error loading Telegram config: {str(e)}")
    
    def configure(self, bot_token: str, chat_id: str):
        """Configurar bot de Telegram"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            config = {
                'bot_token': bot_token,
                'chat_id': chat_id,
                'configured_at': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving Telegram config: {str(e)}")
            return False
    
    def is_configured(self) -> bool:
        """Verificar si el bot está configurado"""
        return bool(self.bot_token and self.chat_id)
    
    def test_connection(self) -> tuple[bool, str]:
        """Probar conexión con Telegram"""
        if not self.is_configured():
            return False, "Bot no configurado"
        
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    return True, f"Bot conectado: @{bot_info['result']['username']}"
                else:
                    return False, "Error en respuesta de Telegram"
            else:
                return False, f"Error HTTP: {response.status_code}"
        
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> tuple[bool, str]:
        """Enviar mensaje de texto"""
        if not self.is_configured():
            return False, "Bot no configurado"
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return True, "Mensaje enviado exitosamente"
                else:
                    return False, f"Error de Telegram: {result.get('description', 'Error desconocido')}"
            else:
                return False, f"Error HTTP: {response.status_code}"
        
        except Exception as e:
            return False, f"Error enviando mensaje: {str(e)}"
    
    def _send_file(self, file_path: str, file_type: str, caption: str = "", timeout: int = 30) -> tuple[bool, str]:
        """Método genérico para enviar archivos"""
        if not self.is_configured():
            return False, "Bot no configurado"
        if not os.path.exists(file_path):
            return False, f"Archivo no encontrado"
        
        try:
            url = f"{self.base_url}/send{file_type.capitalize()}"
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url, files={file_type: f}, 
                    data={'chat_id': self.chat_id, 'caption': caption}, timeout=timeout
                )
            
            if response.status_code == 200 and response.json().get('ok'):
                return True, f"{file_type.capitalize()} enviado exitosamente"
            return False, f"Error: {response.json().get('description', response.status_code)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def send_photo(self, photo_path: str, caption: str = "") -> tuple[bool, str]:
        """Enviar foto"""
        return self._send_file(photo_path, 'photo', caption, 30)
    
    def send_video(self, video_path: str, caption: str = "") -> tuple[bool, str]:
        """Enviar video"""
        return self._send_file(video_path, 'video', caption, 60)
    
    def send_document(self, document_path: str, caption: str = "") -> tuple[bool, str]:
        """Enviar documento"""
        return self._send_file(document_path, 'document', caption, 60)
    
    # NOTIFICACIONES ESPECÍFICAS DEL DASHBOARD
    
    def notify_video_processed(self, video_name: str, output_path: str) -> tuple[bool, str]:
        """Notificar que un video fue procesado"""
        message = f"""
🎬 <b>Video Procesado Exitosamente</b>

📁 <b>Archivo:</b> {video_name}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
✅ <b>Estado:</b> Listo para publicar

<i>El video ha sido procesado y está listo para ser publicado en Instagram.</i>
        """
        
        return self.send_message(message.strip())
    
    def notify_video_published(self, video_name: str, instagram_url: str = "") -> tuple[bool, str]:
        """Notificar que un video fue publicado"""
        message = f"""
📤 <b>Video Publicado en Instagram</b>

📁 <b>Archivo:</b> {video_name}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
✅ <b>Estado:</b> Publicado exitosamente

<i>El video ha sido publicado en tu cuenta de Instagram.</i>
        """
        
        if instagram_url:
            message += f"\n🔗 <b>Enlace:</b> {instagram_url}"
        
        return self.send_message(message.strip())
    
    def notify_ai_video_generated(self, theme: str, script_path: str) -> tuple[bool, str]:
        """Notificar que se generó un video con IA"""
        message = f"""
🤖 <b>Video de IA Generado</b>

🎯 <b>Tema:</b> {theme}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
✅ <b>Estado:</b> Generado exitosamente

<i>Se ha generado un nuevo video con IA listo para procesar.</i>
        """
        
        return self.send_message(message.strip())
    
    def notify_scheduler_status(self, status: str, next_posts: List[str]) -> tuple[bool, str]:
        """Notificar estado del programador automático"""
        if status == "started":
            message = f"""
🤖 <b>Bot Automático Iniciado</b>

⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
✅ <b>Estado:</b> Activo y funcionando

<b>Próximas publicaciones:</b>
"""
            for i, post in enumerate(next_posts[:3], 1):
                message += f"{i}. {post}\n"
            
            message += "\n<i>El bot automático está programando publicaciones.</i>"
        
        elif status == "stopped":
            message = f"""
⏸️ <b>Bot Automático Pausado</b>

⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
⏸️ <b>Estado:</b> Pausado

<i>El bot automático ha sido pausado.</i>
            """
        
        else:
            message = f"""
📊 <b>Estado del Bot Automático</b>

⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
📊 <b>Estado:</b> {status}

<i>Información del programador automático.</i>
            """
        
        return self.send_message(message.strip())
    
    def notify_error(self, error_type: str, error_message: str, video_name: str = "") -> tuple[bool, str]:
        """Notificar errores"""
        message = f"""
🚨 <b>Error en el Dashboard</b>

❌ <b>Tipo:</b> {error_type}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}
        """
        
        if video_name:
            message += f"\n📁 <b>Archivo:</b> {video_name}"
        
        message += f"\n\n<b>Detalles:</b>\n<code>{error_message}</code>"
        
        return self.send_message(message.strip())
    
    def notify_daily_summary(self, stats: Dict) -> tuple[bool, str]:
        """Notificar resumen diario"""
        message = f"""
📊 <b>Resumen Diario - {datetime.now().strftime('%d/%m/%Y')}</b>

📹 <b>Videos procesados:</b> {stats.get('processed', 0)}
📤 <b>Videos publicados:</b> {stats.get('published', 0)}
⏳ <b>Videos pendientes:</b> {stats.get('pending', 0)}
🤖 <b>Videos de IA generados:</b> {stats.get('ai_generated', 0)}

<i>Resumen de actividad del día.</i>
        """
        
        return self.send_message(message.strip())
    
    def send_help_message(self) -> tuple[bool, str]:
        """Enviar mensaje de ayuda"""
        message = """
🤖 <b>Instagram Video Dashboard Bot</b>

<b>Comandos disponibles:</b>
/start - Iniciar el bot
/status - Estado del dashboard
/help - Mostrar esta ayuda
/stats - Estadísticas del día
/test - Probar conexión

<b>Notificaciones automáticas:</b>
• Videos procesados
• Publicaciones exitosas
• Errores del sistema
• Resumen diario
• Estado del bot automático

<i>Este bot te mantiene informado sobre todas las actividades de tu dashboard de Instagram.</i>
        """
        
        return self.send_message(message.strip())
    
    def get_bot_info(self) -> Dict:
        """Obtener información del bot"""
        if not self.is_configured():
            return {"error": "Bot no configurado"}
        
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error HTTP: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}
    
    def get_chat_info(self) -> Dict:
        """Obtener información del chat"""
        if not self.is_configured():
            return {"error": "Bot no configurado"}
        
        try:
            url = f"{self.base_url}/getChat"
            data = {'chat_id': self.chat_id}
            response = requests.get(url, data=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Error HTTP: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"Error de conexión: {str(e)}"}
