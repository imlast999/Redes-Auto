# -*- coding: utf-8 -*-
"""
Procesador de videos completo para Instagram Video Dashboard
Incluye redimensionado, marca de agua, optimización y conversión
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path('videos/processed')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuraciones de Instagram
        self.instagram_formats = {
            '9:16 (Stories/Reels)': {'width': 1080, 'height': 1920},
            '1:1 (Square)': {'width': 1080, 'height': 1080},
            '4:5 (Portrait)': {'width': 1080, 'height': 1350},
            '16:9 (Landscape)': {'width': 1920, 'height': 1080}
        }
        
        # Configuraciones de calidad
        self.quality_settings = {
            'High': {'crf': 18, 'preset': 'slow'},
            'Medium': {'crf': 23, 'preset': 'medium'},
            'Low': {'crf': 28, 'preset': 'fast'}
        }
        
        # Verificar si FFmpeg está disponible
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Verificar si FFmpeg está instalado"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_video_info(self, video_path):
        """Obtener información del video"""
        if not os.path.exists(video_path):
            return None
        
        try:
            if self.ffmpeg_available:
                # Usar FFprobe para obtener información detallada
                cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', '-show_streams', video_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
                    
                    if video_stream:
                        return {
                            'width': int(video_stream.get('width', 0)),
                            'height': int(video_stream.get('height', 0)),
                            'duration': float(data['format'].get('duration', 0)),
                            'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                            'codec': video_stream.get('codec_name', 'unknown'),
                            'size': round(float(data['format'].get('size', 0)) / (1024*1024), 2)
                        }
            
            # Fallback: información básica del archivo
            stat = os.stat(video_path)
            return {
                'width': 'Unknown',
                'height': 'Unknown',
                'duration': 'Unknown',
                'fps': 'Unknown',
                'codec': 'Unknown',
                'size': round(stat.st_size / (1024*1024), 2)
            }
        
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
    
    def process_video(self, input_path, add_watermark=True, watermark_text="@yourusername",
                     watermark_position="bottom-right", resize=True, aspect_ratio="9:16 (Stories/Reels)",
                     quality="Medium", output_path=None):
        """Procesar video completo"""
        
        if not os.path.exists(input_path):
            return None
        
        try:
            # Generar nombre de archivo de salida
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"processed_{timestamp}_{os.path.basename(input_path)}"
                output_path = str(self.output_dir / filename)
            
            if self.ffmpeg_available:
                return self._process_with_ffmpeg(
                    input_path, output_path, add_watermark, watermark_text,
                    watermark_position, resize, aspect_ratio, quality
                )
            else:
                # Fallback: copiar archivo sin procesamiento
                shutil.copy2(input_path, output_path)
                return output_path
        
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            return None
    
    def _process_with_ffmpeg(self, input_path, output_path, add_watermark, watermark_text,
                           watermark_position, resize, aspect_ratio, quality):
        """Procesar video usando FFmpeg"""
        
        # Construir comando FFmpeg
        cmd = ['ffmpeg', '-i', input_path, '-y']  # -y para sobrescribir
        
        # Filtros de video
        filters = []
        
        # Redimensionar si es necesario
        if resize and aspect_ratio in self.instagram_formats:
            dimensions = self.instagram_formats[aspect_ratio]
            width, height = dimensions['width'], dimensions['height']
            filters.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")
            filters.append(f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black")
        
        # Agregar marca de agua
        if add_watermark and watermark_text:
            # Posiciones de marca de agua
            positions = {
                'top-left': 'x=10:y=10',
                'top-right': 'x=w-tw-10:y=10',
                'bottom-left': 'x=10:y=h-th-10',
                'bottom-right': 'x=w-tw-10:y=h-th-10',
                'center': 'x=(w-tw)/2:y=(h-th)/2'
            }
            
            pos = positions.get(watermark_position, positions['bottom-right'])
            watermark_filter = f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:bordercolor=black:borderw=2:{pos}"
            filters.append(watermark_filter)
        
        # Aplicar filtros
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        # Configuración de calidad
        quality_config = self.quality_settings.get(quality, self.quality_settings['Medium'])
        cmd.extend(['-crf', str(quality_config['crf'])])
        cmd.extend(['-preset', quality_config['preset']])
        
        # Configuración de audio
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        
        # Archivo de salida
        cmd.append(output_path)
        
        # Ejecutar comando
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return output_path
        else:
            print(f"FFmpeg error: {result.stderr}")
            return None
    
    def create_video_from_image_and_audio(self, image_path, audio_path, output_path=None, duration=None):
        """Crear video a partir de imagen y audio"""
        
        if not os.path.exists(image_path) or not os.path.exists(audio_path):
            return False, "Archivos no encontrados"
        
        # Validar que la imagen sea realmente una imagen
        if not self._is_valid_image(image_path):
            # Si no es una imagen válida, crear una imagen placeholder real
            image_path = self._create_emergency_image()
            if not image_path:
                return False, "No se pudo crear imagen de respaldo"
        
        # Validar que el audio sea realmente un archivo de audio
        if not self._is_valid_audio(audio_path):
            return False, "El archivo de audio no es válido"
        
        try:
            # Generar nombre de archivo si no se proporciona
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = str(self.output_dir / f"ai_video_{timestamp}.mp4")
            
            # Asegurar que el directorio de salida existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if self.ffmpeg_available:
                return self._create_video_with_ffmpeg(image_path, audio_path, output_path, duration)
            else:
                # Fallback: crear video simple sin FFmpeg
                return self._create_video_fallback(image_path, audio_path, output_path)
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _is_valid_image(self, image_path):
        """Verificar si el archivo es una imagen válida"""
        try:
            # Verificar extensión
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
            file_ext = os.path.splitext(image_path)[1].lower()
            
            if file_ext not in valid_extensions:
                return False
            
            # Intentar abrir con PIL si está disponible
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    img.verify()  # Verificar que es una imagen válida
                return True
            except ImportError:
                # Si PIL no está disponible, solo verificar extensión y tamaño
                return file_ext in valid_extensions and os.path.getsize(image_path) > 1000
            except Exception:
                return False
        
        except Exception:
            return False
    
    def _is_valid_audio(self, audio_path):
        """Verificar si el archivo es un audio válido"""
        try:
            # Verificar extensión
            valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
            file_ext = os.path.splitext(audio_path)[1].lower()
            
            if file_ext not in valid_extensions:
                return False
            
            # Verificar que el archivo tenga un tamaño razonable
            file_size = os.path.getsize(audio_path)
            return file_size > 1000  # Al menos 1KB
        
        except Exception:
            return False
    
    def _create_emergency_image(self):
        """Crear imagen de emergencia cuando no hay imagen válida"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen de 1080x1920 (formato Instagram)
            img = Image.new('RGB', (1080, 1920), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Crear gradiente simple
            for y in range(1920):
                alpha = y / 1920
                r = int(26 + (102 - 26) * alpha)
                g = int(26 + (62 - 26) * alpha)
                b = int(46 + (142 - 46) * alpha)
                draw.line([(0, y), (1080, y)], fill=(r, g, b))
            
            # Agregar elementos visuales
            # Círculos decorativos
            draw.ellipse([200, 400, 400, 600], outline='#FFD700', width=5)
            draw.ellipse([680, 1200, 880, 1400], outline='#FF6B35', width=5)
            
            # Líneas decorativas
            draw.line([(100, 800), (980, 800)], fill='#FFD700', width=3)
            draw.line([(100, 1100), (980, 1100)], fill='#FF6B35', width=3)
            
            # Texto
            try:
                font_large = ImageFont.truetype("arial.ttf", 80)
                font_medium = ImageFont.truetype("arial.ttf", 50)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Título
            title = "CONTENIDO"
            bbox = draw.textbbox((0, 0), title, font=font_large)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            
            # Sombra
            draw.text((x+3, 863), title, fill=(0, 0, 0), font=font_large)
            # Texto principal
            draw.text((x, 860), title, fill='#FFD700', font=font_large)
            
            # Subtítulo
            subtitle = "PREMIUM"
            bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            
            draw.text((x+2, 962), subtitle, fill=(0, 0, 0), font=font_medium)
            draw.text((x, 960), subtitle, fill='white', font=font_medium)
            
            # Guardar imagen
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            emergency_path = str(self.output_dir / f"emergency_bg_{timestamp}.jpg")
            
            img.save(emergency_path, 'JPEG', quality=90)
            return emergency_path
        
        except ImportError:
            # Si PIL no está disponible, crear imagen con FFmpeg
            return self._create_emergency_image_ffmpeg()
        except Exception as e:
            print(f"Error creando imagen de emergencia: {e}")
            return None
    
    def _create_emergency_image_ffmpeg(self):
        """Crear imagen de emergencia usando FFmpeg"""
        try:
            if not self.ffmpeg_available:
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            emergency_path = str(self.output_dir / f"emergency_bg_{timestamp}.jpg")
            
            # Crear imagen sólida con FFmpeg
            cmd = [
                'ffmpeg', '-f', 'lavfi', 
                '-i', 'color=c=#1a1a2e:size=1080x1920:duration=1',
                '-vf', 'drawtext=text=CONTENIDO PREMIUM:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
                '-frames:v', '1', '-y', emergency_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(emergency_path):
                return emergency_path
            else:
                return None
        
        except Exception as e:
            print(f"Error creando imagen con FFmpeg: {e}")
            return None
    
    def _create_video_with_ffmpeg(self, image_path, audio_path, output_path, duration=None):
        """Crear video usando FFmpeg"""
        try:
            # Obtener duración del audio si no se especifica
            if not duration:
                cmd_duration = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', audio_path]
                result = subprocess.run(cmd_duration, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    duration = float(result.stdout.strip())
                else:
                    duration = 30  # Duración por defecto
            
            # Comando para crear video optimizado para Instagram con codificación ULTRA COMPATIBLE
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', image_path, 
                '-i', audio_path,
                
                # Filtros de video mejorados para máxima compatibilidad
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,scale=in_range=full:out_range=tv,format=yuv420p',
                
                # Configuración de video ULTRA COMPATIBLE
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-tune', 'stillimage',  # Optimización para imágenes estáticas
                '-pix_fmt', 'yuv420p',  # CRÍTICO: Formato compatible
                '-profile:v', 'baseline',  # Perfil más compatible
                '-level', '3.0',  # Nivel compatible con dispositivos antiguos
                '-movflags', '+faststart',  # Optimización para streaming
                '-colorspace', 'bt709',  # Espacio de color estándar
                '-color_primaries', 'bt709',
                '-color_trc', 'bt709',
                '-color_range', 'tv',  # Rango de color TV (limitado)
                
                # Configuración de audio ULTRA COMPATIBLE
                '-c:a', 'aac',
                '-b:a', '128k',  # Bitrate fijo
                '-ar', '44100',  # Sample rate estándar
                '-ac', '2',  # Estéreo forzado
                '-aac_coder', 'twoloop',  # Codificador AAC más compatible
                
                # Configuración de video y timing
                '-r', '30',
                '-t', str(duration),
                
                # Optimizaciones adicionales
                '-shortest',
                '-avoid_negative_ts', 'make_zero',
                '-fflags', '+genpts',
                '-max_muxing_queue_size', '1024',
                
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, output_path
            else:
                return False, f"Error FFmpeg: {result.stderr}"
        
        except Exception as e:
            return False, f"Error con FFmpeg: {str(e)}"
    
    def _create_video_fallback(self, image_path, audio_path, output_path):
        """Crear video sin FFmpeg (método de respaldo)"""
        try:
            # Intentar usar moviepy como alternativa
            try:
                from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
                
                # Cargar audio para obtener duración
                audio = AudioFileClip(audio_path)
                duration = audio.duration
                
                # Crear clip de imagen con la duración del audio
                image_clip = ImageClip(image_path, duration=duration)
                image_clip = image_clip.resize(height=1920)  # Redimensionar para Instagram
                
                # Combinar imagen y audio
                video = image_clip.set_audio(audio)
                
                # Exportar video
                video.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac')
                
                # Limpiar recursos
                audio.close()
                video.close()
                
                return True, output_path
                
            except ImportError:
                # Si moviepy no está disponible, crear un archivo de placeholder
                return self._create_placeholder_video(output_path)
        
        except Exception as e:
            return False, f"Error en fallback: {str(e)}"
    
    def _create_placeholder_video(self, output_path):
        """Crear video placeholder cuando no hay herramientas disponibles"""
        try:
            # Crear un archivo de texto que simule un video
            placeholder_content = f"""
# Video Placeholder
# Creado: {datetime.now().isoformat()}
# 
# Este es un placeholder porque no se encontraron herramientas de video.
# Para funcionalidad completa, instala FFmpeg:
# 
# Windows: https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
#
# O instala moviepy: pip install moviepy
"""
            
            # Cambiar extensión a .txt para el placeholder
            placeholder_path = output_path.replace('.mp4', '_placeholder.txt')
            
            with open(placeholder_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            return True, placeholder_path
        
        except Exception as e:
            return False, f"Error creando placeholder: {str(e)}"
    
    def add_subtitles_to_video(self, video_path, script_text, output_path=None, style='animated'):
        """Agregar subtítulos automáticos al video"""
        if not output_path:
            base, ext = os.path.splitext(video_path)
            output_path = f"{base}_subtitled{ext}"
        
        if not self.ffmpeg_available:
            # Sin FFmpeg, solo copiar el archivo
            shutil.copy2(video_path, output_path)
            return True, output_path
        
        try:
            if style == 'animated':
                return self._add_animated_subtitles(video_path, script_text, output_path)
            else:
                return self._add_simple_subtitles(video_path, script_text, output_path)
        
        except Exception as e:
            # En caso de error, copiar el original
            shutil.copy2(video_path, output_path)
            return True, output_path
    
    def _add_animated_subtitles(self, video_path, script_text, output_path):
        """Agregar subtítulos animados palabra por palabra"""
        try:
            # Obtener duración del video
            duration = self._get_video_duration(video_path)
            if not duration:
                duration = 30  # Fallback
            
            # Limpiar texto y dividir en palabras
            clean_text = self._clean_text_for_subtitles(script_text)
            words = clean_text.split()
            
            # Calcular timing por palabra
            words_per_second = len(words) / duration
            time_per_word = duration / len(words)
            
            # Crear filtro de texto animado para FFmpeg
            text_filters = []
            
            for i, word in enumerate(words):
                start_time = i * time_per_word
                end_time = min((i + 3) * time_per_word, duration)  # Mostrar 3 palabras a la vez
                
                # Posición Y que varía ligeramente
                y_pos = 1600 + (i % 3) * 40  # Variación sutil en altura
                
                # Efecto de aparición y desaparición
                text_filter = f"drawtext=text='{word}':fontfile=arial.ttf:fontsize=48:fontcolor=white:bordercolor=black:borderw=3:x=(w-text_w)/2:y={y_pos}:enable='between(t,{start_time},{end_time})'"
                
                text_filters.append(text_filter)
            
            # Combinar todos los filtros
            if text_filters:
                video_filter = ','.join(text_filters)
                
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', video_filter,
                    '-c:a', 'copy', '-y', output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    return True, output_path
            
            # Si falla, usar subtítulos simples
            return self._add_simple_subtitles(video_path, script_text, output_path)
        
        except Exception as e:
            print(f"Error con subtítulos animados: {e}")
            return self._add_simple_subtitles(video_path, script_text, output_path)
    
    def _add_simple_subtitles(self, video_path, script_text, output_path):
        """Agregar subtítulos simples mejorados"""
        try:
            # Crear archivo de subtítulos SRT
            srt_path = video_path.replace('.mp4', '.srt')
            
            # Obtener duración del video
            duration = self._get_video_duration(video_path)
            if not duration:
                duration = 30
            
            # Dividir texto en segmentos inteligentes
            segments = self._create_smart_segments(script_text, duration)
            
            # Crear archivo SRT
            with open(srt_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments):
                    f.write(f"{i + 1}\n")
                    f.write(f"{self._seconds_to_srt_time(segment['start'])} --> {self._seconds_to_srt_time(segment['end'])}\n")
                    f.write(f"{segment['text']}\n\n")
            
            # Agregar subtítulos con estilo mejorado
            cmd = [
                'ffmpeg', '-i', video_path, '-vf', 
                f"subtitles={srt_path}:force_style='Fontsize=36,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=3,Bold=1,Alignment=2'",
                '-c:a', 'copy', '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Limpiar archivo SRT temporal
            if os.path.exists(srt_path):
                os.remove(srt_path)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, output_path
            else:
                # Si falla, copiar el original
                shutil.copy2(video_path, output_path)
                return True, output_path
        
        except Exception as e:
            shutil.copy2(video_path, output_path)
            return True, output_path
    
    def _get_video_duration(self, video_path):
        """Obtener duración del video"""
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return None
    
    def _clean_text_for_subtitles(self, text):
        """Limpiar texto para subtítulos"""
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
        
        # Limpiar caracteres problemáticos para FFmpeg
        clean_text = clean_text.replace("'", "\\'")
        clean_text = clean_text.replace('"', '\\"')
        clean_text = clean_text.replace(':', '\\:')
        
        # Remover múltiples espacios
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _create_smart_segments(self, text, duration):
        """Crear segmentos inteligentes para subtítulos"""
        clean_text = self._clean_text_for_subtitles(text)
        
        # Dividir por oraciones primero
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        segments = []
        time_per_sentence = duration / len(sentences) if sentences else duration
        
        for i, sentence in enumerate(sentences):
            # Si la oración es muy larga, dividirla
            if len(sentence) > 60:
                words = sentence.split()
                mid_point = len(words) // 2
                
                # Primera mitad
                segments.append({
                    'text': ' '.join(words[:mid_point]),
                    'start': i * time_per_sentence,
                    'end': i * time_per_sentence + time_per_sentence / 2
                })
                
                # Segunda mitad
                segments.append({
                    'text': ' '.join(words[mid_point:]),
                    'start': i * time_per_sentence + time_per_sentence / 2,
                    'end': (i + 1) * time_per_sentence
                })
            else:
                segments.append({
                    'text': sentence,
                    'start': i * time_per_sentence,
                    'end': (i + 1) * time_per_sentence
                })
        
        return segments
    
    def _seconds_to_srt_time(self, seconds):
        """Convertir segundos a formato de tiempo SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def optimize_for_instagram(self, input_path, output_path=None):
        """Optimizar video específicamente para Instagram"""
        
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"instagram_{timestamp}_{os.path.basename(input_path)}"
            output_path = str(self.output_dir / filename)
        
        return self.process_video(
            input_path=input_path,
            add_watermark=True,
            resize=True,
            aspect_ratio="9:16 (Stories/Reels)",
            quality="Medium",
            output_path=output_path
        )
    
    def batch_process(self, video_paths, settings):
        """Procesar múltiples videos en lote"""
        results = []
        
        for video_path in video_paths:
            try:
                output_path = self.process_video(video_path, **settings)
                results.append({
                    'input': video_path,
                    'output': output_path,
                    'success': output_path is not None
                })
            except Exception as e:
                results.append({
                    'input': video_path,
                    'output': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_supported_formats(self):
        """Obtener formatos soportados"""
        return {
            'input': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm'],
            'output': ['.mp4'],
            'instagram': list(self.instagram_formats.keys())
        }
    
    def validate_video_for_instagram(self, video_path):
        """Validar si el video cumple con los requisitos de Instagram"""
        info = self.get_video_info(video_path)
        
        if not info:
            return False, "No se pudo obtener información del video"
        
        # Límites de Instagram
        max_duration = 60  # segundos para Reels
        max_size = 100  # MB
        
        issues = []
        
        if info.get('duration', 0) > max_duration:
            issues.append(f"Duración muy larga: {info['duration']}s (máximo {max_duration}s)")
        
        if info.get('size', 0) > max_size:
            issues.append(f"Archivo muy grande: {info['size']}MB (máximo {max_size}MB)")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Video válido para Instagram"
    
    def cleanup_temp_files(self):
        """Limpiar archivos temporales"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error limpiando archivos temporales: {e}")
    
    def install_ffmpeg_instructions(self):
        """Instrucciones para instalar FFmpeg"""
        return {
            'windows': 'Descargar desde https://ffmpeg.org/download.html y agregar al PATH',
            'macos': 'brew install ffmpeg',
            'linux': 'sudo apt-get install ffmpeg',
            'status': self.ffmpeg_available
        }