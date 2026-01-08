# -*- coding: utf-8 -*-
"""
Procesador de video dinámico con múltiples imágenes y transiciones
Crea videos con imágenes que cambian sincronizadas con el audio
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import subprocess

class DynamicVideoProcessor:
    def __init__(self):
        self.output_dir = Path('videos/dynamic')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de video
        self.video_config = {
            'width': 1080,
            'height': 1920,
            'fps': 30,
            'video_bitrate': '2M',
            'audio_bitrate': '128k'
        }
    
    def create_dynamic_video(self, 
                           audio_path: str, 
                           images_data: List[Dict], 
                           script_title: str = "Dynamic Video") -> Tuple[bool, str, str]:
        """
        Crear video dinámico con múltiples imágenes y transiciones
        
        Args:
            audio_path: Ruta del archivo de audio
            images_data: Lista de datos de imágenes con tiempos
            script_title: Título del script para el nombre del archivo
            
        Returns:
            (success, video_path, message)
        """
        
        try:
            print(f"🎬 Creando video dinámico con {len(images_data)} imágenes...")
            
            # Validar datos
            if not images_data:
                return False, "", "No hay imágenes para procesar"
            
            if not os.path.exists(audio_path):
                return False, "", f"Archivo de audio no encontrado: {audio_path}"
            
            # Obtener duración del audio
            audio_duration = self._get_audio_duration(audio_path)
            if audio_duration <= 0:
                return False, "", "No se pudo obtener la duración del audio"
            
            # Preparar imágenes
            prepared_images = self._prepare_images_for_video(images_data, audio_duration)
            
            # Crear video con FFmpeg
            video_path = self._create_video_with_transitions(
                prepared_images, 
                audio_path, 
                audio_duration, 
                script_title
            )
            
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                message = f"Video dinámico creado: {file_size:.1f}MB, {len(images_data)} imágenes"
                return True, video_path, message
            else:
                return False, "", "Error creando el video"
        
        except Exception as e:
            print(f"Error creando video dinámico: {str(e)}")
            return False, "", f"Error: {str(e)}"
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Obtener duración del audio en segundos"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                print(f"Error obteniendo duración: {result.stderr}")
                return 0.0
        
        except Exception as e:
            print(f"Error obteniendo duración del audio: {str(e)}")
            return 0.0
    
    def _prepare_images_for_video(self, images_data: List[Dict], audio_duration: float) -> List[Dict]:
        """Preparar imágenes con tiempos ajustados"""
        prepared_images = []
        
        # Ordenar por tiempo de inicio
        sorted_images = sorted(images_data, key=lambda x: x.get('start_time', 0))
        
        for i, img_data in enumerate(sorted_images):
            # Validar que la imagen existe
            image_path = img_data.get('image_path', '')
            if not image_path or not os.path.exists(image_path):
                print(f"⚠️  Imagen no encontrada: {image_path}")
                continue
            
            # Ajustar tiempos
            start_time = max(0, img_data.get('start_time', 0))
            end_time = img_data.get('end_time', start_time + 10)
            
            # Asegurar que no exceda la duración del audio
            end_time = min(end_time, audio_duration)
            
            # Asegurar duración mínima de 2 segundos
            if end_time - start_time < 2:
                end_time = min(start_time + 2, audio_duration)
            
            prepared_images.append({
                'image_path': image_path,
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'concept': img_data.get('concept', f'Imagen {i+1}'),
                'style': img_data.get('style', 'default')
            })
        
        # Si hay huecos, extender imágenes o crear transiciones
        prepared_images = self._fill_time_gaps(prepared_images, audio_duration)
        
        return prepared_images
    
    def _fill_time_gaps(self, images: List[Dict], total_duration: float) -> List[Dict]:
        """Llenar huecos de tiempo entre imágenes"""
        if not images:
            return images
        
        filled_images = []
        
        for i, img in enumerate(images):
            filled_images.append(img)
            
            # Verificar si hay hueco con la siguiente imagen
            if i < len(images) - 1:
                next_img = images[i + 1]
                gap = next_img['start_time'] - img['end_time']
                
                if gap > 0.5:  # Si hay un hueco mayor a 0.5 segundos
                    # Extender la imagen actual para llenar el hueco
                    filled_images[-1]['end_time'] = next_img['start_time']
                    filled_images[-1]['duration'] = filled_images[-1]['end_time'] - filled_images[-1]['start_time']
        
        # Asegurar que la última imagen llegue hasta el final
        if filled_images:
            last_img = filled_images[-1]
            if last_img['end_time'] < total_duration:
                filled_images[-1]['end_time'] = total_duration
                filled_images[-1]['duration'] = total_duration - last_img['start_time']
        
        return filled_images
    
    def _create_video_with_transitions(self, 
                                     images: List[Dict], 
                                     audio_path: str, 
                                     duration: float, 
                                     title: str) -> str:
        """Crear video con transiciones usando FFmpeg"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"dynamic_video_{title.replace(' ', '_')}_{timestamp}.mp4"
            output_path = self.output_dir / output_filename
            
            # Crear filtro complejo para FFmpeg
            filter_complex = self._build_ffmpeg_filter(images, duration)
            
            # Construir comando FFmpeg
            cmd = ['ffmpeg', '-y']  # -y para sobrescribir
            
            # Agregar inputs de imágenes
            for img in images:
                cmd.extend(['-loop', '1', '-i', img['image_path']])
            
            # Agregar audio
            cmd.extend(['-i', audio_path])
            
            # Configuración de filtros con codificación compatible
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[final]',  # Video final
                '-map', f'{len(images)}:a',  # Audio
                
                # Configuración de video ULTRA COMPATIBLE
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-tune', 'stillimage',  # Optimización para imágenes estáticas
                '-pix_fmt', 'yuv420p',  # CRÍTICO: Formato de pixel compatible (NO yuvj420p)
                '-profile:v', 'baseline',  # Perfil más compatible (NO high)
                '-level', '3.0',  # Nivel compatible con dispositivos antiguos
                '-movflags', '+faststart',  # Optimización para streaming web
                '-colorspace', 'bt709',  # Espacio de color estándar
                '-color_primaries', 'bt709',
                '-color_trc', 'bt709',
                
                # Configuración de audio ULTRA COMPATIBLE
                '-c:a', 'aac',
                '-b:a', '128k',  # Bitrate fijo más compatible
                '-ar', '44100',  # Sample rate estándar (NO 24000)
                '-ac', '2',  # Estéreo forzado
                '-aac_coder', 'twoloop',  # Codificador AAC más compatible
                
                # Configuración general mejorada
                '-r', str(self.video_config['fps']),
                '-t', str(duration),
                '-avoid_negative_ts', 'make_zero',  # Evitar timestamps negativos
                '-fflags', '+genpts',  # Generar timestamps correctos
                '-max_muxing_queue_size', '1024',  # Buffer más grande para evitar errores
                
                str(output_path)
            ])
            
            print(f"🎬 Ejecutando FFmpeg para crear video dinámico...")
            print(f"📁 Salida: {output_path}")
            
            # Ejecutar comando
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Video dinámico creado exitosamente")
                return str(output_path)
            else:
                print(f"❌ Error en FFmpeg: {result.stderr}")
                return ""
        
        except Exception as e:
            print(f"Error creando video con transiciones: {str(e)}")
            return ""
    
    def _build_ffmpeg_filter(self, images: List[Dict], total_duration: float) -> str:
        """Construir filtro complejo de FFmpeg para transiciones"""
        try:
            filters = []
            
            # Preparar cada imagen con conversión de formato
            for i, img in enumerate(images):
                # Escalar, ajustar imagen y forzar formato yuv420p
                filters.append(
                    f"[{i}:v]scale={self.video_config['width']}:{self.video_config['height']}:"
                    f"force_original_aspect_ratio=decrease,pad={self.video_config['width']}:"
                    f"{self.video_config['height']}:(ow-iw)/2:(oh-ih)/2:black,"
                    f"scale=in_range=full:out_range=tv,format=yuv420p,setsar=1[img{i}]"
                )
            
            # Si solo hay una imagen, usarla para todo el video
            if len(images) == 1:
                filters.append(f"[img0]trim=duration={total_duration}[final]")
                return ';'.join(filters)
            
            # Crear transiciones entre imágenes
            transition_filters = []
            current_stream = "img0"
            
            for i in range(len(images) - 1):
                next_img = f"img{i+1}"
                transition_stream = f"trans{i}"
                
                # Calcular tiempos de transición
                img_end = images[i]['end_time']
                next_start = images[i+1]['start_time']
                
                # Duración de transición (0.5 segundos)
                transition_duration = 0.5
                transition_start = max(0, img_end - transition_duration/2)
                
                # Crear transición fade
                transition_filter = (
                    f"[{current_stream}][{next_img}]xfade=transition=fade:"
                    f"duration={transition_duration}:offset={transition_start}[{transition_stream}]"
                )
                
                transition_filters.append(transition_filter)
                current_stream = transition_stream
            
            # Agregar filtros de transición
            filters.extend(transition_filters)
            
            # Stream final
            filters.append(f"[{current_stream}]trim=duration={total_duration}[final]")
            
            return ';'.join(filters)
        
        except Exception as e:
            print(f"Error construyendo filtro FFmpeg: {str(e)}")
            # Filtro simple de fallback
            return f"[0:v]scale={self.video_config['width']}:{self.video_config['height']}:force_original_aspect_ratio=decrease,pad={self.video_config['width']}:{self.video_config['height']}:(ow-iw)/2:(oh-ih)/2:black,setsar=1[final]"
    
    def create_simple_dynamic_video(self, 
                                  audio_path: str, 
                                  images_data: List[Dict], 
                                  title: str = "Simple Dynamic") -> Tuple[bool, str, str]:
        """Crear video dinámico simple (fallback)"""
        try:
            if not images_data:
                return False, "", "No hay imágenes"
            
            # Usar solo la primera imagen si hay problemas
            first_image = images_data[0]
            image_path = first_image.get('image_path', '')
            
            if not os.path.exists(image_path):
                return False, "", "Imagen no encontrada"
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"simple_dynamic_{title.replace(' ', '_')}_{timestamp}.mp4"
            output_path = self.output_dir / output_filename
            
            # Comando FFmpeg simple con codificación ULTRA COMPATIBLE
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-i', image_path,
                '-i', audio_path,
                
                # Configuración de video ULTRA COMPATIBLE
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-tune', 'stillimage',  # Optimización para imágenes estáticas
                '-pix_fmt', 'yuv420p',  # CRÍTICO: Formato compatible (NO yuvj420p)
                '-profile:v', 'baseline',  # Perfil más compatible (NO high)
                '-level', '3.0',  # Nivel compatible con dispositivos antiguos
                '-movflags', '+faststart',  # Optimización para streaming
                '-colorspace', 'bt709',  # Espacio de color estándar
                '-color_primaries', 'bt709',
                '-color_trc', 'bt709',
                
                # Configuración de audio ULTRA COMPATIBLE
                '-c:a', 'aac',
                '-b:a', '128k',  # Bitrate fijo
                '-ar', '44100',  # Sample rate estándar (NO 24000)
                '-ac', '2',  # Estéreo forzado
                '-aac_coder', 'twoloop',  # Codificador AAC más compatible
                
                # Duración y optimización mejorada
                '-shortest',
                '-avoid_negative_ts', 'make_zero',
                '-fflags', '+genpts',
                '-max_muxing_queue_size', '1024',
                
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return True, str(output_path), "Video simple creado"
            else:
                return False, "", f"Error FFmpeg: {result.stderr}"
        
        except Exception as e:
            return False, "", f"Error: {str(e)}"
    
    def get_video_info(self, video_path: str) -> Dict:
        """Obtener información del video creado"""
        try:
            if not os.path.exists(video_path):
                return {}
            
            # Información básica
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            # Obtener duración con FFprobe
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            duration = float(result.stdout.strip()) if result.returncode == 0 else 0
            
            return {
                'file_path': video_path,
                'file_size_mb': round(file_size, 2),
                'duration_seconds': round(duration, 2),
                'resolution': f"{self.video_config['width']}x{self.video_config['height']}",
                'fps': self.video_config['fps'],
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error obteniendo info del video: {str(e)}")
            return {}

# Crear instancia global
dynamic_video_processor = DynamicVideoProcessor()