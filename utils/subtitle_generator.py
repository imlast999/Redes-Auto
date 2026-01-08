# -*- coding: utf-8 -*-
"""
Generador de subtítulos automáticos para Instagram Video Dashboard
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Dict

class SubtitleGenerator:
    def __init__(self):
        self.subtitles_dir = Path('generated/subtitles')
        self.subtitles_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de subtítulos
        self.words_per_subtitle = 6  # Palabras por subtítulo
        self.seconds_per_subtitle = 2.5  # Duración de cada subtítulo
        self.max_chars_per_line = 40  # Caracteres máximos por línea
    
    def generate_subtitles_from_script(self, script_text: str, audio_duration: float = None) -> Tuple[bool, str]:
        """Generar archivo de subtítulos SRT desde un script"""
        try:
            # Limpiar el texto
            clean_text = self._clean_script_text(script_text)
            
            # Dividir en segmentos
            segments = self._split_text_into_segments(clean_text)
            
            # Calcular tiempos
            if audio_duration:
                segments_with_timing = self._calculate_timing_from_duration(segments, audio_duration)
            else:
                segments_with_timing = self._calculate_default_timing(segments)
            
            # Generar archivo SRT
            srt_content = self._generate_srt_content(segments_with_timing)
            
            # Guardar archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            srt_filename = f"subtitles_{timestamp}.srt"
            srt_path = self.subtitles_dir / srt_filename
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return True, str(srt_path)
        
        except Exception as e:
            return False, f"Error generando subtítulos: {str(e)}"
    
    def _clean_script_text(self, text: str) -> str:
        """Limpiar el texto del script"""
        # Remover emojis y caracteres especiales para subtítulos
        clean_text = re.sub(r'[^\w\s\.\,\!\?\-\:]', ' ', text)
        
        # Remover múltiples espacios
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # Remover saltos de línea múltiples
        clean_text = re.sub(r'\n+', ' ', clean_text)
        
        return clean_text.strip()
    
    def _split_text_into_segments(self, text: str) -> List[str]:
        """Dividir texto en segmentos apropiados para subtítulos"""
        words = text.split()
        segments = []
        
        i = 0
        while i < len(words):
            # Tomar un grupo de palabras
            segment_words = words[i:i + self.words_per_subtitle]
            segment = ' '.join(segment_words)
            
            # Si el segmento es muy largo, dividirlo
            if len(segment) > self.max_chars_per_line:
                # Intentar dividir en una coma o punto
                if ',' in segment:
                    parts = segment.split(',', 1)
                    segments.append(parts[0].strip())
                    # Agregar la segunda parte de vuelta a las palabras
                    remaining_words = parts[1].strip().split() + words[i + self.words_per_subtitle:]
                    words = words[:i + self.words_per_subtitle] + remaining_words
                elif '.' in segment:
                    parts = segment.split('.', 1)
                    segments.append(parts[0].strip() + '.')
                    if parts[1].strip():
                        remaining_words = parts[1].strip().split() + words[i + self.words_per_subtitle:]
                        words = words[:i + self.words_per_subtitle] + remaining_words
                else:
                    # Dividir por la mitad
                    mid_point = len(segment_words) // 2
                    segments.append(' '.join(segment_words[:mid_point]))
                    # Agregar la segunda mitad de vuelta
                    words = words[:i] + segment_words[mid_point:] + words[i + self.words_per_subtitle:]
                    i -= self.words_per_subtitle - mid_point
            else:
                segments.append(segment)
            
            i += self.words_per_subtitle
        
        return [seg for seg in segments if seg.strip()]
    
    def _calculate_timing_from_duration(self, segments: List[str], total_duration: float) -> List[Dict]:
        """Calcular tiempos basados en la duración total del audio"""
        segments_with_timing = []
        time_per_segment = total_duration / len(segments)
        
        for i, segment in enumerate(segments):
            start_time = i * time_per_segment
            end_time = (i + 1) * time_per_segment
            
            segments_with_timing.append({
                'text': segment,
                'start': start_time,
                'end': end_time
            })
        
        return segments_with_timing
    
    def _calculate_default_timing(self, segments: List[str]) -> List[Dict]:
        """Calcular tiempos por defecto"""
        segments_with_timing = []
        
        for i, segment in enumerate(segments):
            start_time = i * self.seconds_per_subtitle
            end_time = (i + 1) * self.seconds_per_subtitle
            
            segments_with_timing.append({
                'text': segment,
                'start': start_time,
                'end': end_time
            })
        
        return segments_with_timing
    
    def _generate_srt_content(self, segments_with_timing: List[Dict]) -> str:
        """Generar contenido del archivo SRT"""
        srt_content = ""
        
        for i, segment in enumerate(segments_with_timing, 1):
            start_time = self._seconds_to_srt_time(segment['start'])
            end_time = self._seconds_to_srt_time(segment['end'])
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{segment['text']}\n\n"
        
        return srt_content
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convertir segundos a formato de tiempo SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def generate_vtt_subtitles(self, script_text: str, audio_duration: float = None) -> Tuple[bool, str]:
        """Generar archivo de subtítulos VTT (WebVTT)"""
        try:
            # Usar la misma lógica que SRT pero con formato VTT
            clean_text = self._clean_script_text(script_text)
            segments = self._split_text_into_segments(clean_text)
            
            if audio_duration:
                segments_with_timing = self._calculate_timing_from_duration(segments, audio_duration)
            else:
                segments_with_timing = self._calculate_default_timing(segments)
            
            # Generar contenido VTT
            vtt_content = "WEBVTT\n\n"
            
            for i, segment in enumerate(segments_with_timing, 1):
                start_time = self._seconds_to_vtt_time(segment['start'])
                end_time = self._seconds_to_vtt_time(segment['end'])
                
                vtt_content += f"{start_time} --> {end_time}\n"
                vtt_content += f"{segment['text']}\n\n"
            
            # Guardar archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            vtt_filename = f"subtitles_{timestamp}.vtt"
            vtt_path = self.subtitles_dir / vtt_filename
            
            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write(vtt_content)
            
            return True, str(vtt_path)
        
        except Exception as e:
            return False, f"Error generando subtítulos VTT: {str(e)}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convertir segundos a formato de tiempo VTT (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def get_subtitle_styles(self) -> Dict[str, str]:
        """Obtener estilos predefinidos para subtítulos"""
        return {
            'instagram_style': {
                'font_size': '24',
                'font_color': 'white',
                'outline_color': 'black',
                'outline_width': '2',
                'position': 'bottom'
            },
            'luxury_style': {
                'font_size': '28',
                'font_color': 'gold',
                'outline_color': 'black',
                'outline_width': '3',
                'position': 'bottom'
            },
            'modern_style': {
                'font_size': '26',
                'font_color': 'white',
                'outline_color': 'blue',
                'outline_width': '2',
                'position': 'center'
            }
        }
    
    def create_styled_subtitles(self, script_text: str, style: str = 'instagram_style', 
                              audio_duration: float = None) -> Tuple[bool, str]:
        """Crear subtítulos con estilo específico"""
        try:
            # Generar subtítulos básicos
            success, srt_path = self.generate_subtitles_from_script(script_text, audio_duration)
            
            if not success:
                return False, srt_path
            
            # Aplicar estilo
            styles = self.get_subtitle_styles()
            selected_style = styles.get(style, styles['instagram_style'])
            
            # Crear archivo de estilo ASS (Advanced SubStation Alpha)
            ass_path = srt_path.replace('.srt', '.ass')
            
            ass_content = self._generate_ass_content(srt_path, selected_style)
            
            with open(ass_path, 'w', encoding='utf-8') as f:
                f.write(ass_content)
            
            return True, ass_path
        
        except Exception as e:
            return False, f"Error creando subtítulos con estilo: {str(e)}"
    
    def _generate_ass_content(self, srt_path: str, style: Dict[str, str]) -> str:
        """Generar contenido ASS con estilos"""
        # Leer archivo SRT
        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        # Header ASS básico
        ass_content = f"""[Script Info]
Title: Instagram Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{style['font_size']},&H{style['font_color']},&H{style['font_color']},&H{style['outline_color']},&H00000000,1,0,0,0,100,100,0,0,1,{style['outline_width']},0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Convertir SRT a ASS
        # Esta es una conversión básica - en una implementación completa
        # se haría un parsing más sofisticado del SRT
        
        return ass_content
    
    def get_saved_subtitles(self, limit: int = 10) -> List[Dict]:
        """Obtener subtítulos guardados"""
        subtitles = []
        
        try:
            subtitle_files = sorted(self.subtitles_dir.glob("*.srt"), key=os.path.getmtime, reverse=True)
            
            for subtitle_file in subtitle_files[:limit]:
                try:
                    stat = os.stat(subtitle_file)
                    subtitles.append({
                        'filename': subtitle_file.name,
                        'path': str(subtitle_file),
                        'size_kb': round(stat.st_size / 1024, 2),
                        'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                except Exception as e:
                    print(f"Error leyendo subtítulo {subtitle_file}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Error obteniendo subtítulos guardados: {str(e)}")
        
        return subtitles