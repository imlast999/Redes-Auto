# -*- coding: utf-8 -*-
"""
Generador de imágenes con IA para Instagram Video Dashboard
Utiliza APIs gratuitas para generar fondos de lujo
"""

import os
import requests
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import tempfile
import base64

class AIImageGenerator:
    def __init__(self):
        # APIs de generación de imágenes gratuitas
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY', '')
        self.deepai_api_key = os.getenv('DEEPAI_API_KEY', '')
        self.getimg_api_key = os.getenv('GETIMG_API_KEY', '')
        
        # Directorio para guardar imágenes
        self.images_dir = Path('generated/images')
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Estilos disponibles (ACTUALIZADOS para personas realistas)
        self.styles = {
            'luxury_person': {
                'name': 'Persona de Lujo',
                'description': 'Personas exitosas en entornos de lujo',
                'keywords': ['successful person', 'luxury lifestyle', 'wealthy individual', 'elegant person', 'premium fashion']
            },
            'business_person': {
                'name': 'Empresario/a Exitoso/a',
                'description': 'Personas de negocios, CEOs, emprendedores',
                'keywords': ['business person', 'CEO', 'entrepreneur', 'professional', 'suit', 'confident']
            },
            'crypto_trader': {
                'name': 'Trader de Crypto',
                'description': 'Personas jóvenes exitosas en crypto',
                'keywords': ['crypto trader', 'young millionaire', 'tech entrepreneur', 'digital nomad', 'modern lifestyle']
            },
            'lifestyle_influencer': {
                'name': 'Influencer de Lifestyle',
                'description': 'Personas atractivas viviendo la vida premium',
                'keywords': ['lifestyle influencer', 'attractive person', 'premium life', 'social media', 'trendy']
            },
            'motivation_speaker': {
                'name': 'Speaker Motivacional',
                'description': 'Personas inspiradoras y carismáticas',
                'keywords': ['motivational speaker', 'inspiring person', 'charismatic', 'confident', 'leadership']
            },
            'luxury': {
                'name': 'Lujo y Elegancia (Objetos)',
                'description': 'Imágenes de lujo, mansiones, coches deportivos',
                'keywords': ['luxury', 'mansion', 'supercar', 'yacht', 'diamond', 'gold']
            },
            'business': {
                'name': 'Negocios y Finanzas (Objetos)',
                'description': 'Oficinas modernas, gráficos, dinero',
                'keywords': ['office', 'business', 'money', 'charts', 'success', 'corporate']
            },
            'crypto': {
                'name': 'Criptomonedas (Objetos)',
                'description': 'Bitcoin, blockchain, tecnología',
                'keywords': ['bitcoin', 'crypto', 'blockchain', 'digital', 'technology', 'futuristic']
            },
            'lifestyle': {
                'name': 'Estilo de Vida (Objetos)',
                'description': 'Viajes, experiencias, vida premium',
                'keywords': ['travel', 'lifestyle', 'premium', 'exclusive', 'experience', 'luxury']
            },
            'motivation': {
                'name': 'Motivacional',
                'description': 'Imágenes inspiradoras y motivacionales',
                'keywords': ['success', 'motivation', 'achievement', 'goal', 'winner', 'champion']
            }
        }
        
        # Prompts base para cada estilo
        self.prompt_templates = {
            'luxury': [
                "luxury mansion with infinity pool at sunset, ultra realistic, 4K, cinematic lighting",
                "expensive supercar in front of modern skyscraper, professional photography, golden hour",
                "luxury yacht on crystal clear water, aerial view, paradise setting, high quality",
                "diamond jewelry on black velvet, macro photography, studio lighting, premium",
                "modern penthouse interior, minimalist luxury design, floor to ceiling windows"
            ],
            'business': [
                "modern corporate office with city view, professional, clean, minimalist design",
                "business meeting in glass conference room, professional lighting, corporate style",
                "financial charts and graphs on multiple monitors, trading floor atmosphere",
                "stack of money and gold coins, business success concept, studio photography",
                "handshake in modern office, business deal, professional photography"
            ],
            'crypto': [
                "bitcoin coin with digital blockchain background, futuristic, neon lights, cyber",
                "cryptocurrency trading screens with green charts, high tech, digital art",
                "digital wallet concept with floating coins, blockchain visualization, modern",
                "futuristic city with cryptocurrency symbols, cyberpunk style, neon colors",
                "golden bitcoin on dark background with circuit patterns, premium, detailed"
            ],
            'lifestyle': [
                "luxury travel destination, tropical paradise, crystal clear water, aerial view",
                "first class airplane interior, luxury travel, premium experience, elegant",
                "exclusive restaurant with city view, fine dining, elegant atmosphere",
                "luxury spa and wellness center, relaxation, premium lifestyle, serene",
                "private jet interior, luxury travel, business class, premium lifestyle"
            ],
            'motivation': [
                "person standing on mountain peak at sunrise, success concept, inspirational",
                "trophy and medals on podium, winner concept, golden lighting, achievement",
                "stairway to success with golden light, motivation concept, upward journey",
                "businessman in suit looking at city skyline, success mindset, powerful",
                "hands holding glowing light bulb, innovation concept, creative inspiration"
            ]
        }
    
    def is_configured(self):
        """Verificar si al menos una API está configurada"""
        return bool(self.replicate_api_key or self.deepai_api_key or self.getimg_api_key)
    
    def get_available_styles(self):
        """Obtener estilos disponibles"""
        return self.styles
    
    def generate_image(self, prompt: str, style: str = 'luxury') -> Tuple[bool, str, str, str]:
        """Generar imagen con IA"""
        if not self.is_configured():
            return False, "No hay APIs de generación de imágenes configuradas", "", "Error"
        
        # Mejorar prompt con estilo
        enhanced_prompt = self._enhance_prompt(prompt, style)
        
        # Intentar generar con diferentes APIs
        image_path = None
        image_url = None
        api_used = None
        
        if self.replicate_api_key:
            success, result, url, api = self._generate_with_replicate(enhanced_prompt)
            if success:
                image_path, image_url, api_used = result, url, api
        
        if not image_path and self.deepai_api_key:
            success, result, url, api = self._generate_with_deepai(enhanced_prompt)
            if success:
                image_path, image_url, api_used = result, url, api
        
        if not image_path and self.getimg_api_key:
            success, result, url, api = self._generate_with_getimg(enhanced_prompt)
            if success:
                image_path, image_url, api_used = result, url, api
        
        if not image_path:
            # Fallback: imagen placeholder
            image_path = self._create_placeholder_image(style)
            api_used = "Placeholder"
        
        return bool(image_path), image_path, image_url or "", api_used
    
    def generate_from_script(self, script: str, style: str = 'luxury') -> Tuple[bool, str, str, str]:
        """Generar imagen basada en un script"""
        # Extraer conceptos clave del script
        key_concepts = self._extract_concepts_from_script(script, style)
        
        # Crear prompt basado en conceptos
        prompt = self._create_prompt_from_concepts(key_concepts, style)
        
        return self.generate_image(prompt, style)
    
    def generate_multiple_backgrounds(self, script: str, style: str = 'luxury', count: int = 3) -> Tuple[bool, List[str], str]:
        """Generar múltiples fondos para crear variedad visual"""
        backgrounds = []
        api_used = "Multiple Generation"
        
        # Generar diferentes variaciones del prompt
        base_concepts = self._extract_concepts_from_script(script, style)
        
        variations = [
            "cinematic wide shot",
            "close-up detailed view", 
            "aerial perspective view"
        ]
        
        for i in range(count):
            variation = variations[i % len(variations)]
            prompt = self._create_prompt_from_concepts(base_concepts, style) + f", {variation}"
            
            success, image_path, image_url, api = self.generate_image(prompt, style)
            
            if success:
                backgrounds.append(image_path)
                api_used = api
            else:
                # Si falla, crear placeholder
                placeholder = self._create_placeholder_image(f"{style}_{i}")
                if placeholder:
                    backgrounds.append(placeholder)
                    api_used = "Placeholder Generator"
        
        if backgrounds:
            return True, backgrounds, api_used
        else:
            return False, [], "Error generating backgrounds"
    
    def create_animated_background_sequence(self, backgrounds: List[str], output_path: str = None) -> Tuple[bool, str]:
        """Crear secuencia de fondos para simular animación"""
        if not backgrounds:
            return False, "No backgrounds provided"
        
        try:
            if not output_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = str(self.images_dir / f"animated_bg_{timestamp}.mp4")
            
            # Intentar crear video con transiciones usando FFmpeg
            if self._check_ffmpeg():
                return self._create_video_sequence_ffmpeg(backgrounds, output_path)
            else:
                # Fallback: usar la primera imagen
                return True, backgrounds[0]
        
        except Exception as e:
            return False, f"Error creating animated sequence: {str(e)}"
    
    def _check_ffmpeg(self):
        """Verificar si FFmpeg está disponible"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _create_video_sequence_ffmpeg(self, backgrounds: List[str], output_path: str) -> Tuple[bool, str]:
        """Crear secuencia de video con FFmpeg"""
        try:
            import subprocess
            
            # Crear lista de archivos para FFmpeg
            file_list_path = str(self.images_dir / "bg_sequence.txt")
            
            with open(file_list_path, 'w') as f:
                for bg in backgrounds:
                    # Cada imagen se muestra por 2 segundos
                    f.write(f"file '{os.path.abspath(bg)}'\n")
                    f.write("duration 2\n")
                # Repetir la última imagen
                f.write(f"file '{os.path.abspath(backgrounds[-1])}'\n")
            
            # Comando FFmpeg para crear video con transiciones
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', file_list_path,
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
                '-c:v', 'libx264', '-r', '30', '-pix_fmt', 'yuv420p',
                '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Limpiar archivo temporal
            if os.path.exists(file_list_path):
                os.remove(file_list_path)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, output_path
            else:
                # Si falla, devolver la primera imagen
                return True, backgrounds[0]
        
        except Exception as e:
            return False, f"Error with FFmpeg: {str(e)}"
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Mejorar prompt con palabras clave del estilo"""
        style_data = self.styles.get(style, self.styles['luxury_person'])
        style_keywords = style_data['keywords']
        
        # Detectar si es un estilo de persona
        is_person_style = 'person' in style or any(keyword in style for keyword in ['business_person', 'crypto_trader', 'lifestyle_influencer', 'motivation_speaker'])
        
        # Agregar palabras clave del estilo
        enhanced = f"{prompt}, {', '.join(style_keywords[:3])}"
        
        if is_person_style:
            # Modificadores específicos para personas
            person_modifiers = [
                "photorealistic portrait", "professional headshot", "confident expression",
                "modern fashion", "Instagram worthy", "high-end photography",
                "natural lighting", "sharp facial details", "charismatic presence"
            ]
            enhanced += f", {', '.join(random.sample(person_modifiers, 4))}"
        else:
            # Modificadores para objetos/paisajes
            quality_modifiers = [
                "high quality", "professional photography", "ultra realistic",
                "4K resolution", "cinematic lighting", "detailed", "premium"
            ]
            enhanced += f", {', '.join(random.sample(quality_modifiers, 3))}"
        
        return enhanced
    
    def _extract_concepts_from_script(self, script: str, style: str) -> List[str]:
        """Extraer conceptos clave de un script"""
        # Palabras clave por estilo (ACTUALIZADAS para personas)
        concept_keywords = {
            'luxury_person': ['millonario', 'riqueza', 'éxito', 'lujo', 'persona exitosa', 'empresario', 'elegante'],
            'business_person': ['negocio', 'empresa', 'CEO', 'emprendedor', 'profesional', 'líder', 'ejecutivo'],
            'crypto_trader': ['bitcoin', 'crypto', 'trading', 'joven', 'millonario', 'tecnología', 'digital'],
            'lifestyle_influencer': ['vida', 'experiencia', 'influencer', 'atractivo', 'premium', 'social', 'trendy'],
            'motivation_speaker': ['éxito', 'motivación', 'inspiración', 'líder', 'confianza', 'carisma', 'speaker'],
            'luxury': ['millonario', 'riqueza', 'éxito', 'lujo', 'dinero', 'mansión', 'coche', 'yacht'],
            'business': ['negocio', 'empresa', 'oficina', 'reunión', 'dinero', 'inversión', 'CEO'],
            'crypto': ['bitcoin', 'crypto', 'blockchain', 'trading', 'digital', 'futuro', 'tecnología'],
            'lifestyle': ['vida', 'experiencia', 'viaje', 'exclusivo', 'premium', 'lujo', 'estilo'],
            'motivation': ['éxito', 'meta', 'logro', 'motivación', 'inspiración', 'ganador', 'campeón']
        }
        
        keywords = concept_keywords.get(style, concept_keywords['luxury'])
        found_concepts = []
        
        script_lower = script.lower()
        for keyword in keywords:
            if keyword in script_lower:
                found_concepts.append(keyword)
        
        return found_concepts[:5]  # Máximo 5 conceptos
    
    def _create_prompt_from_concepts(self, concepts: List[str], style: str) -> str:
        """Crear prompt basado en conceptos extraídos"""
        if not concepts:
            # Usar prompt aleatorio del estilo
            return random.choice(self.prompt_templates.get(style, self.prompt_templates['luxury']))
        
        # Mapear conceptos a elementos visuales
        visual_mapping = {
            'millonario': 'luxury mansion',
            'riqueza': 'gold coins and money',
            'éxito': 'trophy and success symbols',
            'lujo': 'luxury lifestyle elements',
            'dinero': 'stack of money',
            'mansión': 'luxury mansion',
            'coche': 'expensive supercar',
            'yacht': 'luxury yacht',
            'negocio': 'modern office building',
            'empresa': 'corporate headquarters',
            'oficina': 'modern office interior',
            'bitcoin': 'golden bitcoin coin',
            'crypto': 'cryptocurrency symbols',
            'blockchain': 'digital blockchain visualization',
            'vida': 'luxury lifestyle scene',
            'viaje': 'luxury travel destination',
            'exclusivo': 'exclusive premium setting'
        }
        
        visual_elements = []
        for concept in concepts:
            if concept in visual_mapping:
                visual_elements.append(visual_mapping[concept])
        
        if visual_elements:
            base_prompt = f"{', '.join(visual_elements[:3])}"
        else:
            base_prompt = random.choice(self.prompt_templates.get(style, self.prompt_templates['luxury']))
        
        return base_prompt
    
    def _generate_with_replicate(self, prompt: str) -> Tuple[bool, str, str, str]:
        """Generar imagen con Replicate usando Flux para personas realistas"""
        try:
            import time
            
            url = "https://api.replicate.com/v1/predictions"
            headers = {
                "Authorization": f"Token {self.replicate_api_key}",
                "Content-Type": "application/json"
            }
            
            # Detectar si el prompt es para personas y usar el modelo apropiado
            is_person_prompt = any(keyword in prompt.lower() for keyword in [
                'person', 'man', 'woman', 'people', 'human', 'face', 'portrait',
                'businessman', 'entrepreneur', 'influencer', 'speaker', 'trader'
            ])
            
            if is_person_prompt:
                # Usar Flux para personas realistas
                model_version = "black-forest-labs/flux-schnell"
                enhanced_prompt = self._enhance_person_prompt(prompt)
                data = {
                    "version": "f2ab8a5569070ad0648a80978e3a4d4e9e2e8e9e",  # Flux Schnell
                    "input": {
                        "prompt": enhanced_prompt,
                        "width": 1080,
                        "height": 1920,  # Formato Instagram
                        "num_outputs": 1,
                        "num_inference_steps": 4,  # Flux Schnell es rápido
                        "guidance_scale": 3.5
                    }
                }
            else:
                # Usar SDXL para objetos y paisajes
                data = {
                    "version": "ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",  # SDXL
                    "input": {
                        "prompt": prompt,
                        "width": 1080,
                        "height": 1920,  # Formato Instagram
                        "num_outputs": 1,
                        "scheduler": "K_EULER",
                        "num_inference_steps": 20,
                        "guidance_scale": 7.5
                    }
                }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 201:
                prediction = response.json()
                prediction_id = prediction['id']
                
                # Esperar a que se complete la generación
                for _ in range(30):  # Máximo 30 intentos (5 minutos)
                    time.sleep(10)
                    
                    status_response = requests.get(
                        f"https://api.replicate.com/v1/predictions/{prediction_id}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data['status'] == 'succeeded':
                            image_url = status_data['output'][0]
                            image_path = self._download_image(image_url, 'replicate')
                            return True, image_path, image_url, "Replicate (SDXL)"
                        
                        elif status_data['status'] == 'failed':
                            return False, "", "", "Replicate Failed"
                
                return False, "", "", "Replicate Timeout"
            else:
                return False, "", "", f"Replicate Error: {response.status_code}"
        
        except Exception as e:
            print(f"Error con Replicate: {str(e)}")
            return False, "", "", f"Replicate Exception: {str(e)}"
    
    def _enhance_person_prompt(self, base_prompt: str) -> str:
        """Mejorar prompts específicamente para generar personas realistas"""
        
        # Términos de calidad para personas realistas
        quality_terms = [
            "photorealistic",
            "high quality portrait",
            "professional photography",
            "8K resolution",
            "detailed facial features",
            "natural lighting",
            "sharp focus",
            "cinematic composition"
        ]
        
        # Términos de estilo para Instagram
        instagram_style = [
            "Instagram style",
            "social media ready",
            "modern aesthetic",
            "trendy",
            "lifestyle photography"
        ]
        
        # Términos para evitar problemas
        safe_terms = [
            "appropriate clothing",
            "professional appearance",
            "business appropriate",
            "clean background"
        ]
        
        # Construir prompt mejorado
        enhanced_parts = [base_prompt]
        enhanced_parts.extend(quality_terms[:3])  # Agregar 3 términos de calidad
        enhanced_parts.extend(instagram_style[:2])  # Agregar 2 términos de Instagram
        enhanced_parts.extend(safe_terms[:2])  # Agregar términos seguros
        
        return ", ".join(enhanced_parts)
    
    def _generate_with_deepai(self, prompt: str) -> Tuple[bool, str, str, str]:
        """Generar imagen con DeepAI"""
        try:
            url = "https://api.deepai.org/api/text2img"
            headers = {"api-key": self.deepai_api_key}
            data = {"text": prompt}
            
            response = requests.post(url, headers=headers, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                image_url = result['output_url']
                image_path = self._download_image(image_url, 'deepai')
                return True, image_path, image_url, "DeepAI"
            else:
                return False, "", "", f"DeepAI Error: {response.status_code}"
        
        except Exception as e:
            print(f"Error con DeepAI: {str(e)}")
            return False, "", "", f"DeepAI Exception: {str(e)}"
    
    def _generate_with_getimg(self, prompt: str) -> Tuple[bool, str, str, str]:
        """Generar imagen con GetImg.ai"""
        try:
            url = "https://api.getimg.ai/v1/stable-diffusion/text-to-image"
            headers = {
                "Authorization": f"Bearer {self.getimg_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "model": "stable-diffusion-v1-5",
                "width": 1024,
                "height": 1024,
                "steps": 20,
                "guidance": 7.5
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # GetImg devuelve imagen en base64
                image_data = base64.b64decode(result['image'])
                image_path = self._save_image_data(image_data, 'getimg')
                return True, image_path, "", "GetImg.ai"
            else:
                return False, "", "", f"GetImg Error: {response.status_code}"
        
        except Exception as e:
            print(f"Error con GetImg: {str(e)}")
            return False, "", "", f"GetImg Exception: {str(e)}"
    
    def _download_image(self, image_url: str, api_name: str) -> str:
        """Descargar imagen desde URL"""
        try:
            response = requests.get(image_url, timeout=30)
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"image_{api_name}_{timestamp}.jpg"
                image_path = self.images_dir / filename
                
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                
                return str(image_path)
            else:
                return ""
        
        except Exception as e:
            print(f"Error descargando imagen: {str(e)}")
            return ""
    
    def _save_image_data(self, image_data: bytes, api_name: str) -> str:
        """Guardar datos de imagen"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"image_{api_name}_{timestamp}.jpg"
            image_path = self.images_dir / filename
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            return str(image_path)
        
        except Exception as e:
            print(f"Error guardando imagen: {str(e)}")
            return ""
    
    def _create_placeholder_image(self, style: str) -> str:
        """Crear imagen placeholder atractiva cuando las APIs fallan"""
        try:
            # Intentar importar PIL, instalarlo si no está disponible
            try:
                from PIL import Image, ImageDraw, ImageFont, ImageFilter
            except ImportError:
                # Intentar instalar PIL automáticamente
                from utils.dependency_manager import dependency_manager
                success, message = dependency_manager.check_and_install_package('PIL', 'pillow')
                if success:
                    from PIL import Image, ImageDraw, ImageFont, ImageFilter
                else:
                    raise ImportError(f"No se pudo instalar PIL: {message}")
            
            import math
            
            # Crear imagen de 1080x1920 (formato Instagram Stories/Reels)
            img = Image.new('RGB', (1080, 1920), color='#000000')
            draw = ImageDraw.Draw(img)
            
            # Configuraciones por estilo
            style_configs = {
                'luxury': {
                    'colors': ['#FFD700', '#FFA500', '#FF6B35', '#8B4513'],
                    'bg_colors': ['#1a1a2e', '#16213e', '#0f3460'],
                    'elements': ['💎', '🏆', '👑', '💰']
                },
                'crypto': {
                    'colors': ['#FF6B35', '#00D4FF', '#FFD700', '#32CD32'],
                    'bg_colors': ['#0a0a0a', '#1a1a2e', '#16213e'],
                    'elements': ['₿', '⚡', '🚀', '📈']
                },
                'business': {
                    'colors': ['#0066CC', '#4169E1', '#1E90FF', '#00BFFF'],
                    'bg_colors': ['#1a1a2e', '#2c3e50', '#34495e'],
                    'elements': ['📊', '💼', '🏢', '📈']
                },
                'lifestyle': {
                    'colors': ['#FF69B4', '#FF1493', '#DA70D6', '#BA55D3'],
                    'bg_colors': ['#2c1810', '#3d2817', '#4a321c'],
                    'elements': ['✨', '🌟', '💫', '🎯']
                },
                'motivation': {
                    'colors': ['#32CD32', '#00FF7F', '#ADFF2F', '#7FFF00'],
                    'bg_colors': ['#1a2e1a', '#2e4a2e', '#3d5a3d'],
                    'elements': ['🔥', '💪', '🎯', '🏆']
                }
            }
            
            config = style_configs.get(style, style_configs['luxury'])
            
            # Crear gradiente de fondo dinámico
            self._create_dynamic_gradient(draw, config['bg_colors'])
            
            # Agregar elementos geométricos animados
            self._add_geometric_elements(draw, config['colors'])
            
            # Agregar partículas flotantes
            self._add_floating_particles(draw, config['colors'][0])
            
            # Agregar texto estilizado
            self._add_stylized_text(draw, style, config['colors'][0])
            
            # Guardar imagen
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dynamic_bg_{style}_{timestamp}.jpg"
            image_path = self.images_dir / filename
            
            img.save(image_path, 'JPEG', quality=95)
            return str(image_path)
        
        except ImportError:
            # Si PIL no está disponible, intentar instalarla automáticamente
            try:
                import subprocess
                subprocess.run(['pip', 'install', 'pillow'], check=True, capture_output=True)
                # Intentar de nuevo después de la instalación
                from PIL import Image, ImageDraw, ImageFont
                return self._create_placeholder_with_pil(style)
            except:
                return self._create_simple_placeholder(style)
        except Exception as e:
            print(f"Error creando placeholder dinámico: {str(e)}")
            return self._create_simple_placeholder(style)
    
    def _create_placeholder_with_pil(self, style: str) -> str:
        """Crear placeholder usando PIL después de instalación"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import math
            
            # Crear imagen de 1080x1920 (formato Instagram Stories/Reels)
            img = Image.new('RGB', (1080, 1920), color='#000000')
            draw = ImageDraw.Draw(img)
            
            # Configuraciones por estilo (simplificadas)
            style_configs = {
                'luxury': {'color': '#FFD700', 'bg': '#1a1a2e', 'name': 'LUXURY'},
                'crypto': {'color': '#FF6B35', 'bg': '#0a0a0a', 'name': 'CRYPTO'},
                'business': {'color': '#0066CC', 'bg': '#1a1a2e', 'name': 'BUSINESS'},
                'lifestyle': {'color': '#FF69B4', 'bg': '#2c1810', 'name': 'LIFESTYLE'},
                'motivation': {'color': '#32CD32', 'bg': '#1a2e1a', 'name': 'SUCCESS'}
            }
            
            config = style_configs.get(style, style_configs['luxury'])
            
            # Fondo con gradiente simple
            bg_color = tuple(int(config['bg'][i:i+2], 16) for i in (1, 3, 5))
            primary_color = tuple(int(config['color'][i:i+2], 16) for i in (1, 3, 5))
            
            # Crear gradiente
            for y in range(1920):
                alpha = y / 1920
                r = int(bg_color[0] + (primary_color[0] - bg_color[0]) * alpha * 0.3)
                g = int(bg_color[1] + (primary_color[1] - bg_color[1]) * alpha * 0.3)
                b = int(bg_color[2] + (primary_color[2] - bg_color[2]) * alpha * 0.3)
                draw.line([(0, y), (1080, y)], fill=(r, g, b))
            
            # Elementos decorativos
            draw.rectangle([50, 50, 1030, 1870], outline=primary_color, width=8)
            draw.ellipse([200, 400, 400, 600], outline=primary_color, width=5)
            draw.ellipse([680, 1200, 880, 1400], outline=primary_color, width=5)
            
            # Texto
            try:
                font_large = ImageFont.truetype("arial.ttf", 100)
            except:
                font_large = ImageFont.load_default()
            
            title = config['name']
            bbox = draw.textbbox((0, 0), title, font=font_large)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            
            # Sombra
            draw.text((x+4, 864), title, fill=(0, 0, 0), font=font_large)
            # Texto principal
            draw.text((x, 860), title, fill=primary_color, font=font_large)
            
            # Guardar imagen
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dynamic_bg_{style}_{timestamp}.jpg"
            image_path = self.images_dir / filename
            
            img.save(image_path, 'JPEG', quality=95)
            return str(image_path)
        
        except Exception as e:
            print(f"Error con PIL después de instalación: {e}")
            return self._create_simple_placeholder(style)
    
    def _create_dynamic_gradient(self, draw, bg_colors):
        """Crear gradiente dinámico de fondo"""
        import colorsys
        
        for y in range(1920):
            # Crear ondas en el gradiente
            wave1 = math.sin(y * 0.01) * 0.3
            wave2 = math.cos(y * 0.005) * 0.2
            
            # Interpolación entre colores
            progress = (y / 1920 + wave1 + wave2) % 1
            
            # Convertir hex a RGB
            color1 = tuple(int(bg_colors[0][i:i+2], 16) for i in (1, 3, 5))
            color2 = tuple(int(bg_colors[1][i:i+2], 16) for i in (1, 3, 5))
            
            # Interpolar colores
            r = int(color1[0] + (color2[0] - color1[0]) * progress)
            g = int(color1[1] + (color2[1] - color1[1]) * progress)
            b = int(color1[2] + (color2[2] - color1[2]) * progress)
            
            draw.line([(0, y), (1080, y)], fill=(r, g, b))
    
    def _add_geometric_elements(self, draw, colors):
        """Agregar elementos geométricos dinámicos"""
        import random
        
        # Círculos con gradiente
        for i in range(8):
            x = random.randint(50, 1030)
            y = random.randint(100, 1820)
            size = random.randint(30, 120)
            color = colors[i % len(colors)]
            
            # Convertir hex a RGB con transparencia
            rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            
            # Círculo principal
            draw.ellipse([x-size, y-size, x+size, y+size], outline=rgb, width=3)
            
            # Círculo interno
            inner_size = size // 2
            draw.ellipse([x-inner_size, y-inner_size, x+inner_size, y+inner_size], 
                        outline=rgb, width=2)
        
        # Líneas dinámicas
        for i in range(12):
            x1 = random.randint(0, 1080)
            y1 = random.randint(0, 1920)
            x2 = x1 + random.randint(-200, 200)
            y2 = y1 + random.randint(-200, 200)
            
            color = colors[i % len(colors)]
            rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            
            draw.line([(x1, y1), (x2, y2)], fill=rgb, width=2)
    
    def _add_floating_particles(self, draw, primary_color):
        """Agregar partículas flotantes"""
        import random
        
        rgb = tuple(int(primary_color[i:i+2], 16) for i in (1, 3, 5))
        
        for i in range(25):
            x = random.randint(0, 1080)
            y = random.randint(0, 1920)
            size = random.randint(2, 8)
            
            # Partícula principal
            draw.ellipse([x-size, y-size, x+size, y+size], fill=rgb)
            
            # Brillo alrededor
            glow_size = size + 2
            glow_color = tuple(min(255, c + 50) for c in rgb)
            draw.ellipse([x-glow_size, y-glow_size, x+glow_size, y+glow_size], 
                        outline=glow_color, width=1)
    
    def _add_stylized_text(self, draw, style, primary_color):
        """Agregar texto estilizado"""
        try:
            font_large = ImageFont.truetype("arial.ttf", 120)
            font_medium = ImageFont.truetype("arial.ttf", 60)
            font_small = ImageFont.truetype("arial.ttf", 40)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        rgb = tuple(int(primary_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Título principal
        style_names = {
            'luxury': 'LUXURY',
            'crypto': 'CRYPTO',
            'business': 'BUSINESS',
            'lifestyle': 'LIFESTYLE',
            'motivation': 'SUCCESS'
        }
        
        title = style_names.get(style, 'CONTENT')
        
        # Calcular posición centrada
        bbox = draw.textbbox((0, 0), title, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (1080 - text_width) // 2
        y = 860
        
        # Sombra del texto
        shadow_color = (0, 0, 0)
        draw.text((x+4, y+4), title, fill=shadow_color, font=font_large)
        
        # Texto principal
        draw.text((x, y), title, fill=rgb, font=font_large)
        
        # Subtítulo
        subtitle = "PREMIUM CONTENT"
        bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
        text_width = bbox[2] - bbox[0]
        x = (1080 - text_width) // 2
        y = 1000
        
        draw.text((x+2, y+2), subtitle, fill=shadow_color, font=font_medium)
        draw.text((x, y), subtitle, fill=(255, 255, 255), font=font_medium)
    
    def _create_simple_placeholder(self, style):
        """Crear placeholder simple si PIL no está disponible"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"placeholder_{style}_{timestamp}.txt"
        image_path = self.images_dir / filename
        
        with open(image_path, 'w', encoding='utf-8') as f:
            f.write(f"Fondo dinámico para: {style}\n")
            f.write(f"Creado: {datetime.now().isoformat()}\n")
            f.write("Para fondos reales, configura las APIs de IA en .env")
        
        return str(image_path)
    
    def create_animated_background_sequence(self, script: str, style: str = 'luxury', duration: int = 30) -> Tuple[bool, str, str]:
        """Crear secuencia de fondos animados"""
        try:
            # Generar múltiples fondos con variaciones
            backgrounds = []
            
            for i in range(5):  # 5 fondos diferentes
                # Crear variación del estilo
                variation_style = f"{style}_{i}"
                bg_path = self._create_placeholder_image(variation_style)
                if bg_path:
                    backgrounds.append(bg_path)
            
            if not backgrounds:
                return False, "No se pudieron crear fondos", "Error"
            
            # Crear video animado con transiciones
            if self._check_ffmpeg():
                success, result = self._create_animated_video(backgrounds, duration)
                if success:
                    return True, result, "FFmpeg Animated"
                else:
                    return True, backgrounds[0], "Static Fallback"
            else:
                # Fallback: devolver el primer fondo
                return True, backgrounds[0], "Static Background"
        
        except Exception as e:
            return False, f"Error creando secuencia animada: {str(e)}", "Exception"
    
    def _create_animated_video(self, backgrounds: List[str], duration: int) -> Tuple[bool, str]:
        """Crear video animado con transiciones"""
        try:
            import subprocess
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = str(self.images_dir.parent / f"animated_bg_{timestamp}.mp4")
            
            # Crear archivo de lista para FFmpeg
            list_file = str(self.images_dir / "bg_list.txt")
            
            segment_duration = duration / len(backgrounds)
            
            with open(list_file, 'w') as f:
                for bg in backgrounds:
                    f.write(f"file '{os.path.abspath(bg)}'\n")
                    f.write(f"duration {segment_duration}\n")
                # Repetir último frame
                f.write(f"file '{os.path.abspath(backgrounds[-1])}'\n")
            
            # Comando FFmpeg con transiciones suaves
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', list_file,
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fade=t=in:st=0:d=0.5,fade=t=out:st=' + str(duration-0.5) + ':d=0.5',
                '-c:v', 'libx264', '-r', '30', '-pix_fmt', 'yuv420p',
                '-t', str(duration), '-y', output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            # Limpiar archivo temporal
            if os.path.exists(list_file):
                os.remove(list_file)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return True, output_path
            else:
                return True, backgrounds[0]  # Fallback
        
        except Exception as e:
            return False, f"Error creando video animado: {str(e)}"
    
    def get_saved_images(self, limit: int = 10) -> List[Dict]:
        """Obtener imágenes guardadas"""
        images = []
        
        try:
            image_files = sorted(self.images_dir.glob("*.jpg"), key=os.path.getmtime, reverse=True)
            
            for image_file in image_files[:limit]:
                try:
                    stat = os.stat(image_file)
                    images.append({
                        'filename': image_file.name,
                        'path': str(image_file),
                        'size_mb': round(stat.st_size / (1024*1024), 2),
                        'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                
                except Exception as e:
                    print(f"Error leyendo imagen {image_file}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Error obteniendo imágenes guardadas: {str(e)}")
        
        return images
    
    def get_api_status(self) -> Dict:
        """Obtener estado de las APIs"""
        return {
            'replicate': {
                'configured': bool(self.replicate_api_key),
                'name': 'Replicate',
                'cost': 'GRATIS ($10 crédito/mes)',
                'quality': 'Alta'
            },
            'deepai': {
                'configured': bool(self.deepai_api_key),
                'name': 'DeepAI',
                'cost': 'GRATIS (con marca de agua)',
                'quality': 'Media'
            },
            'getimg': {
                'configured': bool(self.getimg_api_key),
                'name': 'GetImg.ai',
                'cost': 'GRATIS (100 imágenes/mes)',
                'quality': 'Alta'
            }
        }

# Crear instancia global
image_generator = AIImageGenerator()