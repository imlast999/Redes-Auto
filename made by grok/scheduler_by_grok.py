import schedule
import time
import threading
from datetime import datetime, timedelta
import random
import os
import json
from utils.file_manager import FileManager
from utils.video_processor import VideoProcessor
from telegram import Bot

class AutoScheduler:
    def __init__(self):
        self.file_manager = FileManager()
        self.video_processor = VideoProcessor()
        self.is_running = False
        self.scheduler_thread = None
        self.config_file = "config/scheduler_config.json"
        self.telegram_bot = None
        self.load_config()
    
    def load_config(self):
        default_config = {
            "enabled": False,
            "weekday_slots": {
                "morning": {"start": "07:00", "end": "09:00"},
                "evening": {"start": "18:00", "end": "21:00"}
            },
            "weekend_slots": {
                "midday": {"start": "10:00", "end": "13:00"}
            },
            "videos_per_day": 2,
            "auto_watermark": True,
            "auto_resize": True,
            "watermark_text": "@tuusuario",
            "preferred_format": "9:16 (Stories/Reels)",
            "telegram_channel": "t.me/tucanalgratis",
            "telegram_token": ""
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
        if self.config["telegram_token"]:
            self.telegram_bot = Bot(token=self.config["telegram_token"])
    
    def save_config(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_random_time_in_slot(self, start_time, end_time):
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        random_minutes = random.randint(start_minutes, end_minutes)
        hour = random_minutes // 60
        minute = random_minutes % 60
        return f"{hour:02d}:{minute:02d}"
    
    def schedule_daily_posts(self):
        schedule.clear()
        if not self.config["enabled"]:
            return
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            morning_time = self.get_random_time_in_slot(
                self.config["weekday_slots"]["morning"]["start"],
                self.config["weekday_slots"]["morning"]["end"]
            )
            getattr(schedule.every(), day).at(morning_time).do(self.process_and_queue_video)
            evening_time = self.get_random_time_in_slot(
                self.config["weekday_slots"]["evening"]["start"],
                self.config["weekday_slots"]["evening"]["end"]
            )
            getattr(schedule.every(), day).at(evening_time).do(self.process_and_queue_video)
        for day in ['saturday', 'sunday']:
            weekend_time = self.get_random_time_in_slot(
                self.config["weekend_slots"]["midday"]["start"],
                self.config["weekend_slots"]["midday"]["end"]
            )
            getattr(schedule.every(), day).at(weekend_time).do(self.process_and_queue_video)
    
    def select_luxury_video(self):
        pending_videos = self.file_manager.get_pending_videos()
        if not pending_videos:
            return None
        keywords = [
            'luxury', 'lujo', 'rich', 'wealth', 'expensive', 'mansion', 
            'supercar', 'yacht', 'dubai', 'monaco', 'millionaire', 
            'billionaire', 'lifestyle', 'exclusive', 'premium',
            'inversiones', 'acciones', 'bienes raices', 'crypto', 'memecoins', 'startups'
        ]
        luxury_videos = []
        for video in pending_videos:
            video_name = os.path.basename(video).lower()
            if any(keyword in video_name for keyword in keywords):
                luxury_videos.append(video)
        if not luxury_videos:
            luxury_videos = pending_videos
        return random.choice(luxury_videos)
    
    def process_and_queue_video(self):
        try:
            selected_video = self.select_luxury_video()
            if not selected_video:
                print(f"[{datetime.now()}] No hay videos disponibles para procesar")
                return
            print(f"[{datetime.now()}] Procesando video: {os.path.basename(selected_video)}")
            processed_path = self.video_processor.process_video(
                selected_video,
                add_watermark=self.config["auto_watermark"],
                watermark_text=self.config["watermark_text"],
                resize=self.config["auto_resize"],
                aspect_ratio=self.config["preferred_format"],
                quality="Medium"
            )
            if processed_path:
                self.file_manager.move_to_processed(selected_video, processed_path)
                self.mark_ready_for_publish(processed_path)
                if self.telegram_bot:
                    try:
                        with open(processed_path, 'rb') as video_file:
                            self.telegram_bot.send_video(
                                chat_id=self.config["telegram_channel"],
                                video=video_file,
                                caption=f"Nuevo video: {os.path.basename(processed_path)}\nÚnete: {self.config['telegram_channel']}"
                            )
                    except Exception as e:
                        print(f"[{datetime.now()}] Error enviando a Telegram: {str(e)}")
                print(f"[{datetime.now()}] Video procesado exitosamente: {os.path.basename(processed_path)}")
            else:
                print(f"[{datetime.now()}] Error al procesar video")
        except Exception as e:
            print(f"[{datetime.now()}] Error en proceso automático: {str(e)}")
    
    def mark_ready_for_publish(self, video_path):
        queue_file = "config/publish_queue.json"
        queue = []
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    queue = json.load(f)
            except:
                queue = []
        queue_entry = {
            "video_path": video_path,
            "processed_at": datetime.now().isoformat(),
            "status": "ready_to_publish",
            "scheduled_time": datetime.now().isoformat()
        }
        queue.append(queue_entry)
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def start_scheduler(self):
        if self.is_running:
            return
        self.is_running = True
        self.schedule_daily_posts()
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print(f"[{datetime.now()}] Programador iniciado")
    
    def stop_scheduler(self):
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        schedule.clear()
        print(f"[{datetime.now()}] Programador detenido")
    
    def get_next_scheduled_times(self):
        jobs = schedule.get_jobs()
        next_runs = []
        for job in jobs:
            next_runs.append({
                "job": str(job.job_func.__name__),
                "next_run": job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else "N/A"
            })
        return sorted(next_runs, key=lambda x: x["next_run"])
    
    def get_publish_queue(self):
        queue_file = "config/publish_queue.json"
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def manual_publish_next(self):
        queue = self.get_publish_queue()
        if not queue:
            return False, "No hay videos en la cola"
        video_entry = queue[0]
        video_path = video_entry["video_path"]
        try:
            if self.file_manager.move_to_published(video_path):
                queue.pop(0)
                queue_file = "config/publish_queue.json"
                with open(queue_file, 'w') as f:
                    json.dump(queue, f, indent=2)
                if self.telegram_bot:
                    try:
                        with open(video_path, 'rb') as video_file:
                            self.telegram_bot.send_video(
                                chat_id=self.config["telegram_channel"],
                                video=video_file,
                                caption=f"Video publicado: {os.path.basename(video_path)}\nÚnete: {self.config['telegram_channel']}"
                            )
                    except Exception as e:
                        print(f"[{datetime.now()}] Error enviando a Telegram: {str(e)}")
                return True, f"Video publicado: {os.path.basename(video_path)}"
            else:
                return False, "Error al mover video a publicados"
        except Exception as e:
            return False, f"Error: {str(e)}"