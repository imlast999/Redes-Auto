# -*- coding: utf-8 -*-
"""
Templates de video profesionales para Instagram Video Dashboard
Diferentes estilos visuales para crear contenido atractivo
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class VideoTemplates:
    def __init__(self):
        self.templates_dir = Path('generated/templates')
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Definir templates disponibles
        self.templates = {
            'luxury_gold': {
                'name': 'Luxury Gold',
                'description': 'Elegante template dorado para contenido de lujo',
                'colors': {
                    'primary': '#FFD700',
                    'secondary': '#FFA500',
                    'accent': '#FF6B35',
                    'background': '#1a1a2e',
                    'text': '#FFFFFF'
                },
                'fonts': {
                    'title': {'size': 48, 'weight': 'bold'},
                    'subtitle': {'size': 36, 'weight': 'normal'},
                    'body': {'size': 32, 'weight': 'normal'}
                },
                'animations': {
                    'text_entrance': 'fade_in_up',
                    'text_emphasis': 'pulse',
                    'background': 'gradient_shift'
                }
            },
            'crypto_neon': {
                'name': 'Crypto Neon',
                'description': 'Template futurista con efectos neón para crypto',
                'colors': {
                    'primary': '#00D4FF',
                    'secondary': '#FF6B35',
                    'accent': '#32CD32',
                    'background': '#0a0a0a',
                    'text': '#FFFFFF'
                },
                'fonts': {
                    'title': {'size': 52, 'weight': 'bold'},
                    'subtitle': {'size': 38, 'weight': 'normal'},
                    'body': {'size': 34, 'weight': 'normal'}
                },
                'animations': {
                    'text_entrance': 'slide_in_left',
                    'text_emphasis': 'glow',
                    'background': 'matrix_rain'
                }
            },
            'business_pro': {
                'name': 'Business Pro',
                'description': 'Template profesional para contenido de negocios',
                'colors': {
                    'primary': '#0066CC',
                    'secondary': '#4169E1',
                    'accent': '#1E90FF',
                    'background': '#2c3e50',
                    'text': '#FFFFFF'
                },
                'fonts': {
                    'title': {'size': 46, 'weight': 'bold'},
                    'subtitle': {'size': 34, 'weight': 'normal'},
                    'body': {'size': 30, 'weight': 'normal'}
                },
                'animations': {
                    'text_entrance': 'fade_in',
                    'text_emphasis': 'scale',
                    'background': 'subtle_movement'
                }
            },
            'lifestyle_vibrant': {
                'name': 'Lifestyle Vibrant',
                'description': 'Template colorido y vibrante para lifestyle',
                'colors': {
                    'primary': '#FF69B4',
                    'secondary': '#FF1493',
                    'accent': '#DA70D6',
                    'background': '#2c1810',
                    'text': '#FFFFFF'
                },
                'fonts': {
                    'title': {'size': 50, 'weight': 'bold'},
                    'subtitle': {'size': 36, 'weight': 'normal'},
                    'body': {'size': 32, 'weight': 'normal'}
                },
                'animations': {
                    'text_entrance': 'bounce_in',
                    'text_emphasis': 'rainbow',
                    'background': 'color_wave'
                }
            },
            'motivation_fire': {
                'name': 'Motivation Fire',
                'description': 'Template energético para contenido motivacional',
                'colors': {
                    'primary': '#FF4500',
                    'secondary': '#FF6347',
                    'accent': '#FFD700',
                    'background': '#1a0000',
                    'text': '#FFFFFF'
                },
                'fonts': {
                    'title': {'size': 54, 'weight': 'bold'},
                    'subtitle': {'size': 40, 'weight': 'bold'},
                    'body': {'size': 36, 'weight': 'normal'}
                },
                'animations': {
                    'text_entrance': 'explode_in',
                    'text_emphasis': 'fire_effect',
                    'background': 'flame_movement'
                }
            }
        }
    
    def get_available_templates(self) -> Dict:
        """Obtener templates disponibles"""
        return self.templates
    
    def apply_template_to_video(self, video_path: str, script_text: str, template_name: str, output_path: str = None) -> Tuple[bool, str]:
        """Aplicar template a un video"""
        if template_name not in self.templates:
            return False, f"Template '{template_name}' no encontrado"
        
        template = self.templates[template_name]
        
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = str(self.templates_dir / f"templated_{template_name}_{timestamp}.mp4")
        
        try:
            # Verificar si FFmpeg está disponible
            if self._check_ffmpeg():
                return self._apply_template_with_ffmpeg(video_path, script_text, template, output_path)
            else:
                # Fallback: copiar video original
                import shutil
                shutil.copy2(video_path, output_path)
                return True, output_path
        
        except Exception as e:
            return False, f"Error aplicando template: {str(e)}"
    
    def _apply_template_with_ffmpeg(self, video_path: str, script_text: str, template: Dict, output_path: str) -> Tuple[bool, str]:
        """Aplicar template usando FFmpeg"""
        try:
            import subprocess
            
            # Crear filtros de video basados en el template
            video_filters = []
            
            # Filtro de fondo
            bg_filter = self._create_background_filter(template)
            if bg_filter:
                video_filters.append(bg_filter)
            
            # Filtros de texto animado
            text_filters = self._create_text_filters(script_text, template)
            video_filters.extend(text_filters)
            
            # Efectos adicionales
            effect_filters = self._create_effect_filters(template)
            video_filters.extend(effect_filters)
            
            # Combinar todos los filtros
            if video_filters:
                filter_complex = ','.join(video_filters)
                
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-vf', filter_complex,
                    '-c:a', 'copy', '-y', output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    return True, output_path
                else:
                    print(f"FFmpeg error: {result.stderr}")
                    return False, f"Error FFmpeg: {result.stderr}"
            
            return False, "No se pudieron crear filtros"
        
        except Exception as e:
            return False, f"Error con FFmpeg: {str(e)}"
    
    def _create_background_filter(self, template: Dict) -> str:
        """Crear filtro de fondo basado en el template"""
        colors = template['colors']
        animation = template['animations']['background']
        
        if animation == 'gradient_shift':
            return f"colorkey={colors['background']}:0.3:0.1"
        elif animation == 'matrix_rain':
            return "noise=alls=20:allf=t+u"
        elif animation == 'subtle_movement':
            return "crop=iw-20:ih-20:10+5*sin(t):10+5*cos(t)"
        elif animation == 'color_wave':
            return f"hue=h=t*30:s=sin(t)+1"
        elif animation == 'flame_movement':
            return "noise=alls=10:allf=t,hue=h=10+t*5"
        
        return ""
    
    def _create_text_filters(self, script_text: str, template: Dict) -> List[str]:
        """Crear filtros de texto animado"""
        colors = template['colors']
        fonts = template['fonts']
        animation = template['animations']['text_entrance']
        
        # Limpiar texto
        clean_text = self._clean_text_for_ffmpeg(script_text)
        
        # Dividir en segmentos
        words = clean_text.split()
        filters = []
        
        # Crear filtros para diferentes segmentos del texto
        segments = self._create_text_segments(words)
        
        for i, segment in enumerate(segments):
            start_time = i * 2.5
            end_time = (i + 1) * 2.5
            
            # Posición Y basada en el segmento
            y_positions = [1400, 1500, 1600]  # Diferentes alturas
            y_pos = y_positions[i % len(y_positions)]
            
            # Color del texto
            text_color = colors['text'].replace('#', '')
            outline_color = colors['primary'].replace('#', '')
            
            # Crear filtro según el tipo de animación
            if animation == 'fade_in_up':
                text_filter = f"drawtext=text='{segment}':fontsize={fonts['body']['size']}:fontcolor={text_color}:bordercolor={outline_color}:borderw=3:x=(w-text_w)/2:y={y_pos}+50-50*min(1\\,max(0\\,(t-{start_time})/0.5)):alpha=min(1\\,max(0\\,(t-{start_time})/0.5)):enable='between(t,{start_time},{end_time})'"
            elif animation == 'slide_in_left':
                text_filter = f"drawtext=text='{segment}':fontsize={fonts['body']['size']}:fontcolor={text_color}:bordercolor={outline_color}:borderw=3:x=(w-text_w)/2-200+200*min(1\\,max(0\\,(t-{start_time})/0.5)):y={y_pos}:enable='between(t,{start_time},{end_time})'"
            elif animation == 'bounce_in':
                text_filter = f"drawtext=text='{segment}':fontsize={fonts['body']['size']}:fontcolor={text_color}:bordercolor={outline_color}:borderw=3:x=(w-text_w)/2:y={y_pos}-20*abs(sin(t*10)):enable='between(t,{start_time},{end_time})'"
            elif animation == 'explode_in':
                text_filter = f"drawtext=text='{segment}':fontsize={fonts['body']['size']}:fontcolor={text_color}:bordercolor={outline_color}:borderw=4:x=(w-text_w)/2:y={y_pos}:enable='between(t,{start_time},{end_time})'"
            else:  # fade_in por defecto
                text_filter = f"drawtext=text='{segment}':fontsize={fonts['body']['size']}:fontcolor={text_color}:bordercolor={outline_color}:borderw=3:x=(w-text_w)/2:y={y_pos}:enable='between(t,{start_time},{end_time})'"
            
            filters.append(text_filter)
        
        return filters
    
    def _create_effect_filters(self, template: Dict) -> List[str]:
        """Crear filtros de efectos adicionales"""
        filters = []
        
        # Agregar efectos basados en el template
        emphasis = template['animations']['text_emphasis']
        
        if emphasis == 'glow':
            filters.append("unsharp=5:5:1.0:5:5:0.0")
        elif emphasis == 'pulse':
            filters.append("scale=1080+20*sin(t):1920+20*sin(t)")
        elif emphasis == 'fire_effect':
            filters.append("hue=h=t*10:s=2")
        
        return filters
    
    def _create_text_segments(self, words: List[str]) -> List[str]:
        """Crear segmentos de texto optimizados"""
        segments = []
        current_segment = []
        max_words_per_segment = 6
        
        for word in words:
            current_segment.append(word)
            
            if len(current_segment) >= max_words_per_segment or word.endswith(('.', '!', '?')):
                segments.append(' '.join(current_segment))
                current_segment = []
        
        # Agregar último segmento si queda algo
        if current_segment:
            segments.append(' '.join(current_segment))
        
        return segments
    
    def _clean_text_for_ffmpeg(self, text: str) -> str:
        """Limpiar texto para FFmpeg"""
        import re
        
        # Remover emojis
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"
                                 u"\U0001F300-\U0001F5FF"
                                 u"\U0001F680-\U0001F6FF"
                                 u"\U0001F1E0-\U0001F1FF"
                                 u"\U00002702-\U000027B0"
                                 u"\U000024C2-\U0001F251"
                                 "]+", flags=re.UNICODE)
        
        clean_text = emoji_pattern.sub('', text)
        
        # Escapar caracteres especiales para FFmpeg
        clean_text = clean_text.replace("'", "\\'")
        clean_text = clean_text.replace('"', '\\"')
        clean_text = clean_text.replace(':', '\\:')
        clean_text = clean_text.replace(',', '\\,')
        
        # Remover múltiples espacios
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _check_ffmpeg(self) -> bool:
        """Verificar si FFmpeg está disponible"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def create_template_preview(self, template_name: str) -> Tuple[bool, str]:
        """Crear preview de un template"""
        if template_name not in self.templates:
            return False, f"Template '{template_name}' no encontrado"
        
        template = self.templates[template_name]
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Crear imagen de preview
            img = Image.new('RGB', (540, 960), color=template['colors']['background'])  # Mitad del tamaño
            draw = ImageDraw.Draw(img)
            
            # Agregar elementos del template
            self._draw_template_preview(draw, template)
            
            # Guardar preview
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            preview_path = self.templates_dir / f"preview_{template_name}_{timestamp}.jpg"
            
            img.save(preview_path, 'JPEG', quality=90)
            return True, str(preview_path)
        
        except Exception as e:
            return False, f"Error creando preview: {str(e)}"
    
    def _draw_template_preview(self, draw, template: Dict):
        """Dibujar preview del template"""
        colors = template['colors']
        
        # Convertir colores hex a RGB
        def hex_to_rgb(hex_color):
            return tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        
        primary_rgb = hex_to_rgb(colors['primary'])
        secondary_rgb = hex_to_rgb(colors['secondary'])
        text_rgb = hex_to_rgb(colors['text'])
        
        # Dibujar elementos decorativos
        draw.rectangle([20, 20, 520, 940], outline=primary_rgb, width=3)
        draw.rectangle([40, 40, 500, 920], outline=secondary_rgb, width=2)
        
        # Título del template
        try:
            font_large = ImageFont.truetype("arial.ttf", 36)
            font_medium = ImageFont.truetype("arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Nombre del template
        name = template['name']
        bbox = draw.textbbox((0, 0), name, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (540 - text_width) // 2
        
        draw.text((x, 400), name, fill=primary_rgb, font=font_large)
        
        # Descripción
        desc = template['description']
        bbox = draw.textbbox((0, 0), desc, font=font_medium)
        text_width = bbox[2] - bbox[0]
        x = (540 - text_width) // 2
        
        draw.text((x, 450), desc, fill=text_rgb, font=font_medium)
        
        # Elementos decorativos adicionales
        draw.ellipse([100, 200, 150, 250], outline=primary_rgb, width=2)
        draw.ellipse([390, 700, 440, 750], outline=secondary_rgb, width=2)
        
        # Líneas decorativas
        draw.line([(80, 350), (460, 350)], fill=primary_rgb, width=2)
        draw.line([(80, 550), (460, 550)], fill=secondary_rgb, width=2)