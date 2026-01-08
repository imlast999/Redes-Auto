# -*- coding: utf-8 -*-
"""
Analizador de scripts con IA para extraer conceptos visuales
Genera prompts para imágenes basados en el contenido del guión
"""

import os
import re
import json
import requests
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class ScriptAnalyzer:
    def __init__(self):
        # APIs para análisis
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.cohere_api_key = os.getenv('COHERE_API_KEY', '')
    
    def analyze_script_for_visuals(self, script: str, video_duration: int = 60) -> Tuple[bool, List[Dict], str]:
        """
        Analiza un script y extrae conceptos visuales clave
        
        Args:
            script: El texto del guión
            video_duration: Duración del video en segundos
            
        Returns:
            (success, visual_concepts, api_used)
        """
        
        # Calcular cuántas imágenes necesitamos (cambio cada 8-10 segundos)
        num_images = max(3, video_duration // 8)
        
        # Crear prompt para análisis visual
        analysis_prompt = f"""
Analiza este script para video de Instagram y extrae {num_images} conceptos visuales clave que representen diferentes momentos del contenido.

SCRIPT:
{script}

Para cada concepto visual, proporciona:
1. MOMENTO: En qué segundo del video (0-{video_duration})
2. CONCEPTO: Descripción visual específica
3. ESTILO: Tipo de imagen (realista, minimalista, abstracto, etc.)
4. PROMPT_EN: Prompt en inglés para generar la imagen
5. EMOCIÓN: Qué emoción debe transmitir

Formato de respuesta:
VISUAL_1:
MOMENTO: 0-8
CONCEPTO: [descripción del concepto visual]
ESTILO: [estilo de imagen]
PROMPT_EN: [prompt detallado en inglés para IA]
EMOCIÓN: [emoción a transmitir]

VISUAL_2:
MOMENTO: 8-16
CONCEPTO: [descripción del concepto visual]
ESTILO: [estilo de imagen]
PROMPT_EN: [prompt detallado en inglés para IA]
EMOCIÓN: [emoción a transmitir]

[continuar hasta VISUAL_{num_images}]

REGLAS:
- Los prompts deben ser específicos y detallados
- Evitar texto en las imágenes
- Enfocar en conceptos visuales que complementen el audio
- Usar estilos modernos y atractivos para redes sociales
- Cada imagen debe ser única y diferente
"""

        # Intentar análisis con diferentes APIs
        analysis_result = None
        api_used = None
        
        if self.groq_api_key:
            analysis_result, api_used = self._analyze_with_groq(analysis_prompt)
        
        if not analysis_result and self.huggingface_api_key:
            analysis_result, api_used = self._analyze_with_huggingface(analysis_prompt)
        
        if not analysis_result and self.cohere_api_key:
            analysis_result, api_used = self._analyze_with_cohere(analysis_prompt)
        
        if not analysis_result:
            # Fallback: análisis básico
            analysis_result, api_used = self._analyze_fallback(script, num_images)
        
        # Parsear el resultado
        visual_concepts = self._parse_visual_analysis(analysis_result, video_duration)
        
        return True, visual_concepts, api_used
    
    def _analyze_with_groq(self, prompt: str) -> Tuple[Optional[str], str]:
        """Analizar con API de Groq"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "Eres un experto en análisis visual y creación de contenido para redes sociales. Tu trabajo es extraer conceptos visuales clave de scripts para crear imágenes impactantes."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content'].strip()
                return analysis, "Groq (Llama 3.1)"
            else:
                print(f"Error Groq análisis: {response.status_code}")
                return None, "Groq Error"
        
        except Exception as e:
            print(f"Error con Groq análisis: {str(e)}")
            return None, "Groq Exception"
    
    def _analyze_with_huggingface(self, prompt: str) -> Tuple[Optional[str], str]:
        """Analizar con API de Hugging Face"""
        try:
            # Usar modelo de análisis de texto
            model = "facebook/bart-large-cnn"
            url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "min_length": 100,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    analysis = result[0].get('summary_text', '').strip()
                    return analysis, "Hugging Face (BART)"
                else:
                    return None, "Hugging Face Empty"
            else:
                print(f"Error Hugging Face análisis: {response.status_code}")
                return None, "Hugging Face Error"
        
        except Exception as e:
            print(f"Error con Hugging Face análisis: {str(e)}")
            return None, "Hugging Face Exception"
    
    def _analyze_with_cohere(self, prompt: str) -> Tuple[Optional[str], str]:
        """Analizar con API de Cohere"""
        try:
            url = "https://api.cohere.ai/v1/generate"
            headers = {
                "Authorization": f"Bearer {self.cohere_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "command",
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.7,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['generations'][0]['text'].strip()
                return analysis, "Cohere (Command)"
            else:
                print(f"Error Cohere análisis: {response.status_code}")
                return None, "Cohere Error"
        
        except Exception as e:
            print(f"Error con Cohere análisis: {str(e)}")
            return None, "Cohere Exception"
    
    def _analyze_fallback(self, script: str, num_images: int) -> Tuple[str, str]:
        """Análisis de fallback cuando las APIs fallan"""
        
        # Palabras clave para diferentes tipos de contenido (ACTUALIZADAS para personas realistas)
        keywords_mapping = {
            'éxito': 'successful confident businessman in expensive suit, luxury office background, photorealistic portrait',
            'dinero': 'wealthy entrepreneur counting money, professional attire, modern office setting, realistic photography',
            'inversión': 'professional financial advisor analyzing charts, business suit, confident expression, high-end office',
            'crypto': 'young crypto trader with multiple monitors, modern workspace, successful millionaire, realistic portrait',
            'lujo': 'elegant wealthy person in luxury environment, expensive clothing, confident posture, premium lifestyle',
            'negocio': 'charismatic business leader in boardroom, professional suit, leadership presence, corporate success',
            'mentalidad': 'motivational speaker with confident expression, professional appearance, inspiring presence',
            'riqueza': 'successful millionaire in luxury setting, expensive watch and suit, confident wealthy person',
            'futuro': 'tech entrepreneur in modern office, innovative leader, forward-thinking professional',
            'oportunidad': 'ambitious young professional seizing opportunity, confident expression, success-oriented person'
        }
        
        # Extraer palabras clave del script
        script_lower = script.lower()
        found_keywords = []
        
        for keyword, visual_prompt in keywords_mapping.items():
            if keyword in script_lower:
                found_keywords.append((keyword, visual_prompt))
        
        # Si no encontramos palabras clave específicas, usar personas por defecto
        if not found_keywords:
            found_keywords = [
                ('motivación', 'charismatic motivational speaker, confident expression, professional attire, inspiring presence'),
                ('éxito', 'successful entrepreneur in luxury office, expensive suit, confident posture, wealthy lifestyle'),
                ('crecimiento', 'ambitious young professional, modern business environment, success-oriented person')
            ]
        
        # Generar conceptos visuales
        analysis_result = ""
        duration_per_image = 60 // num_images
        
        for i in range(num_images):
            keyword_idx = i % len(found_keywords)
            keyword, base_prompt = found_keywords[keyword_idx]
            
            start_time = i * duration_per_image
            end_time = min((i + 1) * duration_per_image, 60)
            
            # Variar el estilo para cada imagen
            styles = ['cinematic', 'minimalist', 'abstract', 'realistic', 'artistic']
            style = styles[i % len(styles)]
            
            emotions = ['inspiring', 'powerful', 'confident', 'ambitious', 'successful']
            emotion = emotions[i % len(emotions)]
            
            analysis_result += f"""VISUAL_{i+1}:
MOMENTO: {start_time}-{end_time}
CONCEPTO: Imagen relacionada con {keyword}
ESTILO: {style}
PROMPT_EN: {base_prompt}, {style} style, high quality, professional
EMOCIÓN: {emotion}

"""
        
        return analysis_result, "Fallback Analyzer"
    
    def _parse_visual_analysis(self, analysis_text: str, video_duration: int) -> List[Dict]:
        """Parsear el análisis visual en estructura de datos"""
        visual_concepts = []
        
        # Dividir por "VISUAL_X:"
        visual_parts = re.split(r'VISUAL_\d+:', analysis_text)
        
        for i, part in enumerate(visual_parts[1:], 1):  # Saltar la primera parte vacía
            concept = self._parse_single_visual(part, i, video_duration)
            if concept:
                visual_concepts.append(concept)
        
        # Si no se parseó correctamente, crear conceptos básicos
        if not visual_concepts:
            visual_concepts = self._create_basic_concepts(video_duration)
        
        return visual_concepts
    
    def _parse_single_visual(self, visual_text: str, index: int, video_duration: int) -> Optional[Dict]:
        """Parsear un concepto visual individual"""
        try:
            lines = visual_text.strip().split('\n')
            concept = {
                'id': index,
                'start_time': 0,
                'end_time': 10,
                'concept': '',
                'style': 'cinematic',
                'prompt_en': '',
                'emotion': 'inspiring'
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('MOMENTO:'):
                    # Extraer tiempos
                    time_part = line.replace('MOMENTO:', '').strip()
                    if '-' in time_part:
                        start, end = time_part.split('-')
                        concept['start_time'] = int(start.strip())
                        concept['end_time'] = int(end.strip())
                
                elif line.startswith('CONCEPTO:'):
                    concept['concept'] = line.replace('CONCEPTO:', '').strip()
                
                elif line.startswith('ESTILO:'):
                    concept['style'] = line.replace('ESTILO:', '').strip()
                
                elif line.startswith('PROMPT_EN:'):
                    concept['prompt_en'] = line.replace('PROMPT_EN:', '').strip()
                
                elif line.startswith('EMOCIÓN:'):
                    concept['emotion'] = line.replace('EMOCIÓN:', '').strip()
            
            # Validar que tenemos los datos mínimos
            if concept['prompt_en']:
                return concept
            else:
                return None
        
        except Exception as e:
            print(f"Error parseando concepto visual: {str(e)}")
            return None
    
    def _create_basic_concepts(self, video_duration: int) -> List[Dict]:
        """Crear conceptos visuales básicos como fallback"""
        num_concepts = max(3, video_duration // 10)
        duration_per_concept = video_duration // num_concepts
        
        basic_concepts = [
            {
                'concept': 'Éxito y ambición',
                'prompt_en': 'successful businessman in modern office, cinematic lighting, professional style',
                'style': 'cinematic',
                'emotion': 'ambitious'
            },
            {
                'concept': 'Crecimiento financiero',
                'prompt_en': 'golden coins and growth charts, luxury style, warm lighting',
                'style': 'luxury',
                'emotion': 'confident'
            },
            {
                'concept': 'Futuro próspero',
                'prompt_en': 'futuristic cityscape at sunset, inspiring view, cinematic style',
                'style': 'futuristic',
                'emotion': 'inspiring'
            },
            {
                'concept': 'Mentalidad ganadora',
                'prompt_en': 'abstract brain with golden connections, digital art style',
                'style': 'abstract',
                'emotion': 'powerful'
            },
            {
                'concept': 'Oportunidades',
                'prompt_en': 'open door with bright light, symbolic art, dramatic lighting',
                'style': 'symbolic',
                'emotion': 'hopeful'
            }
        ]
        
        concepts = []
        for i in range(num_concepts):
            concept_template = basic_concepts[i % len(basic_concepts)]
            
            concepts.append({
                'id': i + 1,
                'start_time': i * duration_per_concept,
                'end_time': min((i + 1) * duration_per_concept, video_duration),
                'concept': concept_template['concept'],
                'style': concept_template['style'],
                'prompt_en': concept_template['prompt_en'],
                'emotion': concept_template['emotion']
            })
        
        return concepts
    
    def save_analysis(self, script: str, visual_concepts: List[Dict], api_used: str) -> str:
        """Guardar análisis visual en archivo"""
        try:
            from pathlib import Path
            
            # Crear directorio si no existe
            analysis_dir = Path('generated/analysis')
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"visual_analysis_{timestamp}.json"
            file_path = analysis_dir / filename
            
            # Datos del análisis
            analysis_data = {
                'script': script,
                'visual_concepts': visual_concepts,
                'api_used': api_used,
                'created_at': datetime.now().isoformat(),
                'total_concepts': len(visual_concepts)
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
        
        except Exception as e:
            print(f"Error guardando análisis: {str(e)}")
            return ""

# Crear instancia global
script_analyzer = ScriptAnalyzer()