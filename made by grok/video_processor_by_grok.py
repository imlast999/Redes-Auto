import os
from pathlib import Path
import tempfile
import subprocess
try:
    import cv2
    import numpy as np
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip
    from diffusers import StableDiffusionPipeline
    import torch
    from elevenlabs import generate, save
    import whisper
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("Video processing dependencies not available. Install moviepy, opencv-python, diffusers, elevenlabs, whisper.")

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def get_video_info(self, video_path):
        if not DEPS_AVAILABLE:
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            return {
                'duration': 'Unknown',
                'width': 'Unknown', 
                'height': 'Unknown',
                'fps': 'Unknown',
                'size': round(file_size, 2)
            }
        
        try:
            clip = VideoFileClip(video_path)
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            info = {
                'duration': clip.duration,
                'width': clip.w,
                'height': clip.h,
                'fps': clip.fps,
                'size': round(file_size, 2)
            }
            clip.close()
            return info
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return {}
    
    def process_video(self, input_path, add_watermark=False, watermark_text=None, 
                     watermark_position="bottom-right", resize=False, aspect_ratio=None, 
                     quality="Medium"):
        if not DEPS_AVAILABLE:
            output_filename = f"processed_{os.path.basename(input_path)}"
            output_path = os.path.join("videos/processed", output_filename)
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
        
        try:
            clip = VideoFileClip(input_path)
            if resize and aspect_ratio:
                clip = self._resize_video(clip, aspect_ratio)
            if add_watermark and watermark_text:
                clip = self._add_watermark(clip, watermark_text, watermark_position)
            output_filename = f"processed_{os.path.basename(input_path)}"
            output_path = os.path.join("videos/processed", output_filename)
            bitrate = self._get_bitrate(quality)
            clip.write_videofile(
                output_path,
                bitrate=bitrate,
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            clip.close()
            return output_path
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            return None
    
    def generate_ai_video(self, script_path, image_prompt, voice="Adam", add_subtitles=True, telegram_cta=""):
        if not DEPS_AVAILABLE:
            return None, "Dependencies not available"
        
        try:
            # Leer guion
            with open(script_path, 'r') as f:
                script = f.read()
            
            # Generar imagen de fondo
            model_id = "stabilityai/stable-diffusion-2-1"
            pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
            pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
            imagen = pipe(image_prompt).images[0]
            imagen_path = os.path.join(self.temp_dir, "fondo_temp.jpg")
            imagen.save(imagen_path)
            
            # Generar voz
            audio = generate(
                text=script,
                voice=voice,
                model="eleven_monolingual_v1"
            )
            audio_path = os.path.join(self.temp_dir, "voz_temp.mp3")
            save(audio, audio_path)
            
            # Generar subtítulos
            subtitulos = []
            if add_subtitles:
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)
                subtitulos = [(segment["start"], segment["end"], segment["text"]) for segment in result["segments"]]
            
            # Crear video
            imagen_clip = ImageClip(imagen_path).set_duration(AudioFileClip(audio_path).duration)
            audio_clip = AudioFileClip(audio_path)
            clips = [imagen_clip]
            
            if add_subtitles:
                subtitulos_clips = [
                    TextClip(txt, fontsize=40, color='white', stroke_color='black', stroke_width=2)
                    .set_position(('center', 'bottom'))
                    .set_start(start)
                    .set_end(end)
                    for start, end, txt in subtitulos
                ]
                clips.extend(subtitulos_clips)
            
            video = CompositeVideoClip(clips).set_audio(audio_clip)
            video_path = f"videos/pending/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            os.makedirs("videos/pending", exist_ok=True)
            video.write_videofile(video_path, fps=24)
            
            # Limpiar temporales
            os.remove(imagen_path)
            os.remove(audio_path)
            
            return video_path, "Video generated successfully"
        except Exception as e:
            return None, f"Error generating AI video: {str(e)}"
    
    def _resize_video(self, clip, aspect_ratio):
        if aspect_ratio == "9:16 (Stories/Reels)":
            target_width = 1080
            target_height = 1920
        elif aspect_ratio == "1:1 (Square)":
            target_width = 1080
            target_height = 1080
        elif aspect_ratio == "4:5 (Portrait)":
            target_width = 1080
            target_height = 1350
        else:
            return clip
        
        scale_w = target_width / clip.w
        scale_h = target_height / clip.h
        scale = min(scale_w, scale_h)
        resized_clip = clip.resize(scale)
        
        if resized_clip.w != target_width or resized_clip.h != target_height:
            from moviepy.editor import ColorClip
            black_clip = ColorClip(size=(target_width, target_height), color=(0, 0, 0), duration=clip.duration)
            resized_clip = resized_clip.set_position('center')
            final_clip = CompositeVideoClip([black_clip, resized_clip])
            return final_clip
        return resized_clip
    
    def _add_watermark(self, clip, text, position):
        try:
            txt_clip = TextClip(
                text,
                fontsize=50,
                color='white',
                stroke_color='black',
                stroke_width=2,
                font='Arial-Bold'
            ).set_duration(clip.duration)
            if position == "bottom-right":
                txt_clip = txt_clip.set_position(('right', 'bottom')).set_margin((20, 20))
            elif position == "bottom-left":
                txt_clip = txt_clip.set_position(('left', 'bottom')).set_margin((20, 20))
            elif position == "top-right":
                txt_clip = txt_clip.set_position(('right', 'top')).set_margin((20, 20))
            elif position == "top-left":
                txt_clip = txt_clip.set_position(('left', 'top')).set_margin((20, 20))
            elif position == "center":
                txt_clip = txt_clip.set_position('center')
            watermarked_clip = CompositeVideoClip([clip, txt_clip])
            return watermarked_clip
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            return clip
    
    def _get_bitrate(self, quality):
        bitrates = {
            "High": "8000k",
            "Medium": "4000k",
            "Low": "2000k"
        }
        return bitrates.get(quality, "4000k")
    
    def create_preview_thumbnail(self, video_path, time_offset=1):
        try:
            clip = VideoFileClip(video_path)
            time_offset = min(time_offset, clip.duration - 0.1)
            frame = clip.get_frame(time_offset)
            from PIL import Image
            image = Image.fromarray(frame)
            thumbnail_path = os.path.join(self.temp_dir, f"thumb_{os.path.basename(video_path)}.jpg")
            image.save(thumbnail_path)
            clip.close()
            return thumbnail_path
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None
    
    def get_video_duration(self, video_path):
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except:
            return 0
    
    def batch_process_videos(self, video_list, processing_options):
        results = []
        for video_path in video_list:
            try:
                output_path = self.process_video(
                    video_path,
                    **processing_options
                )
                results.append({
                    'input': video_path,
                    'output': output_path,
                    'status': 'success' if output_path else 'failed'
                })
            except Exception as e:
                results.append({
                    'input': video_path,
                    'output': None,
                    'status': 'error',
                    'error': str(e)
                })
        return results