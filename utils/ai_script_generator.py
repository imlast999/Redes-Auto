# -*- coding: utf-8 -*-
"""
Generador de scripts con IA para Instagram Video Dashboard
Utiliza APIs gratuitas de IA para generar contenido
"""

import os
import requests
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

class AIScriptGenerator:
    def __init__(self):
        # APIs de IA gratuitas
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.cohere_api_key = os.getenv('COHERE_API_KEY', '')
        
        # Directorio para guardar scripts
        self.scripts_dir = Path('generated/scripts')
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Temas disponibles
        self.themes = {
            'mindset': {
                'name': 'Mindset de Lujo',
                'description': 'Mentalidad millonaria y éxito',
                'keywords': ['éxito', 'millonario', 'mentalidad', 'riqueza', 'lujo']
            },
            'investment': {
                'name': 'Inversiones',
                'description': 'Consejos de inversión y finanzas',
                'keywords': ['inversión', 'dinero', 'finanzas', 'crypto', 'bolsa']
            },
            'crypto': {
                'name': 'Criptomonedas',
                'description': 'Mundo crypto y blockchain',
                'keywords': ['bitcoin', 'crypto', 'blockchain', 'trading', 'NFT']
            },
            'business': {
                'name': 'Negocios',
                'description': 'Emprendimiento y negocios',
                'keywords': ['negocio', 'empresa', 'emprendedor', 'startup', 'CEO']
            },
            'lifestyle': {
                'name': 'Estilo de Vida',
                'description': 'Vida de lujo y exclusividad',
                'keywords': ['lujo', 'lifestyle', 'exclusivo', 'premium', 'élite']
            }
        }
        
        # Plantillas de prompts
        self.prompt_templates = {
            'mindset': """
Crea un script motivacional de 45-60 segundos sobre mentalidad millonaria.
Tema específico: {subtema}
Incluye:
- Hook potente en los primeros 3 segundos
- 3 puntos clave sobre mentalidad de éxito
- Call to action al final: {cta}
- Tono: Inspirador pero directo
- Estilo: Como si fueras un mentor millonario
""",
            'investment': """
Crea un script educativo de 45-60 segundos sobre inversiones.
Tema específico: {subtema}
Incluye:
- Dato impactante como hook
- 3 consejos prácticos de inversión
- Advertencia sobre riesgos
- Call to action: {cta}
- Tono: Profesional pero accesible
""",
            'crypto': """
Crea un script sobre criptomonedas de 45-60 segundos.
Tema específico: {subtema}
Incluye:
- Hook sobre oportunidad crypto
- Explicación simple de un concepto
- Perspectiva de futuro
- Call to action: {cta}
- Tono: Visionario pero realista
""",
            'business': """
Crea un script sobre negocios de 45-60 segundos.
Tema específico: {subtema}
Incluye:
- Historia de éxito como hook
- 3 lecciones de negocio
- Consejo actionable
- Call to action: {cta}
- Tono: Empresarial y motivador
""",
            'lifestyle': """
Crea un script sobre estilo de vida de lujo de 45-60 segundos.
Tema específico: {subtema}
Incluye:
- Descripción aspiracional como hook
- 3 elementos del lifestyle de élite
- Mensaje inspiracional
- Call to action: {cta}
- Tono: Aspiracional y exclusivo
"""
        }
    
    def is_configured(self):
        """Verificar si al menos una API está configurada"""
        return bool(self.huggingface_api_key or self.groq_api_key or self.cohere_api_key)
    
    def get_available_themes(self):
        """Obtener temas disponibles"""
        return self.themes
    
    def generate_multiple_scripts(self, topic: str, count: int = 5) -> Tuple[bool, List[Dict], str]:
        """Generar múltiples scripts para un tema libre"""
        
        # Crear prompt para generar múltiples scripts
        prompt = f"""
Crea {count} scripts diferentes para videos de Instagram sobre: {topic}

Cada script debe:
- Durar entre 45-60 segundos al leerlo
- Tener un hook potente en los primeros 3 segundos
- Incluir 3 puntos clave sobre el tema
- Ser inspirador y motivacional
- NO incluir call to action (se agregará después)
- NO usar emojis (se agregarán después)
- Ser único y diferente de los otros

Formato de respuesta:
SCRIPT 1:
[contenido del script 1]

SCRIPT 2:
[contenido del script 2]

[continuar hasta SCRIPT {count}]
"""
        
        # Intentar generar con múltiples APIs usando rotación
        scripts_text = None
        api_used = None
        
        try:
            from utils.multi_api_manager import multi_api_manager
            success, scripts_text, api_used = multi_api_manager.generate_script_with_rotation(prompt)
            
            if not success:
                # Fallback: usar APIs individuales
                if self.groq_api_key:
                    scripts_text, api_used = self._generate_with_groq(prompt)
                
                if not scripts_text and self.huggingface_api_key:
                    scripts_text, api_used = self._generate_with_huggingface(prompt)
                
                if not scripts_text and self.cohere_api_key:
                    scripts_text, api_used = self._generate_with_cohere(prompt)
        
        except ImportError:
            # Si no está disponible el gestor, usar método original
            if self.groq_api_key:
                scripts_text, api_used = self._generate_with_groq(prompt)
            
            if not scripts_text and self.huggingface_api_key:
                scripts_text, api_used = self._generate_with_huggingface(prompt)
            
            if not scripts_text and self.cohere_api_key:
                scripts_text, api_used = self._generate_with_cohere(prompt)
        
        if not scripts_text:
            # Fallback: scripts predefinidos
            scripts_text = self._get_fallback_multiple_scripts(topic, count)
            api_used = "Fallback"
        
        # Parsear los scripts
        scripts = self._parse_multiple_scripts(scripts_text, topic)
        
        # Guardar scripts
        scripts_file = self._save_multiple_scripts(scripts, topic, api_used)
        
        return True, scripts, scripts_file
    
    def _get_fallback_multiple_scripts(self, topic: str, count: int) -> str:
        """Generar múltiples scripts de fallback"""
        
        # Templates base para diferentes tipos de contenido
        templates = [
            # Template 1: Pregunta + Revelación
            """¿Sabías que {topic} puede cambiar completamente tu vida?

La mayoría de personas no entiende el verdadero poder de {topic}.

Mientras otros siguen haciendo lo mismo de siempre, las personas exitosas han descubierto estos secretos:

Primero, entienden que {topic} no es solo una tendencia, es el futuro.

Segundo, saben que la información correcta vale más que el oro.

Tercero, actúan mientras otros dudan.

El momento de actuar es ahora. ¿Estás listo para el cambio?""",

            # Template 2: Historia + Lección
            """Hace un año, pensaba que {topic} era solo para expertos.

Me equivocaba completamente.

Hoy quiero compartir contigo lo que he aprendido:

{topic} no es complicado si sabes por dónde empezar.

Los resultados llegan más rápido de lo que imaginas.

Pero hay un secreto que pocos conocen.

La diferencia entre el éxito y el fracaso está en la mentalidad.

Cambia tu perspectiva, cambia tu vida.""",

            # Template 3: Estadística + Oportunidad
            """El 95% de las personas nunca aprovecha las oportunidades de {topic}.

¿Por qué?

Porque esperan el momento perfecto que nunca llega.

Mientras tanto, el 5% que actúa está construyendo su futuro.

{topic} es más que una oportunidad, es una revolución.

Y las revoluciones no esperan a nadie.

La pregunta no es si vas a participar, sino cuándo vas a empezar.

El futuro pertenece a quienes se atreven a crearlo.""",

            # Template 4: Contraste + Revelación
            """Hay dos tipos de personas en el mundo de {topic}:

Los que hablan y los que hacen.

Los que hablan siempre tienen excusas.

Los que hacen siempre tienen resultados.

{topic} recompensa la acción, no las intenciones.

Cada día que pasa sin actuar es una oportunidad perdida.

Pero hoy puede ser diferente.

Hoy puedes elegir ser parte de la solución.""",

            # Template 5: Futuro + Urgencia
            """En 5 años, {topic} habrá cambiado el mundo.

Los que se preparen hoy serán los líderes del mañana.

Los que esperen serán espectadores.

{topic} no es solo una tendencia, es una transformación.

Y las transformaciones crean oportunidades únicas.

Pero estas oportunidades tienen fecha de caducidad.

El tren está saliendo de la estación.

¿Vas a subir o vas a quedarte en el andén?"""
        ]
        
        # Generar scripts usando los templates
        scripts_text = ""
        for i in range(min(count, len(templates))):
            script_content = templates[i].format(topic=topic)
            scripts_text += f"SCRIPT {i+1}:\n{script_content}\n\n"
        
        # Si necesitamos más scripts, reutilizar templates con variaciones
        if count > len(templates):
            for i in range(len(templates), count):
                template_idx = i % len(templates)
                script_content = templates[template_idx].format(topic=topic)
                # Agregar pequeña variación
                script_content = script_content.replace("¿Sabías que", "¿Sabías realmente que")
                scripts_text += f"SCRIPT {i+1}:\n{script_content}\n\n"
        
        return scripts_text
    
    def _parse_multiple_scripts(self, scripts_text: str, topic: str) -> List[Dict]:
        """Parsear múltiples scripts del texto generado"""
        scripts = []
        
        # Dividir por "SCRIPT X:"
        import re
        script_parts = re.split(r'SCRIPT \d+:', scripts_text)
        
        for i, part in enumerate(script_parts[1:], 1):  # Saltar la primera parte vacía
            script_content = part.strip()
            if script_content:
                scripts.append({
                    'id': i,
                    'title': f"Script {i} - {topic}",
                    'content': script_content,
                    'topic': topic,
                    'word_count': len(script_content.split()),
                    'char_count': len(script_content)
                })
        
        return scripts
    
    def _save_multiple_scripts(self, scripts: List[Dict], topic: str, api_used: str) -> str:
        """Guardar múltiples scripts en archivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"multiple_scripts_{topic.replace(' ', '_')}_{timestamp}.json"
            file_path = self.scripts_dir / filename
            
            # Metadata
            data = {
                'topic': topic,
                'api_used': api_used,
                'created_at': datetime.now().isoformat(),
                'scripts': scripts
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
        
        except Exception as e:
            print(f"Error guardando scripts múltiples: {str(e)}")
            return ""
    
    def generate_script(self, theme: str, subtema: str = "", cta: str = "t.me/tucanalgratis") -> Tuple[bool, str, str]:
        """Generar script individual (mantener compatibilidad)"""
        # Generar múltiples scripts y devolver el primero
        success, scripts, scripts_file = self.generate_multiple_scripts(theme, 1)
        
        if success and scripts:
            script_content = scripts[0]['content']
            # Agregar CTA al final si se proporciona
            if cta and cta.strip():
                script_content += f"\n\nÚnete a nuestra comunidad: {cta}"
            
            return True, script_content, scripts_file
        else:
            return False, "Error generando script", ""
    
    def _generate_subtema(self, theme: str) -> str:
        """Generar subtema aleatorio"""
        subtemas = {
            'mindset': [
                "Cómo pensar como millonario",
                "Hábitos de personas exitosas",
                "Mentalidad de abundancia vs escasez",
                "El poder de la visualización",
                "Cómo superar el miedo al fracaso"
            ],
            'investment': [
                "Diversificación de portafolio",
                "Inversión en bienes raíces",
                "Fondos indexados para principiantes",
                "Cómo evaluar una acción",
                "Inversión a largo plazo vs trading"
            ],
            'crypto': [
                "Bitcoin como reserva de valor",
                "DeFi y el futuro de las finanzas",
                "Cómo hacer HODL correctamente",
                "Altcoins con potencial",
                "Seguridad en wallets crypto"
            ],
            'business': [
                "Cómo validar una idea de negocio",
                "Escalabilidad en startups",
                "Networking efectivo",
                "Liderazgo en equipos remotos",
                "Monetización de audiencias"
            ],
            'lifestyle': [
                "Rutinas matutinas de millonarios",
                "Viajes de lujo exclusivos",
                "Inversión en experiencias",
                "Networking en círculos de élite",
                "Mentalidad de abundancia"
            ]
        }
        
        return random.choice(subtemas.get(theme, subtemas['mindset']))
    
    def _generate_with_groq(self, prompt: str) -> Tuple[Optional[str], str]:
        """Generar con API de Groq"""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "Eres un experto en crear contenido viral para redes sociales, especializado en temas de éxito, inversiones y lifestyle de lujo."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                script = result['choices'][0]['message']['content'].strip()
                return script, "Groq (Llama2-70B)"
            else:
                print(f"Error Groq: {response.status_code} - {response.text}")
                return None, "Groq Error"
        
        except Exception as e:
            print(f"Error con Groq: {str(e)}")
            return None, "Groq Exception"
    
    def _generate_with_huggingface(self, prompt: str) -> Tuple[Optional[str], str]:
        """Generar con API de Hugging Face"""
        try:
            # Usar modelo gratuito de Hugging Face
            model = "microsoft/DialoGPT-medium"
            url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    script = result[0].get('generated_text', '').strip()
                    return script, "Hugging Face (DialoGPT)"
                else:
                    return None, "Hugging Face Empty"
            else:
                print(f"Error Hugging Face: {response.status_code} - {response.text}")
                return None, "Hugging Face Error"
        
        except Exception as e:
            print(f"Error con Hugging Face: {str(e)}")
            return None, "Hugging Face Exception"
    
    def _generate_with_cohere(self, prompt: str) -> Tuple[Optional[str], str]:
        """Generar con API de Cohere"""
        try:
            url = "https://api.cohere.ai/v1/generate"
            headers = {
                "Authorization": f"Bearer {self.cohere_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "command",
                "prompt": prompt,
                "max_tokens": 500,
                "temperature": 0.7,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                script = result['generations'][0]['text'].strip()
                return script, "Cohere (Command)"
            else:
                print(f"Error Cohere: {response.status_code} - {response.text}")
                return None, "Cohere Error"
        
        except Exception as e:
            print(f"Error con Cohere: {str(e)}")
            return None, "Cohere Exception"
    
    def _get_fallback_script(self, theme: str, subtema: str, cta: str) -> str:
        """Script de respaldo cuando las APIs fallan"""
        # Usar subtema si se proporciona, sino usar uno por defecto
        if not subtema:
            subtema = self._generate_subtema(theme)
        
        fallback_scripts = {
            'mindset': f"""
🔥 ¿Sabes cuál es la diferencia entre un millonario y una persona promedio?

No es la suerte. No es el dinero inicial. Es la MENTALIDAD.

Los millonarios piensan en oportunidades mientras otros ven problemas.
Los millonarios invierten en su educación mientras otros gastan en entretenimiento.
Los millonarios construyen activos mientras otros acumulan pasivos.

{subtema} - Este es el secreto que cambió mi vida.

La riqueza comienza en tu mente. ¿Estás listo para cambiar la tuya?

💎 Únete a nuestra comunidad: {cta}
""",
            'investment': f"""
💰 DATO IMPACTANTE: El 90% de los millonarios tienen al menos 4 fuentes de ingresos.

¿Tú cuántas tienes?

Aquí tienes 3 reglas de oro para invertir como los ricos:

1️⃣ Diversifica SIEMPRE - Nunca pongas todos los huevos en una canasta
2️⃣ Piensa a LARGO PLAZO - La paciencia es tu mejor aliada
3️⃣ Invierte en lo que ENTIENDES - El conocimiento es poder

{subtema} - La clave está en empezar HOY, no mañana.

Recuerda: Los ricos invierten primero y gastan después. Los pobres gastan primero y nunca invierten.

📈 Aprende más estrategias: {cta}
""",
            'crypto': f"""
⚡ Bitcoin acaba de superar los $50,000 otra vez...

¿Te perdiste el tren? ¡Para nada!

Estamos apenas en el 1% de la adopción global. Piénsalo:
- Solo 100M de personas usan crypto
- Somos 8 mil millones en el planeta
- Las instituciones apenas están entrando

{subtema} - El futuro del dinero ya está aquí.

No se trata de hacerse rico rápido. Se trata de no quedarse pobre lentamente.

La pregunta no es SI crypto va a explotar, sino CUÁNDO vas a posicionarte.

🚀 Únete a la revolución: {cta}
""",
            'business': f"""
🏆 Jeff Bezos empezó Amazon en un garaje.
🏆 Steve Jobs empezó Apple en un garaje.
🏆 Google empezó en un garaje.

¿Ves el patrón?

No necesitas una oficina lujosa para construir un imperio. Necesitas:
- Una idea que resuelva un problema real
- La determinación para no rendirte
- La capacidad de adaptarte rápidamente

{subtema} - Este es el momento de actuar.

Mientras otros buscan excusas, los emprendedores buscan soluciones.

Tu próximo cliente está esperando. ¿Qué estás esperando tú?

💼 Construye tu imperio: {cta}
""",
            'lifestyle': f"""
✨ Despertar en una villa en Maldivas...
✨ Desayunar en la terraza de tu penthouse...
✨ Viajar en primera clase como si fuera normal...

¿Fantasía? Para algunos. Realidad para otros.

La diferencia no está en la suerte. Está en las decisiones que tomas HOY:
- Inviertes en ti mismo o en entretenimiento?
- Construyes activos o acumulas pasivos?
- Piensas en grande o te conformas con poco?

{subtema} - El lifestyle que mereces te está esperando.

La vida de lujo no es un destino, es una mentalidad.

🌟 Eleva tu estilo de vida: {cta}
"""
        }
        
        return fallback_scripts.get(theme, fallback_scripts['mindset'])
    
    def _save_script(self, script: str, theme: str, subtema: str, api_used: str) -> str:
        """Guardar script en archivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"script_{theme}_{timestamp}.txt"
            file_path = self.scripts_dir / filename
            
            # Metadata del script
            metadata = {
                'theme': theme,
                'subtema': subtema,
                'api_used': api_used,
                'created_at': datetime.now().isoformat(),
                'word_count': len(script.split()),
                'char_count': len(script)
            }
            
            # Guardar script con metadata
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# METADATA\n")
                f.write(f"# {json.dumps(metadata, indent=2)}\n\n")
                f.write(f"# SCRIPT\n")
                f.write(script)
            
            return str(file_path)
        
        except Exception as e:
            print(f"Error guardando script: {str(e)}")
            return ""
    
    def get_saved_scripts(self, limit: int = 10) -> List[Dict]:
        """Obtener scripts guardados"""
        scripts = []
        
        try:
            script_files = sorted(self.scripts_dir.glob("*.txt"), key=os.path.getmtime, reverse=True)
            
            for script_file in script_files[:limit]:
                try:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extraer metadata
                    if '# METADATA' in content:
                        metadata_start = content.find('{')
                        metadata_end = content.find('}') + 1
                        if metadata_start != -1 and metadata_end != -1:
                            metadata_str = content[metadata_start:metadata_end]
                            metadata = json.loads(metadata_str)
                            
                            # Extraer script
                            script_start = content.find('# SCRIPT\n') + len('# SCRIPT\n')
                            script_text = content[script_start:].strip()
                            
                            scripts.append({
                                'filename': script_file.name,
                                'path': str(script_file),
                                'metadata': metadata,
                                'preview': script_text[:100] + "..." if len(script_text) > 100 else script_text
                            })
                
                except Exception as e:
                    print(f"Error leyendo script {script_file}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Error obteniendo scripts guardados: {str(e)}")
        
        return scripts
    
    def get_script_content(self, script_path: str) -> Optional[str]:
        """Obtener contenido completo de un script"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer solo el script (sin metadata)
            script_start = content.find('# SCRIPT\n') + len('# SCRIPT\n')
            return content[script_start:].strip()
        
        except Exception as e:
            print(f"Error leyendo script: {str(e)}")
            return None
    
    def get_api_status(self) -> Dict:
        """Obtener estado de las APIs"""
        return {
            'huggingface': {
                'configured': bool(self.huggingface_api_key),
                'name': 'Hugging Face',
                'cost': 'GRATIS'
            },
            'groq': {
                'configured': bool(self.groq_api_key),
                'name': 'Groq',
                'cost': 'GRATIS (14,400 req/día)'
            },
            'cohere': {
                'configured': bool(self.cohere_api_key),
                'name': 'Cohere',
                'cost': 'GRATIS (1M tokens/mes)'
            }
        }

# Crear instancia global
script_generator = AIScriptGenerator()