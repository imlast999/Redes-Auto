# -*- coding: utf-8 -*-
"""
Programador automático completo para Instagram Video Dashboard
Incluye publicación automática inteligente y gestión de cola
"""

import os
import json
import random
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

class AutoScheduler:
    def __init__(self):
        # Configuración
        self.config_file = Path('config/scheduler_config.json')
        self.queue_file = Path('config/publish_queue.json')
        self.log_file = Path('config/scheduler.log')
        
        # Crear directorios
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Estado del programador
        self.is_running = False
        self.scheduler_thread = None
        
        # Configuración por defecto
        self.default_config = {
            'enabled': False,
            'watermark_text': '@yourusername',
            'auto_watermark': True,
            'auto_resize': True,
            'preferred_format': '9:16 (Stories/Reels)',
            'weekday_slots': {
                'morning': {'start': '07:00', 'end': '09:00'},
                'evening': {'start': '18:00', 'end': '21:00'}
            },
            'weekend_slots': {
                'midday': {'start': '10:00', 'end': '13:00'}
            },
            'posts_per_day': {
                'weekdays': 2,
                'weekends': 1
            },
            'luxury_keywords': [
                'luxury', 'lujo', 'rich', 'wealth', 'expensive', 'mansion',
                'supercar', 'yacht', 'dubai', 'monaco', 'millionaire',
                'billionaire', 'lifestyle', 'exclusive', 'premium'
            ],
            'hashtags': {
                'luxury': ['#luxury', '#lifestyle', '#wealth', '#success', '#motivation'],
                'business': ['#business', '#entrepreneur', '#success', '#money', '#investment'],
                'crypto': ['#crypto', '#bitcoin', '#blockchain', '#trading', '#investment']
            }
        }
        
        # Cargar configuración
        self.config = self.load_config()
        
        # Configurar logging
        self.setup_logging()
        
        # Importar componentes necesarios
        self.setup_components()
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_components(self):
        """Configurar componentes necesarios"""
        try:
            from utils.file_manager import FileManager
            from utils.video_processor import VideoProcessor
            from utils.instagram_publisher import InstagramPublisher
            from utils.telegram_bot import TelegramBot
            
            self.file_manager = FileManager()
            self.video_processor = VideoProcessor()
            self.instagram_publisher = InstagramPublisher()
            self.telegram_bot = TelegramBot()
            
        except ImportError as e:
            self.logger.error(f"Error importando componentes: {e}")
            # Crear componentes mock
            self.file_manager = None
            self.video_processor = None
            self.instagram_publisher = None
            self.telegram_bot = None
    
    def load_config(self) -> Dict:
        """Cargar configuración del programador"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Fusionar con configuración por defecto
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                return self.default_config.copy()
        
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """Guardar configuración"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuración guardada exitosamente")
        
        except Exception as e:
            self.logger.error(f"Error guardando configuración: {e}")
    
    def start_scheduler(self):
        """Iniciar el programador automático"""
        if self.is_running:
            self.logger.warning("El programador ya está ejecutándose")
            return
        
        self.is_running = True
        self.config['enabled'] = True
        self.save_config()
        
        # Limpiar programaciones anteriores
        schedule.clear()
        
        # Programar publicaciones diarias
        self.schedule_daily_posts()
        
        # Iniciar hilo del programador
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Programador automático iniciado")
    
    def stop_scheduler(self):
        """Detener el programador automático"""
        self.is_running = False
        self.config['enabled'] = False
        self.save_config()
        
        # Limpiar programaciones
        schedule.clear()
        
        self.logger.info("Programador automático detenido")
    
    def _run_scheduler(self):
        """Ejecutar el programador en bucle"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except Exception as e:
                self.logger.error(f"Error en el programador: {e}")
                time.sleep(60)
    
    def schedule_daily_posts(self):
        """Programar publicaciones diarias"""
        # Limpiar programaciones anteriores
        schedule.clear()
        
        # Programar para días laborales (Lunes a Viernes)
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            posts_count = self.config['posts_per_day']['weekdays']
            
            if posts_count >= 1:
                # Publicación matutina
                morning_time = self._get_random_time_in_slot('weekday', 'morning')
                getattr(schedule.every(), day).at(morning_time).do(self.auto_publish_job)
            
            if posts_count >= 2:
                # Publicación vespertina
                evening_time = self._get_random_time_in_slot('weekday', 'evening')
                getattr(schedule.every(), day).at(evening_time).do(self.auto_publish_job)
        
        # Programar para fines de semana
        for day in ['saturday', 'sunday']:
            posts_count = self.config['posts_per_day']['weekends']
            
            if posts_count >= 1:
                # Publicación de mediodía
                midday_time = self._get_random_time_in_slot('weekend', 'midday')
                getattr(schedule.every(), day).at(midday_time).do(self.auto_publish_job)
        
        self.logger.info("Publicaciones diarias programadas")
    
    def _get_random_time_in_slot(self, day_type: str, slot: str) -> str:
        """Obtener hora aleatoria dentro de un slot"""
        try:
            if day_type == 'weekday':
                slot_config = self.config['weekday_slots'][slot]
            else:
                slot_config = self.config['weekend_slots'][slot]
            
            start_time = datetime.strptime(slot_config['start'], '%H:%M')
            end_time = datetime.strptime(slot_config['end'], '%H:%M')
            
            # Calcular diferencia en minutos
            diff_minutes = int((end_time - start_time).total_seconds() / 60)
            
            # Hora aleatoria dentro del slot
            random_minutes = random.randint(0, diff_minutes)
            random_time = start_time + timedelta(minutes=random_minutes)
            
            return random_time.strftime('%H:%M')
        
        except Exception as e:
            self.logger.error(f"Error calculando hora aleatoria: {e}")
            return "12:00"  # Hora por defecto
    
    def auto_publish_job(self):
        """Trabajo de publicación automática"""
        try:
            self.logger.info("Iniciando trabajo de publicación automática")
            
            # Seleccionar video para publicar
            video_path = self._select_video_for_publishing()
            
            if not video_path:
                self.logger.warning("No hay videos disponibles para publicar")
                return
            
            # Procesar video si es necesario
            processed_video = self._process_video_for_instagram(video_path)
            
            if not processed_video:
                self.logger.error(f"Error procesando video: {video_path}")
                return
            
            # Generar caption y hashtags
            caption = self._generate_caption_for_video(video_path)
            
            # Publicar en Instagram
            success, message = self._publish_to_instagram(processed_video, caption)
            
            if success:
                self.logger.info(f"Video publicado exitosamente: {os.path.basename(video_path)}")
                
                # Mover a carpeta de publicados
                if self.file_manager:
                    self.file_manager.move_to_published(processed_video)
                
                # Enviar notificación
                if self.telegram_bot:
                    self.telegram_bot.notify_video_published(os.path.basename(video_path))
            
            else:
                self.logger.error(f"Error publicando video: {message}")
                
                # Enviar notificación de error
                if self.telegram_bot:
                    self.telegram_bot.notify_error("Publicación Automática", message, os.path.basename(video_path))
        
        except Exception as e:
            self.logger.error(f"Error en trabajo de publicación automática: {e}")
    
    def _select_video_for_publishing(self) -> Optional[str]:
        """Seleccionar video inteligentemente para publicar"""
        if not self.file_manager:
            return None
        
        try:
            # Obtener videos pendientes
            pending_videos = self.file_manager.get_pending_videos()
            
            if not pending_videos:
                return None
            
            # Filtrar videos con palabras clave de lujo
            luxury_videos = []
            for video in pending_videos:
                video_name = os.path.basename(video).lower()
                
                for keyword in self.config['luxury_keywords']:
                    if keyword.lower() in video_name:
                        luxury_videos.append(video)
                        break
            
            # Usar videos de lujo si están disponibles, sino cualquier video
            candidates = luxury_videos if luxury_videos else pending_videos
            
            # Seleccionar video aleatorio
            return random.choice(candidates)
        
        except Exception as e:
            self.logger.error(f"Error seleccionando video: {e}")
            return None
    
    def _process_video_for_instagram(self, video_path: str) -> Optional[str]:
        """Procesar video para Instagram"""
        if not self.video_processor:
            return video_path  # Devolver original si no hay procesador
        
        try:
            processed_path = self.video_processor.process_video(
                input_path=video_path,
                add_watermark=self.config['auto_watermark'],
                watermark_text=self.config['watermark_text'],
                watermark_position='bottom-right',
                resize=self.config['auto_resize'],
                aspect_ratio=self.config['preferred_format'],
                quality='Medium'
            )
            
            return processed_path
        
        except Exception as e:
            self.logger.error(f"Error procesando video: {e}")
            return None
    
    def _generate_caption_for_video(self, video_path: str) -> str:
        """Generar caption automático para el video"""
        try:
            video_name = os.path.basename(video_path).lower()
            
            # Determinar tema basado en el nombre del archivo
            theme = 'luxury'  # Por defecto
            
            if any(word in video_name for word in ['business', 'negocio', 'empresa']):
                theme = 'business'
            elif any(word in video_name for word in ['crypto', 'bitcoin', 'blockchain']):
                theme = 'crypto'
            
            # Plantillas de caption por tema
            caption_templates = {
                'luxury': [
                    "La diferencia entre soñar y vivir tus sueños está en las decisiones que tomas HOY. 💎",
                    "Mientras otros buscan excusas, los millonarios buscan oportunidades. 🏆",
                    "El lujo no es un destino, es una mentalidad. ¿Cuál es la tuya? ✨"
                ],
                'business': [
                    "En el mundo de los negocios, la velocidad mata. ¿Estás listo para acelerar? ⚡",
                    "No busques oportunidades, créalas. El éxito está en tus manos. 💼",
                    "Los grandes negocios nacen de grandes decisiones. ¿Cuál será la tuya? 🚀"
                ],
                'crypto': [
                    "El futuro del dinero ya está aquí. ¿Te vas a quedar atrás? 🚀",
                    "Mientras unos dudan, otros construyen el futuro financiero. 💰",
                    "La revolución crypto no espera a nadie. ¿Estás preparado? ⚡"
                ]
            }
            
            # Seleccionar caption aleatorio
            captions = caption_templates.get(theme, caption_templates['luxury'])
            base_caption = random.choice(captions)
            
            # Agregar hashtags
            hashtags = self.config['hashtags'].get(theme, self.config['hashtags']['luxury'])
            hashtag_string = ' '.join(hashtags)
            
            # Caption final
            final_caption = f"{base_caption}\n\n{hashtag_string}"
            
            return final_caption
        
        except Exception as e:
            self.logger.error(f"Error generando caption: {e}")
            return "Contenido exclusivo para mentes millonarias. 💎 #luxury #lifestyle #success"
    
    def _publish_to_instagram(self, video_path: str, caption: str) -> Tuple[bool, str]:
        """Publicar video en Instagram"""
        if not self.instagram_publisher:
            return False, "Instagram Publisher no disponible"
        
        try:
            return self.instagram_publisher.upload_video_to_instagram(video_path, caption)
        
        except Exception as e:
            self.logger.error(f"Error publicando en Instagram: {e}")
            return False, str(e)
    
    def manual_publish_next(self) -> Tuple[bool, str]:
        """Publicar manualmente el siguiente video en cola"""
        try:
            # Ejecutar trabajo de publicación
            self.auto_publish_job()
            return True, "Video publicado manualmente"
        
        except Exception as e:
            self.logger.error(f"Error en publicación manual: {e}")
            return False, str(e)
    
    def get_publish_queue(self) -> List[Dict]:
        """Obtener cola de publicación"""
        try:
            if self.queue_file.exists():
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"Error obteniendo cola de publicación: {e}")
            return []
    
    def add_to_queue(self, video_path: str, priority: int = 0):
        """Agregar video a la cola de publicación"""
        try:
            queue = self.get_publish_queue()
            
            queue_entry = {
                'video_path': video_path,
                'priority': priority,
                'added_at': datetime.now().isoformat(),
                'processed_at': None,
                'status': 'pending'
            }
            
            queue.append(queue_entry)
            
            # Ordenar por prioridad
            queue.sort(key=lambda x: x['priority'], reverse=True)
            
            # Guardar cola
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Video agregado a la cola: {os.path.basename(video_path)}")
        
        except Exception as e:
            self.logger.error(f"Error agregando a la cola: {e}")
    
    def get_next_scheduled_times(self, limit: int = 5) -> List[Dict]:
        """Obtener próximas horas programadas"""
        try:
            next_runs = []
            
            for job in schedule.jobs:
                next_run = job.next_run
                if next_run:
                    next_runs.append({
                        'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S'),
                        'job_func': job.job_func.__name__ if hasattr(job.job_func, '__name__') else 'auto_publish'
                    })
            
            # Ordenar por fecha
            next_runs.sort(key=lambda x: x['next_run'])
            
            return next_runs[:limit]
        
        except Exception as e:
            self.logger.error(f"Error obteniendo próximas programaciones: {e}")
            return []
    
    def get_scheduler_stats(self) -> Dict:
        """Obtener estadísticas del programador"""
        try:
            stats = {
                'is_running': self.is_running,
                'enabled': self.config.get('enabled', False),
                'total_jobs': len(schedule.jobs),
                'next_runs': len(self.get_next_scheduled_times()),
                'queue_size': len(self.get_publish_queue()),
                'config_last_updated': self.config_file.stat().st_mtime if self.config_file.exists() else None
            }
            
            if stats['config_last_updated']:
                stats['config_last_updated'] = datetime.fromtimestamp(stats['config_last_updated']).isoformat()
            
            return stats
        
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}
    
    def update_config(self, new_config: Dict):
        """Actualizar configuración"""
        try:
            self.config.update(new_config)
            self.save_config()
            
            # Reprogramar si está activo
            if self.is_running:
                self.schedule_daily_posts()
            
            self.logger.info("Configuración actualizada")
        
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")
    
    def get_logs(self, lines: int = 50) -> List[str]:
        """Obtener últimas líneas del log"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:] if len(all_lines) > lines else all_lines
            else:
                return []
        
        except Exception as e:
            self.logger.error(f"Error obteniendo logs: {e}")
            return [f"Error obteniendo logs: {e}"]