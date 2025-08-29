import os
from pathlib import Path
import tempfile
import subprocess
try:
    import cv2
    import numpy as np
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("Video processing dependencies not available. Install moviepy and opencv-python.")

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def get_video_info(self, video_path):
        """Get basic information about a video file"""
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
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
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
        """Process a video with watermark and/or resize"""
        if not DEPS_AVAILABLE:
            # Fallback: just copy file to processed folder
            output_filename = f"processed_{os.path.basename(input_path)}"
            output_path = os.path.join("videos/processed", output_filename)
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
        
        try:
            # Load video
            clip = VideoFileClip(input_path)
            
            # Resize if requested
            if resize and aspect_ratio:
                clip = self._resize_video(clip, aspect_ratio)
            
            # Add watermark if requested
            if add_watermark and watermark_text:
                clip = self._add_watermark(clip, watermark_text, watermark_position)
            
            # Set output path
            output_filename = f"processed_{os.path.basename(input_path)}"
            output_path = os.path.join("videos/processed", output_filename)
            
            # Set quality parameters
            bitrate = self._get_bitrate(quality)
            
            # Write video
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
    
    def _resize_video(self, clip, aspect_ratio):
        """Resize video to Instagram format"""
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
        
        # Calculate scaling to fit within target dimensions
        scale_w = target_width / clip.w
        scale_h = target_height / clip.h
        scale = min(scale_w, scale_h)
        
        # Resize clip
        resized_clip = clip.resize(scale)
        
        # If the resized clip doesn't match exact dimensions, pad with black
        if resized_clip.w != target_width or resized_clip.h != target_height:
            # Create black background
            from moviepy.editor import ColorClip
            black_clip = ColorClip(size=(target_width, target_height), color=(0, 0, 0), duration=clip.duration)
            
            # Center the resized clip
            resized_clip = resized_clip.set_position('center')
            
            # Composite
            final_clip = CompositeVideoClip([black_clip, resized_clip])
            return final_clip
        
        return resized_clip
    
    def _add_watermark(self, clip, text, position):
        """Add text watermark to video"""
        try:
            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=50,
                color='white',
                stroke_color='black',
                stroke_width=2,
                font='Arial-Bold'
            ).set_duration(clip.duration)
            
            # Set position
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
            
            # Composite video with watermark
            watermarked_clip = CompositeVideoClip([clip, txt_clip])
            return watermarked_clip
        
        except Exception as e:
            print(f"Error adding watermark: {str(e)}")
            return clip
    
    def _get_bitrate(self, quality):
        """Get bitrate based on quality setting"""
        bitrates = {
            "High": "8000k",
            "Medium": "4000k",
            "Low": "2000k"
        }
        return bitrates.get(quality, "4000k")
    
    def create_preview_thumbnail(self, video_path, time_offset=1):
        """Create a thumbnail image from video"""
        try:
            clip = VideoFileClip(video_path)
            
            # Extract frame at specified time or 1 second
            time_offset = min(time_offset, clip.duration - 0.1)
            frame = clip.get_frame(time_offset)
            
            # Convert to PIL Image format
            from PIL import Image
            image = Image.fromarray(frame)
            
            # Save thumbnail
            thumbnail_path = os.path.join(self.temp_dir, f"thumb_{os.path.basename(video_path)}.jpg")
            image.save(thumbnail_path)
            
            clip.close()
            return thumbnail_path
        
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None
    
    def get_video_duration(self, video_path):
        """Get video duration in seconds"""
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            return duration
        except:
            return 0
    
    def batch_process_videos(self, video_list, processing_options):
        """Process multiple videos with same settings"""
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
