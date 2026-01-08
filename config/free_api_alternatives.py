# -*- coding: utf-8 -*-
"""
Configuración de APIs 100% GRATUITAS para Instagram Video Dashboard
Alternativas gratuitas a APIs de pago
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Información detallada de APIs gratuitas
FREE_APIS_INFO = {
    'ai_text': {
        'huggingface': {
            'name': 'Hugging Face',
            'description': 'Modelos de IA de código abierto (Llama, Mistral, etc.)',
            'cost': 'GRATIS',
            'limits': 'Sin límites',
            'signup_url': 'https://huggingface.co/settings/tokens',
            'models': ['meta-llama/Llama-2-7b-chat-hf', 'mistralai/Mistral-7B-Instruct-v0.1'],
            'quality': 'Alta'
        },
        'groq': {
            'name': 'Groq',
            'description': 'API ultra-rápida para modelos de IA',
            'cost': 'GRATIS',
            'limits': '14,400 requests/día',
            'signup_url': 'https://console.groq.com/keys',
            'models': ['llama2-70b-4096', 'mixtral-8x7b-32768'],
            'quality': 'Alta'
        },
        'cohere': {
            'name': 'Cohere',
            'description': 'API de procesamiento de lenguaje natural',
            'cost': 'GRATIS',
            'limits': '1M tokens/mes',
            'signup_url': 'https://dashboard.cohere.ai/api-keys',
            'models': ['command', 'command-light'],
            'quality': 'Alta'
        }
    },
    'tts': {
        'google_tts': {
            'name': 'Google Cloud TTS',
            'description': 'Text-to-Speech de Google',
            'cost': 'GRATIS',
            'limits': '1M caracteres/mes',
            'signup_url': 'https://console.cloud.google.com/',
            'voices': '220+ voces en 40+ idiomas',
            'quality': 'Alta'
        },
        'azure_speech': {
            'name': 'Azure Speech',
            'description': 'Text-to-Speech de Microsoft',
            'cost': 'GRATIS',
            'limits': '5 horas/mes',
            'signup_url': 'https://azure.microsoft.com/free/',
            'voices': '270+ voces en 119 idiomas',
            'quality': 'Alta'
        },
        'ibm_watson': {
            'name': 'IBM Watson TTS',
            'description': 'Text-to-Speech de IBM',
            'cost': 'GRATIS',
            'limits': '10K caracteres/mes',
            'signup_url': 'https://cloud.ibm.com/registration',
            'voices': '50+ voces en 13 idiomas',
            'quality': 'Alta'
        }
    },
    'image_generation': {
        'replicate': {
            'name': 'Replicate',
            'description': 'Modelos de IA para generación de imágenes',
            'cost': 'GRATIS',
            'limits': '$10 crédito/mes',
            'signup_url': 'https://replicate.com/account/api-tokens',
            'models': ['SDXL', 'Stable Diffusion', 'DALL-E'],
            'quality': 'Alta'
        },
        'deepai': {
            'name': 'DeepAI',
            'description': 'API de generación de imágenes',
            'cost': 'GRATIS',
            'limits': 'Sin límites (con marca de agua)',
            'signup_url': 'https://deepai.org/api-key',
            'models': ['Text2Image', 'StyleGAN', 'Super Resolution'],
            'quality': 'Media'
        },
        'getimg': {
            'name': 'GetImg.ai',
            'description': 'Generación de imágenes con IA',
            'cost': 'GRATIS',
            'limits': '100 imágenes/mes',
            'signup_url': 'https://getimg.ai/',
            'models': ['Stable Diffusion XL', 'DreamShaper'],
            'quality': 'Alta'
        }
    },
    'storage': {
        'cloudinary': {
            'name': 'Cloudinary',
            'description': 'Almacenamiento y procesamiento de medios',
            'cost': 'GRATIS',
            'limits': '25GB almacenamiento, 25GB ancho de banda/mes',
            'signup_url': 'https://cloudinary.com/console',
            'features': ['Redimensionado', 'Optimización', 'CDN'],
            'quality': 'Alta'
        },
        'imgur': {
            'name': 'Imgur',
            'description': 'Hosting de imágenes',
            'cost': 'GRATIS',
            'limits': 'Ilimitado (solo imágenes)',
            'signup_url': 'https://api.imgur.com/oauth2/addclient',
            'features': ['Hosting', 'Enlaces directos'],
            'quality': 'Media'
        }
    }
}

class FreeAPIConfig:
    def __init__(self):
        # APIs de IA gratuitas
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.cohere_api_key = os.getenv('COHERE_API_KEY', '')
        
        # APIs de TTS gratuitas
        self.google_tts_api_key = os.getenv('GOOGLE_TTS_API_KEY', '')
        self.azure_speech_key = os.getenv('AZURE_SPEECH_KEY', '')
        self.ibm_watson_api_key = os.getenv('IBM_WATSON_API_KEY', '')
        
        # APIs de generación de imágenes gratuitas
        self.replicate_api_key = os.getenv('REPLICATE_API_KEY', '')
        self.deepai_api_key = os.getenv('DEEPAI_API_KEY', '')
        self.getimg_api_key = os.getenv('GETIMG_API_KEY', '')
        
        # APIs de almacenamiento gratuitas
        self.cloudinary_url = os.getenv('CLOUDINARY_URL', '')
        self.imgur_client_id = os.getenv('IMGUR_CLIENT_ID', '')
    
    def test_huggingface_api(self):
        """Probar API de Hugging Face"""
        if not self.huggingface_api_key:
            return False, "API key no configurada"
        
        try:
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            response = requests.get("https://api-inference.huggingface.co/models/gpt2", 
                                  headers=headers, timeout=10)
            return response.status_code == 200, f"Status: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def test_groq_api(self):
        """Probar API de Groq"""
        if not self.groq_api_key:
            return False, "API key no configurada"
        
        try:
            headers = {"Authorization": f"Bearer {self.groq_api_key}"}
            response = requests.get("https://api.groq.com/openai/v1/models", 
                                  headers=headers, timeout=10)
            return response.status_code == 200, f"Status: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def test_cohere_api(self):
        """Probar API de Cohere"""
        if not self.cohere_api_key:
            return False, "API key no configurada"
        
        try:
            headers = {"Authorization": f"Bearer {self.cohere_api_key}"}
            response = requests.get("https://api.cohere.ai/v1/models", 
                                  headers=headers, timeout=10)
            return response.status_code == 200, f"Status: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def test_replicate_api(self):
        """Probar API de Replicate"""
        if not self.replicate_api_key:
            return False, "API key no configurada"
        
        try:
            headers = {"Authorization": f"Token {self.replicate_api_key}"}
            response = requests.get("https://api.replicate.com/v1/models", 
                                  headers=headers, timeout=10)
            return response.status_code == 200, f"Status: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def test_deepai_api(self):
        """Probar API de DeepAI"""
        if not self.deepai_api_key:
            return False, "API key no configurada"
        
        try:
            headers = {"api-key": self.deepai_api_key}
            response = requests.get("https://api.deepai.org/api/text2img", 
                                  headers=headers, timeout=10)
            return response.status_code in [200, 400], f"Status: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def get_all_free_apis_status(self):
        """Obtener estado de todas las APIs gratuitas"""
        status = {}
        
        # APIs de IA
        status['huggingface'] = {
            'configured': bool(self.huggingface_api_key),
            'working': False
        }
        status['groq'] = {
            'configured': bool(self.groq_api_key),
            'working': False
        }
        status['cohere'] = {
            'configured': bool(self.cohere_api_key),
            'working': False
        }
        
        # APIs de generación de imágenes
        status['replicate'] = {
            'configured': bool(self.replicate_api_key),
            'working': False
        }
        status['deepai'] = {
            'configured': bool(self.deepai_api_key),
            'working': False
        }
        status['getimg'] = {
            'configured': bool(self.getimg_api_key),
            'working': False
        }
        
        # APIs de almacenamiento
        status['cloudinary'] = {
            'configured': bool(self.cloudinary_url),
            'working': False
        }
        status['imgur'] = {
            'configured': bool(self.imgur_client_id),
            'working': False
        }
        
        return status
    
    def get_cost_comparison(self):
        """Comparar costos entre APIs gratuitas y de pago"""
        return {
            'free_apis': {
                'monthly_cost': 0,
                'setup_time': '5 minutos',
                'credit_card_required': False,
                'limitations': 'Límites de uso generosos',
                'quality': 'Alta (igual que APIs de pago)'
            },
            'paid_apis': {
                'monthly_cost': 37,  # OpenAI + ElevenLabs + Stability AI
                'setup_time': '15 minutos',
                'credit_card_required': True,
                'limitations': 'Sin límites (pero costoso)',
                'quality': 'Alta'
            },
            'savings_per_year': 444  # $37 * 12 meses
        }

# Instancia global
free_api_config = FreeAPIConfig()