# -*- coding: utf-8 -*-
"""
Gestor de múltiples APIs para Instagram Video Dashboard
Rota automáticamente entre diferentes APIs para cada tarea
"""

import os
import random
import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class MultiAPIManager:
    def __init__(self):
        # APIs para generación de scripts
        self.script_apis = {
            'groq': {
                'name': 'Groq (Llama)',
                'api_key': os.getenv('GROQ_API_KEY', ''),
                'endpoint': 'https://api.groq.com/openai/v1/chat/completions',
                'model': 'llama2-70b-4096',
                'active': True,
                'priority': 1
            },
            'huggingface': {
                'name': 'Hugging Face',
                'api_key': os.getenv('HUGGINGFACE_API_KEY', ''),
                'endpoint': 'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
                'model': 'microsoft/DialoGPT-medium',
                'active': True,
                'priority': 2
            },
            'cohere': {
                'name': 'Cohere',
                'api_key': os.getenv('COHERE_API_KEY', ''),
                'endpoint': 'https://api.cohere.ai/v1/chat',
                'model': 'command',
                'active': True,
                'priority': 3
            },
            'openai': {
                'name': 'OpenAI (Premium)',
                'api_key': os.getenv('OPENAI_API_KEY', ''),
                'endpoint': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-3.5-turbo',
                'active': True,
                'priority': 4
            }
        }
        
        # APIs para generación de imágenes
        self.image_apis = {
            'replicate': {
                'name': 'Replicate (SDXL)',
                'api_key': os.getenv('REPLICATE_API_KEY', ''),
                'endpoint': 'https://api.replicate.com/v1/predictions',
                'model': 'stability-ai/sdxl',
                'active': True,
                'priority': 1
            },
            'deepai': {
                'name': 'DeepAI',
                'api_key': os.getenv('DEEPAI_API_KEY', ''),
                'endpoint': 'https://api.deepai.org/api/text2img',
                'model': 'text2img',
                'active': True,
                'priority': 2
            },
            'getimg': {
                'name': 'GetImg.ai',
                'api_key': os.getenv('GETIMG_API_KEY', ''),
                'endpoint': 'https://api.getimg.ai/v1/stable-diffusion/text-to-image',
                'model': 'stable-diffusion-v1-5',
                'active': True,
                'priority': 3
            },
            'stability': {
                'name': 'Stability AI (Premium)',
                'api_key': os.getenv('STABILITY_API_KEY', ''),
                'endpoint': 'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                'model': 'stable-diffusion-xl-1024-v1-0',
                'active': True,
                'priority': 4
            }
        }
        
        # APIs para TTS
        self.tts_apis = {
            'gtts': {
                'name': 'Google TTS (Free)',
                'api_key': 'local',
                'active': True,
                'priority': 1
            },
            'elevenlabs': {
                'name': 'ElevenLabs (Premium)',
                'api_key': os.getenv('ELEVENLABS_API_KEY', ''),
                'endpoint': 'https://api.elevenlabs.io/v1/text-to-speech',
                'active': True,
                'priority': 2
            },
            'azure': {
                'name': 'Azure Speech',
                'api_key': os.getenv('AZURE_SPEECH_KEY', ''),
                'endpoint': 'https://api.cognitive.microsoft.com/sts/v1.0/issuetoken',
                'active': True,
                'priority': 3
            }
        }
        
        # Estadísticas de uso
        self.usage_stats = {
            'script_apis': {},
            'image_apis': {},
            'tts_apis': {}
        }
    
    def get_available_apis(self, api_type: str) -> List[Dict]:
        """Obtener APIs disponibles para un tipo específico"""
        api_dict = getattr(self, f"{api_type}_apis", {})
        available = []
        
        for api_id, config in api_dict.items():
            if config['active'] and config.get('api_key'):
                available.append({
                    'id': api_id,
                    'name': config['name'],
                    'priority': config['priority'],
                    'configured': bool(config['api_key'] and config['api_key'] != '')
                })
        
        # Ordenar por prioridad
        available.sort(key=lambda x: x['priority'])
        return available
    
    def select_best_api(self, api_type: str, exclude: List[str] = None) -> Optional[Dict]:
        """Seleccionar la mejor API disponible para un tipo"""
        if exclude is None:
            exclude = []
        
        available = self.get_available_apis(api_type)
        
        # Filtrar APIs excluidas
        available = [api for api in available if api['id'] not in exclude and api['configured']]
        
        if not available:
            return None
        
        # Estrategia de selección: 70% mejor prioridad, 30% aleatorio
        if random.random() < 0.7:
            return available[0]  # Mejor prioridad
        else:
            return random.choice(available[:3])  # Top 3 aleatorio
    
    def generate_script_with_rotation(self, prompt: str, max_attempts: int = 3) -> Tuple[bool, str, str]:
        """Generar script rotando entre APIs disponibles"""
        attempted_apis = []
        
        for attempt in range(max_attempts):
            api_config = self.select_best_api('script', exclude=attempted_apis)
            
            if not api_config:
                break
            
            api_id = api_config['id']
            attempted_apis.append(api_id)
            
            try:
                success, result = self._call_script_api(api_id, prompt)
                
                if success:
                    self._update_usage_stats('script_apis', api_id, True)
                    return True, result, api_config['name']
                else:
                    self._update_usage_stats('script_apis', api_id, False)
                    print(f"API {api_config['name']} falló: {result}")
            
            except Exception as e:
                print(f"Error con API {api_config['name']}: {e}")
                self._update_usage_stats('script_apis', api_id, False)
        
        return False, "Todas las APIs de script fallaron", "None"
    
    def generate_image_with_rotation(self, prompt: str, style: str = 'luxury', max_attempts: int = 3) -> Tuple[bool, str, str, str]:
        """Generar imagen rotando entre APIs disponibles"""
        attempted_apis = []
        
        for attempt in range(max_attempts):
            api_config = self.select_best_api('image', exclude=attempted_apis)
            
            if not api_config:
                break
            
            api_id = api_config['id']
            attempted_apis.append(api_id)
            
            try:
                success, image_path, image_url = self._call_image_api(api_id, prompt, style)
                
                if success:
                    self._update_usage_stats('image_apis', api_id, True)
                    return True, image_path, image_url, api_config['name']
                else:
                    self._update_usage_stats('image_apis', api_id, False)
                    print(f"API {api_config['name']} falló: {image_path}")
            
            except Exception as e:
                print(f"Error con API {api_config['name']}: {e}")
                self._update_usage_stats('image_apis', api_id, False)
        
        return False, "Todas las APIs de imagen fallaron", "", "None"
    
    def _call_script_api(self, api_id: str, prompt: str) -> Tuple[bool, str]:
        """Llamar a una API específica de scripts"""
        config = self.script_apis[api_id]
        
        if api_id == 'groq':
            return self._call_groq_api(prompt, config)
        elif api_id == 'huggingface':
            return self._call_huggingface_api(prompt, config)
        elif api_id == 'cohere':
            return self._call_cohere_api(prompt, config)
        elif api_id == 'openai':
            return self._call_openai_api(prompt, config)
        
        return False, f"API {api_id} no implementada"
    
    def _call_image_api(self, api_id: str, prompt: str, style: str) -> Tuple[bool, str, str]:
        """Llamar a una API específica de imágenes"""
        config = self.image_apis[api_id]
        
        if api_id == 'replicate':
            return self._call_replicate_api(prompt, style, config)
        elif api_id == 'deepai':
            return self._call_deepai_api(prompt, style, config)
        elif api_id == 'getimg':
            return self._call_getimg_api(prompt, style, config)
        elif api_id == 'stability':
            return self._call_stability_api(prompt, style, config)
        
        return False, f"API {api_id} no implementada", ""
    
    def _call_groq_api(self, prompt: str, config: Dict) -> Tuple[bool, str]:
        """Llamar a la API de Groq"""
        try:
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-8b-8192",  # Modelo actualizado
                "messages": [
                    {"role": "system", "content": "Eres un experto en crear contenido viral para redes sociales."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(config['endpoint'], headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content'].strip()
                return True, script
            else:
                return False, f"Error HTTP {response.status_code}: {response.text}"
        
        except Exception as e:
            return False, str(e)
    
    def _call_deepai_api(self, prompt: str, style: str, config: Dict) -> Tuple[bool, str, str]:
        """Llamar a la API de DeepAI"""
        try:
            headers = {"api-key": config['api_key']}
            data = {"text": f"{prompt}, {style} style, high quality, professional"}
            
            response = requests.post(config['endpoint'], headers=headers, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                image_url = result['output_url']
                
                # Descargar imagen
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_path = f"generated/images/deepai_{style}_{timestamp}.jpg"
                    
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    with open(image_path, 'wb') as f:
                        f.write(image_response.content)
                    
                    return True, image_path, image_url
                else:
                    return False, "Error descargando imagen", ""
            else:
                return False, f"Error HTTP {response.status_code}", ""
        
        except Exception as e:
            return False, str(e), ""
    
    def _update_usage_stats(self, api_type: str, api_id: str, success: bool):
        """Actualizar estadísticas de uso de APIs"""
        if api_id not in self.usage_stats[api_type]:
            self.usage_stats[api_type][api_id] = {'success': 0, 'failed': 0, 'total': 0}
        
        self.usage_stats[api_type][api_id]['total'] += 1
        if success:
            self.usage_stats[api_type][api_id]['success'] += 1
        else:
            self.usage_stats[api_type][api_id]['failed'] += 1
    
    def get_usage_stats(self) -> Dict:
        """Obtener estadísticas de uso de todas las APIs"""
        return self.usage_stats
    
    def get_api_health(self) -> Dict:
        """Obtener estado de salud de todas las APIs"""
        health = {}
        
        for api_type in ['script', 'image', 'tts']:
            health[api_type] = {}
            available_apis = self.get_available_apis(api_type)
            
            for api in available_apis:
                api_id = api['id']
                stats = self.usage_stats.get(f"{api_type}_apis", {}).get(api_id, {})
                
                total = stats.get('total', 0)
                success = stats.get('success', 0)
                success_rate = (success / total * 100) if total > 0 else 0
                
                health[api_type][api_id] = {
                    'name': api['name'],
                    'configured': api['configured'],
                    'success_rate': round(success_rate, 1),
                    'total_calls': total
                }
        
        return health

# Instancia global
multi_api_manager = MultiAPIManager()