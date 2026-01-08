# -*- coding: utf-8 -*-
"""
Sistema de Text-to-Speech LOCAL usando Google TTS
Completamente GRATUITO sin tarjeta de crédito
"""

import os
import requests
import tempfile
from pathlib import Path
import subprocess
import platform

class LocalTTS:
    def __init__(self):
        # Usar carpeta del proyecto para audios generados
        self.audio_dir = Path('generated/audio')
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir = tempfile.mkdtemp()
        self.supported_languages = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文'
        }
        
        # Verificar si gTTS está disponible
        self.gtts_available = self._check_gtts()
        
        # Verificar si espeak está disponible
        self.espeak_available = self._check_espeak()
        
        # Verificar si festival está disponible
        self.festival_available = self._check_festival()
    
    def _check_gtts(self):
        """Verificar si gTTS está disponible"""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            return False
    
    def _check_espeak(self):
        """Verificar si espeak está disponible"""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_festival(self):
        """Verificar si festival está disponible"""
        try:
            result = subprocess.run(['festival', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_available_engines(self):
        """Obtener motores TTS disponibles"""
        engines = []
        
        if self.gtts_available:
            engines.append({
                'name': 'Google TTS (Online)',
                'description': 'Google Text-to-Speech online (gratuito)',
                'quality': 'Alta',
                'languages': '100+ idiomas',
                'limitations': 'Requiere internet'
            })
        
        if self.espeak_available:
            engines.append({
                'name': 'eSpeak (Local)',
                'description': 'Síntesis de voz local (gratuito)',
                'quality': 'Media',
                'languages': '50+ idiomas',
                'limitations': 'Voz robótica'
            })
        
        if self.festival_available:
            engines.append({
                'name': 'Festival (Local)',
                'description': 'Síntesis de voz local (gratuito)',
                'quality': 'Media',
                'languages': '20+ idiomas',
                'limitations': 'Configuración compleja'
            })
        
        return engines
    
    def text_to_speech_gtts(self, text: str, language: str = 'es', output_path: str = None, speed: str = 'normal') -> tuple[bool, str]:
        """Convertir texto a voz usando Google TTS (gratuito)"""
        if not self.gtts_available:
            return False, "gTTS no está instalado. Instala con: pip install gtts"
        
        try:
            from gtts import gTTS
            from datetime import datetime
            import subprocess
            
            # Limpiar texto de emojis y caracteres especiales
            clean_text = self._clean_text_for_tts(text)
            
            # Configurar velocidad (gTTS no tiene velocidad nativa, pero podemos usar slow=False siempre)
            slow_speech = False  # Siempre rápido para mejor fluidez
            
            # Crear objeto gTTS
            tts = gTTS(text=clean_text, lang=language, slow=slow_speech)
            
            # Generar nombre de archivo si no se proporciona
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"audio_{language}_{speed}_{timestamp}.mp3"
                output_path = str(self.audio_dir / filename)
            
            # Guardar archivo de audio temporal
            temp_output = output_path.replace('.mp3', '_temp.mp3')
            tts.save(temp_output)
            
            # Ajustar velocidad usando FFmpeg si está disponible
            if speed != 'normal' and self._check_ffmpeg():
                speed_factor = {
                    'slow': '0.8',
                    'normal': '1.0', 
                    'fast': '1.3',
                    'very_fast': '1.5'
                }.get(speed, '1.0')
                
                cmd = [
                    'ffmpeg', '-i', temp_output, 
                    '-filter:a', f'atempo={speed_factor}',
                    '-y', output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Eliminar archivo temporal
                    os.remove(temp_output)
                else:
                    # Si falla FFmpeg, usar el archivo original
                    os.rename(temp_output, output_path)
            else:
                # Sin FFmpeg, usar archivo original
                os.rename(temp_output, output_path)
            
            return True, output_path
        
        except Exception as e:
            return False, f"Error con Google TTS: {str(e)}"
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Limpiar texto para TTS removiendo emojis y caracteres problemáticos"""
        import re
        
        # Remover emojis
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                 u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 "]+", flags=re.UNICODE)
        
        clean_text = emoji_pattern.sub('', text)
        
        # Reemplazar algunos símbolos comunes con palabras
        replacements = {
            '💎': 'diamante',
            '🔥': '',
            '✨': '',
            '💰': 'dinero',
            '🚀': '',
            '⚡': '',
            '🏆': '',
            '💪': '',
            '🎯': '',
            '📈': '',
            '₿': 'Bitcoin',
            '@': 'arroba ',
            '#': 'hashtag ',
            '&': ' y ',
            '%': ' por ciento',
            '$': ' dólares'
        }
        
        for symbol, replacement in replacements.items():
            clean_text = clean_text.replace(symbol, replacement)
        
        # Limpiar espacios múltiples
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _check_ffmpeg(self):
        """Verificar si FFmpeg está disponible"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_available_voices(self, language: str = 'es') -> dict:
        """Obtener voces disponibles para un idioma"""
        # Verificar si ElevenLabs está configurado
        if self._check_elevenlabs():
            return self._get_elevenlabs_voices(language)
        
        # Fallback: gTTS con diferentes configuraciones
        voices = {
            'es': {
                'standard': {'name': 'Voz Estándar', 'speed': 'normal', 'provider': 'gtts'},
                'fast': {'name': 'Voz Rápida', 'speed': 'fast', 'provider': 'gtts'},
                'slow': {'name': 'Voz Pausada', 'speed': 'slow', 'provider': 'gtts'},
                'energetic': {'name': 'Voz Energética', 'speed': 'very_fast', 'provider': 'gtts'}
            },
            'en': {
                'standard': {'name': 'Standard Voice', 'speed': 'normal', 'provider': 'gtts'},
                'fast': {'name': 'Fast Voice', 'speed': 'fast', 'provider': 'gtts'},
                'slow': {'name': 'Slow Voice', 'speed': 'slow', 'provider': 'gtts'},
                'energetic': {'name': 'Energetic Voice', 'speed': 'very_fast', 'provider': 'gtts'}
            }
        }
        
        return voices.get(language, voices['es'])
    
    def _check_elevenlabs(self) -> bool:
        """Verificar si ElevenLabs está configurado"""
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY', '')
        return bool(elevenlabs_api_key)
    
    def _get_elevenlabs_voices(self, language: str = 'es') -> dict:
        """Obtener voces de ElevenLabs (cuando esté configurado)"""
        try:
            # Aquí iría la integración real con ElevenLabs
            # Por ahora devolvemos voces simuladas
            elevenlabs_voices = {
                'es': {
                    'rachel': {'name': 'Rachel (Premium)', 'provider': 'elevenlabs', 'voice_id': 'rachel_es'},
                    'adam': {'name': 'Adam (Premium)', 'provider': 'elevenlabs', 'voice_id': 'adam_es'},
                    'bella': {'name': 'Bella (Premium)', 'provider': 'elevenlabs', 'voice_id': 'bella_es'},
                    'antoni': {'name': 'Antoni (Premium)', 'provider': 'elevenlabs', 'voice_id': 'antoni_es'},
                    'elli': {'name': 'Elli (Premium)', 'provider': 'elevenlabs', 'voice_id': 'elli_es'}
                },
                'en': {
                    'rachel': {'name': 'Rachel (Premium)', 'provider': 'elevenlabs', 'voice_id': 'rachel_en'},
                    'adam': {'name': 'Adam (Premium)', 'provider': 'elevenlabs', 'voice_id': 'adam_en'},
                    'bella': {'name': 'Bella (Premium)', 'provider': 'elevenlabs', 'voice_id': 'bella_en'},
                    'antoni': {'name': 'Antoni (Premium)', 'provider': 'elevenlabs', 'voice_id': 'antoni_en'},
                    'elli': {'name': 'Elli (Premium)', 'provider': 'elevenlabs', 'voice_id': 'elli_en'}
                }
            }
            
            return elevenlabs_voices.get(language, elevenlabs_voices['es'])
        
        except Exception as e:
            print(f"Error obteniendo voces de ElevenLabs: {e}")
            return self.get_available_voices(language)  # Fallback a gTTS
    
    def text_to_speech_elevenlabs(self, text: str, voice_id: str, output_path: str = None) -> tuple[bool, str]:
        """Convertir texto a voz usando ElevenLabs (cuando esté configurado)"""
        if not self._check_elevenlabs():
            return False, "ElevenLabs no está configurado"
        
        try:
            # CÓDIGO PREPARADO PARA ELEVENLABS
            # Descomenta y configura cuando tengas la API key
            
            """
            import requests
            
            elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
            
            # Limpiar texto
            clean_text = self._clean_text_for_tts(text)
            
            # URL de la API de ElevenLabs
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": elevenlabs_api_key
            }
            
            data = {
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                # Generar nombre de archivo si no se proporciona
                if not output_path:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"elevenlabs_{voice_id}_{timestamp}.mp3"
                    output_path = str(self.audio_dir / filename)
                
                # Guardar audio
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                return True, output_path
            else:
                return False, f"Error ElevenLabs: {response.status_code} - {response.text}"
            """
            
            # Por ahora, usar gTTS como fallback
            return self.text_to_speech_gtts(text, 'es', output_path, 'fast')
        
        except Exception as e:
            return False, f"Error con ElevenLabs: {str(e)}"
    
    def text_to_speech_with_voice(self, text: str, language: str = 'es', voice: str = 'standard', output_path: str = None) -> tuple[bool, str]:
        """Convertir texto a voz con voz específica"""
        voices = self.get_available_voices(language)
        voice_config = voices.get(voice, voices['standard'])
        speed = voice_config['speed']
        
        return self.text_to_speech_gtts(text, language, output_path, speed)
    
    def text_to_speech_espeak(self, text: str, language: str = 'es', output_path: str = None) -> tuple[bool, str]:
        """Convertir texto a voz usando eSpeak (local)"""
        if not self.espeak_available:
            return False, "eSpeak no está instalado"
        
        try:
            # Mapear idiomas
            lang_map = {
                'es': 'es',
                'en': 'en',
                'fr': 'fr',
                'de': 'de',
                'it': 'it',
                'pt': 'pt',
                'ru': 'ru',
                'ja': 'ja',
                'ko': 'ko',
                'zh': 'zh'
            }
            
            espeak_lang = lang_map.get(language, 'en')
            
            # Generar nombre de archivo si no se proporciona
            if not output_path:
                output_path = os.path.join(self.temp_dir, f"espeak_{hash(text) % 10000}.wav")
            
            # Comando espeak
            cmd = [
                'espeak',
                '-v', espeak_lang,
                '-s', '150',  # Velocidad
                '-w', output_path,
                text
            ]
            
            # Ejecutar comando
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, output_path
            else:
                return False, f"Error ejecutando espeak: {result.stderr}"
        
        except Exception as e:
            return False, f"Error con eSpeak: {str(e)}"
    
    def text_to_speech_festival(self, text: str, language: str = 'es', output_path: str = None) -> tuple[bool, str]:
        """Convertir texto a voz usando Festival (local)"""
        if not self.festival_available:
            return False, "Festival no está instalado"
        
        try:
            # Generar nombre de archivo si no se proporciona
            if not output_path:
                output_path = os.path.join(self.temp_dir, f"festival_{hash(text) % 10000}.wav")
            
            # Crear script de Festival
            festival_script = f"""
            (set! utt1 (Utterance Text "{text}"))
            (utt.synth utt1)
            (utt.save.wave utt1 "{output_path}")
            """
            
            # Ejecutar Festival
            result = subprocess.run(['festival', '--pipe'], 
                                  input=festival_script, text=True, 
                                  capture_output=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, output_path
            else:
                return False, f"Error ejecutando Festival: {result.stderr}"
        
        except Exception as e:
            return False, f"Error con Festival: {str(e)}"
    
    def text_to_speech_auto(self, text: str, language: str = 'es', output_path: str = None) -> tuple[bool, str]:
        """Convertir texto a voz usando el mejor motor disponible"""
        # Prioridad: Google TTS > eSpeak > Festival
        
        if self.gtts_available:
            success, result = self.text_to_speech_gtts(text, language, output_path)
            if success:
                return True, f"Google TTS: {result}"
        
        if self.espeak_available:
            success, result = self.text_to_speech_espeak(text, language, output_path)
            if success:
                return True, f"eSpeak: {result}"
        
        if self.festival_available:
            success, result = self.text_to_speech_festival(text, language, output_path)
            if success:
                return True, f"Festival: {result}"
        
        return False, "No hay motores TTS disponibles"
    
    def get_voice_preview(self, text: str = "Hola, este es un ejemplo de síntesis de voz", 
                         language: str = 'es') -> tuple[bool, str]:
        """Generar preview de voz"""
        return self.text_to_speech_auto(text, language)
    
    def install_dependencies(self) -> tuple[bool, str]:
        """Instalar dependencias necesarias"""
        commands = []
        
        if not self.gtts_available:
            commands.append("pip install gtts")
        
        if platform.system() == "Windows":
            if not self.espeak_available:
                commands.append("Instalar eSpeak desde: https://espeak.sourceforge.net/download.html")
        else:
            if not self.espeak_available:
                commands.append("sudo apt-get install espeak espeak-data")
            
            if not self.festival_available:
                commands.append("sudo apt-get install festival")
        
        if commands:
            return False, "Comandos para instalar dependencias:\n" + "\n".join(commands)
        else:
            return True, "Todas las dependencias están instaladas"
    
    def get_supported_languages(self):
        """Obtener idiomas soportados"""
        return self.supported_languages
    
    def cleanup_temp_files(self):
        """Limpiar archivos temporales"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error limpiando archivos temporales: {e}")
    
    def get_engine_status(self):
        """Obtener estado de todos los motores"""
        return {
            'gtts': {
                'available': self.gtts_available,
                'name': 'Google TTS',
                'type': 'Online',
                'quality': 'Alta'
            },
            'espeak': {
                'available': self.espeak_available,
                'name': 'eSpeak',
                'type': 'Local',
                'quality': 'Media'
            },
            'festival': {
                'available': self.festival_available,
                'name': 'Festival',
                'type': 'Local',
                'quality': 'Media'
            }
        }
# Crear instancia global
local_tts = LocalTTS()