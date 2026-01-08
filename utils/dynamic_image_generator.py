# -*- coding: utf-8 -*-
"""
Generador de imágenes dinámicas basado en análisis de scripts
Crea múltiples imágenes sincronizadas con el contenido del audio
"""

import os
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

class DynamicImageGenerator:
    def __init__(self):
        # APIs de generación de imágenes
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY', '')
        self.deepai_api_key = os.getenv('DEEPAI_API_KEY', '')
        self.getimg_api_key = os.getenv('GETIMG_API_KEY', '')
        self.stability_api_key = os.getenv('STABILITY_API_KEY', '')
        
        # Directorio para imágenes
        self.images_dir = Path('generated/dynamic_images')
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_images_from_analysis(self, visual_concepts: List[Dict], style_theme: str = "luxury") -> Tuple[bool, List[Dict], str]:
        """
        Generar múltiples imágenes basadas en el análisis visual
        
        Args:
            visual_concepts: Lista de conceptos visuales del análisis
            style_theme: Tema de estilo general (luxury, modern, minimal, etc.)
            
        Returns:
            (success, generated_images, summary)
        """
        
        print(f"🎨 Generando {len(visual_concepts)} imágenes dinámicas...")
        
        generated_images = []
        successful_generations = 0
        
        # Generar imágenes en paralelo para mayor velocidad
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for i, concept in enumerate(visual_concepts):
                future = executor.submit(self._generate_single_image, concept, style_theme, i)
                futures.append(future)
            
            # Recopilar resultados
            for future in futures:
                try:
                    result = future.result(timeout=60)  # 60 segundos por imagen
                    if result:
                        generated_images.append(result)
                        successful_generations += 1
                except Exception as e:
                    print(f"Error generando imagen: {str(e)}")
                    continue
        
        # Ordenar por tiempo de inicio
        generated_images.sort(key=lambda x: x['start_time'])
        
        # Crear resumen
        summary = f"Generadas {successful_generations}/{len(visual_concepts)} imágenes dinámicas"
        
        return successful_generations > 0, generated_images, summary
    
    def _generate_single_image(self, concept: Dict, style_theme: str, index: int) -> Optional[Dict]:
        """Generar una imagen individual"""
        try:
            # Mejorar el prompt con el tema de estilo
            enhanced_prompt = self._enhance_prompt(concept['prompt_en'], style_theme, concept['emotion'])
            
            print(f"🖼️  Generando imagen {index + 1}: {concept['concept']}")
            
            # Intentar con diferentes APIs
            image_path = None
            image_url = None
            api_used = None
            
            # Prioridad: Replicate > Stability > DeepAI > GetImg
            if self.replicate_api_key and not image_path:
                image_path, image_url, api_used = self._generate_with_replicate(enhanced_prompt, index)
            
            if self.stability_api_key and not image_path:
                image_path, image_url, api_used = self._generate_with_stability(enhanced_prompt, index)
            
            if self.deepai_api_key and not image_path:
                image_path, image_url, api_used = self._generate_with_deepai(enhanced_prompt, index)
            
            if self.getimg_api_key and not image_path:
                image_path, image_url, api_used = self._generate_with_getimg(enhanced_prompt, index)
            
            if not image_path:
                # Crear imagen placeholder
                image_path = self._create_dynamic_placeholder(concept, index)
                api_used = "Dynamic Placeholder"
            
            # Crear resultado
            result = {
                'id': concept['id'],
                'start_time': concept['start_time'],
                'end_time': concept['end_time'],
                'concept': concept['concept'],
                'style': concept['style'],
                'emotion': concept['emotion'],
                'prompt_used': enhanced_prompt,
                'image_path': image_path,
                'image_url': image_url,
                'api_used': api_used,
                'generated_at': datetime.now().isoformat()
            }
            
            print(f"✅ Imagen {index + 1} generada con {api_used}")
            return result
        
        except Exception as e:
            print(f"❌ Error generando imagen {index + 1}: {str(e)}")
            return None
    
    def _enhance_prompt(self, base_prompt: str, style_theme: str, emotion: str) -> str:
        """Mejorar el prompt con estilo y emoción"""
        
        # Estilos por tema
        style_enhancements = {
            'luxury': 'luxury, premium, elegant, gold accents, high-end, sophisticated',
            'modern': 'modern, clean, minimalist, contemporary, sleek, professional',
            'cinematic': 'cinematic lighting, dramatic, movie-style, high contrast, epic',
            'abstract': 'abstract, artistic, creative, unique perspective, stylized',
            'futuristic': 'futuristic, sci-fi, neon lights, high-tech, digital, advanced'
        }
        
        # Mejoras por emoción
        emotion_enhancements = {
            'inspiring': 'uplifting, motivational, bright lighting, positive energy',
            'powerful': 'strong, bold, dramatic lighting, commanding presence',
            'confident': 'self-assured, professional, clear focus, determined',
            'ambitious': 'goal-oriented, forward-looking, dynamic, energetic',
            'successful': 'achievement, victory, celebration, prosperity'
        }
        
        # Construir prompt mejorado
        enhanced_parts = [base_prompt]
        
        # Agregar estilo
        if style_theme in style_enhancements:
            enhanced_parts.append(style_enhancements[style_theme])
        
        # Agregar emoción
        if emotion in emotion_enhancements:
            enhanced_parts.append(emotion_enhancements[emotion])
        
        # Agregar mejoras técnicas
        technical_enhancements = [
            "high quality",
            "4K resolution",
            "professional photography",
            "perfect composition",
            "vibrant colors",
            "sharp focus"
        ]
        
        enhanced_parts.extend(technical_enhancements)
        
        return ", ".join(enhanced_parts)
    
    def _generate_with_replicate(self, prompt: str, index: int) -> Tuple[Optional[str], Optional[str], str]:
        """Generar con Replicate API"""
        try:
            import replicate
            
            # Usar modelo SDXL para mejor calidad
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": prompt,
                    "width": 1080,
                    "height": 1920,  # Formato vertical para Instagram
                    "num_outputs": 1,
                    "scheduler": "K_EULER",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5
                }
            )
            
            if output and len(output) > 0:
                image_url = output[0]
                
                # Descargar imagen
                import requests
                response = requests.get(image_url, timeout=30)
                
                if response.status_code == 200:
                    filename = f"dynamic_image_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    image_path = self.images_dir / filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    
                    return str(image_path), image_url, "Replicate (SDXL)"
            
            return None, None, "Replicate Failed"
        
        except Exception as e:
            print(f"Error con Replicate: {str(e)}")
            return None, None, "Replicate Error"
    
    def _generate_with_stability(self, prompt: str, index: int) -> Tuple[Optional[str], Optional[str], str]:
        """Generar con Stability AI"""
        try:
            import requests
            
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {self.stability_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1920,
                "width": 1080,
                "samples": 1,
                "steps": 30
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'artifacts' in result and len(result['artifacts']) > 0:
                    import base64
                    
                    image_data = base64.b64decode(result['artifacts'][0]['base64'])
                    
                    filename = f"dynamic_image_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    image_path = self.images_dir / filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    return str(image_path), None, "Stability AI (SDXL)"
            
            return None, None, "Stability Failed"
        
        except Exception as e:
            print(f"Error con Stability AI: {str(e)}")
            return None, None, "Stability Error"
    
    def _generate_with_deepai(self, prompt: str, index: int) -> Tuple[Optional[str], Optional[str], str]:
        """Generar con DeepAI"""
        try:
            import requests
            
            url = "https://api.deepai.org/api/text2img"
            
            headers = {
                "Api-Key": self.deepai_api_key
            }
            
            data = {
                "text": prompt,
                "width": 1080,
                "height": 1920
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'output_url' in result:
                    image_url = result['output_url']
                    
                    # Descargar imagen
                    img_response = requests.get(image_url, timeout=30)
                    
                    if img_response.status_code == 200:
                        filename = f"dynamic_image_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                        image_path = self.images_dir / filename
                        
                        with open(image_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        return str(image_path), image_url, "DeepAI"
            
            return None, None, "DeepAI Failed"
        
        except Exception as e:
            print(f"Error con DeepAI: {str(e)}")
            return None, None, "DeepAI Error"
    
    def _generate_with_getimg(self, prompt: str, index: int) -> Tuple[Optional[str], Optional[str], str]:
        """Generar con GetImg.ai"""
        try:
            import requests
            
            url = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {self.getimg_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "model": "stable-diffusion-v1-5",
                "width": 1080,
                "height": 1920,
                "steps": 25,
                "guidance": 7.5
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'image' in result:
                    import base64
                    
                    image_data = base64.b64decode(result['image'])
                    
                    filename = f"dynamic_image_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    image_path = self.images_dir / filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    return str(image_path), None, "GetImg.ai"
            
            return None, None, "GetImg Failed"
        
        except Exception as e:
            print(f"Error con GetImg.ai: {str(e)}")
            return None, None, "GetImg Error"
    
    def _create_dynamic_placeholder(self, concept: Dict, index: int) -> str:
        """Crear placeholder dinámico basado en el concepto"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Crear imagen base
            width, height = 1080, 1920
            
            # Colores por emoción
            emotion_colors = {
                'inspiring': [(255, 215, 0), (255, 140, 0)],  # Dorado a naranja
                'powerful': [(128, 0, 128), (255, 0, 255)],   # Púrpura a magenta
                'confident': [(0, 100, 200), (0, 200, 255)],  # Azul oscuro a claro
                'ambitious': [(255, 0, 0), (255, 100, 100)],  # Rojo a rosa
                'successful': [(0, 128, 0), (144, 238, 144)]  # Verde oscuro a claro
            }
            
            # Obtener colores
            emotion = concept.get('emotion', 'inspiring')
            colors = emotion_colors.get(emotion, emotion_colors['inspiring'])
            
            # Crear gradiente
            image = Image.new('RGB', (width, height), colors[0])
            draw = ImageDraw.Draw(image)
            
            # Crear efecto gradiente
            for y in range(height):
                ratio = y / height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Agregar elementos gráficos
            self._add_graphic_elements(draw, width, height, concept)
            
            # Agregar texto del concepto
            self._add_concept_text(draw, width, height, concept)
            
            # Guardar imagen
            filename = f"dynamic_placeholder_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = self.images_dir / filename
            image.save(image_path, 'PNG', quality=95)
            
            return str(image_path)
        
        except Exception as e:
            print(f"Error creando placeholder dinámico: {str(e)}")
            # Fallback simple
            return self._create_simple_placeholder(index)
    
    def _add_graphic_elements(self, draw, width, height, concept):
        """Agregar elementos gráficos al placeholder"""
        try:
            import random
            
            # Elementos por estilo
            if concept.get('style') == 'luxury':
                # Círculos dorados
                for _ in range(5):
                    x = random.randint(0, width)
                    y = random.randint(0, height)
                    radius = random.randint(20, 100)
                    draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               outline=(255, 215, 0, 100), width=3)
            
            elif concept.get('style') == 'modern':
                # Líneas geométricas
                for _ in range(8):
                    x1 = random.randint(0, width)
                    y1 = random.randint(0, height)
                    x2 = random.randint(0, width)
                    y2 = random.randint(0, height)
                    draw.line([x1, y1, x2, y2], fill=(255, 255, 255, 150), width=2)
            
            elif concept.get('style') == 'abstract':
                # Formas abstractas
                for _ in range(6):
                    points = []
                    for _ in range(6):
                        points.append((random.randint(0, width), random.randint(0, height)))
                    draw.polygon(points, outline=(255, 255, 255, 100), width=2)
        
        except Exception as e:
            print(f"Error agregando elementos gráficos: {str(e)}")
    
    def _add_concept_text(self, draw, width, height, concept):
        """Agregar texto del concepto al placeholder"""
        try:
            # Texto del concepto
            text = concept.get('concept', 'Concepto Visual')
            
            # Intentar cargar fuente
            try:
                font = ImageFont.truetype("arial.ttf", 60)
                small_font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Dividir texto en líneas
            import textwrap
            lines = textwrap.wrap(text, width=20)
            
            # Calcular posición centrada
            total_height = len(lines) * 80
            start_y = (height - total_height) // 2
            
            # Dibujar texto con sombra
            for i, line in enumerate(lines):
                # Calcular posición centrada para cada línea
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + i * 80
                
                # Sombra
                draw.text((x+3, y+3), line, font=font, fill=(0, 0, 0, 180))
                # Texto principal
                draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            
            # Agregar estilo en la parte inferior
            style_text = f"Estilo: {concept.get('style', 'Dinámico')}"
            bbox = draw.textbbox((0, 0), style_text, font=small_font)
            style_width = bbox[2] - bbox[0]
            style_x = (width - style_width) // 2
            style_y = height - 150
            
            draw.text((style_x+2, style_y+2), style_text, font=small_font, fill=(0, 0, 0, 150))
            draw.text((style_x, style_y), style_text, font=small_font, fill=(255, 255, 255, 200))
        
        except Exception as e:
            print(f"Error agregando texto: {str(e)}")
    
    def _create_simple_placeholder(self, index: int) -> str:
        """Crear placeholder simple como último recurso"""
        try:
            from PIL import Image, ImageDraw
            
            width, height = 1080, 1920
            image = Image.new('RGB', (width, height), (100, 50, 150))
            draw = ImageDraw.Draw(image)
            
            # Texto simple
            text = f"Imagen Dinámica {index + 1}"
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height // 2
            
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
            
            filename = f"simple_placeholder_{index+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = self.images_dir / filename
            image.save(image_path, 'PNG')
            
            return str(image_path)
        
        except Exception as e:
            print(f"Error creando placeholder simple: {str(e)}")
            return ""

# Crear instancia global
dynamic_image_generator = DynamicImageGenerator()