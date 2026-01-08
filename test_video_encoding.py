#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la codificación de video
"""

import os
import sys
import subprocess
from pathlib import Path

def test_video_compatibility(video_path):
    """Probar la compatibilidad de un video"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return False
    
    print(f"🧪 Probando compatibilidad de: {video_path}")
    
    try:
        # Obtener información del video con ffprobe
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Error ejecutando ffprobe: {result.stderr}")
            return False
        
        import json
        info = json.loads(result.stdout)
        
        # Verificar streams
        video_stream = None
        audio_stream = None
        
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        print("📊 INFORMACIÓN DEL VIDEO:")
        print(f"   📁 Tamaño: {os.path.getsize(video_path) / (1024*1024):.1f} MB")
        
        if video_stream:
            print(f"   🎬 Video Codec: {video_stream.get('codec_name', 'N/A')}")
            print(f"   📐 Resolución: {video_stream.get('width', 'N/A')}x{video_stream.get('height', 'N/A')}")
            print(f"   🎨 Pixel Format: {video_stream.get('pix_fmt', 'N/A')}")
            print(f"   📈 Profile: {video_stream.get('profile', 'N/A')}")
            print(f"   📊 Level: {video_stream.get('level', 'N/A')}")
            print(f"   🎞️  FPS: {video_stream.get('r_frame_rate', 'N/A')}")
        
        if audio_stream:
            print(f"   🎵 Audio Codec: {audio_stream.get('codec_name', 'N/A')}")
            print(f"   📻 Sample Rate: {audio_stream.get('sample_rate', 'N/A')} Hz")
            print(f"   🔊 Channels: {audio_stream.get('channels', 'N/A')}")
            print(f"   💿 Bitrate: {audio_stream.get('bit_rate', 'N/A')} bps")
        
        # Verificar compatibilidad
        compatibility_issues = []
        
        if video_stream:
            # Verificar codec de video
            if video_stream.get('codec_name') != 'h264':
                compatibility_issues.append("❌ Codec de video no es H.264")
            else:
                print("✅ Codec de video: H.264 (Compatible)")
            
            # Verificar pixel format
            if video_stream.get('pix_fmt') != 'yuv420p':
                compatibility_issues.append("❌ Pixel format no es yuv420p")
            else:
                print("✅ Pixel format: yuv420p (Compatible)")
            
            # Verificar profile
            profile = video_stream.get('profile', '').lower()
            if 'baseline' not in profile and 'main' not in profile:
                compatibility_issues.append(f"⚠️  Profile: {profile} (puede no ser compatible)")
            else:
                print(f"✅ Profile: {profile} (Compatible)")
        
        if audio_stream:
            # Verificar codec de audio
            if audio_stream.get('codec_name') != 'aac':
                compatibility_issues.append("❌ Codec de audio no es AAC")
            else:
                print("✅ Codec de audio: AAC (Compatible)")
            
            # Verificar sample rate
            sample_rate = int(audio_stream.get('sample_rate', 0))
            if sample_rate not in [44100, 48000]:
                compatibility_issues.append(f"⚠️  Sample rate: {sample_rate} Hz (puede no ser compatible)")
            else:
                print(f"✅ Sample rate: {sample_rate} Hz (Compatible)")
        
        # Resultado final
        if compatibility_issues:
            print("\n⚠️  PROBLEMAS DE COMPATIBILIDAD ENCONTRADOS:")
            for issue in compatibility_issues:
                print(f"   {issue}")
            return False
        else:
            print("\n🎉 ¡VIDEO COMPLETAMENTE COMPATIBLE!")
            print("   ✅ Reproducible en todos los dispositivos")
            print("   ✅ Compatible con redes sociales")
            print("   ✅ Optimizado para streaming")
            return True
    
    except Exception as e:
        print(f"❌ Error analizando video: {str(e)}")
        return False

def test_video_playback(video_path):
    """Probar reproducción del video"""
    
    print(f"\n🎬 PROBANDO REPRODUCCIÓN: {video_path}")
    
    try:
        # Intentar reproducir los primeros 5 segundos
        cmd = [
            'ffmpeg', '-i', video_path, '-t', '5', '-f', 'null', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Video se reproduce correctamente")
            return True
        else:
            print(f"❌ Error de reproducción: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"❌ Error probando reproducción: {str(e)}")
        return False

def main():
    """Función principal"""
    
    print("🧪 PRUEBA DE COMPATIBILIDAD DE VIDEOS")
    print("=" * 50)
    
    # Buscar videos en las carpetas de salida
    video_folders = [
        'videos/dynamic',
        'videos/processed',
        'generated/videos'
    ]
    
    videos_found = []
    
    for folder in video_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith('.mp4'):
                    videos_found.append(os.path.join(folder, file))
    
    if not videos_found:
        print("❌ No se encontraron videos para probar")
        print("💡 Genera un video primero usando la interfaz web")
        return
    
    print(f"📹 Videos encontrados: {len(videos_found)}")
    
    # Probar cada video
    compatible_count = 0
    
    for video_path in videos_found[-3:]:  # Probar solo los últimos 3
        print(f"\n{'='*60}")
        
        # Probar compatibilidad
        is_compatible = test_video_compatibility(video_path)
        
        # Probar reproducción
        can_play = test_video_playback(video_path)
        
        if is_compatible and can_play:
            compatible_count += 1
            print("🎉 ¡VIDEO PERFECTO!")
        else:
            print("⚠️  Video con problemas")
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTADO FINAL: {compatible_count}/{min(len(videos_found), 3)} videos compatibles")
    
    if compatible_count == min(len(videos_found), 3):
        print("🎉 ¡TODOS LOS VIDEOS SON COMPATIBLES!")
        print("✅ La codificación está funcionando perfectamente")
    else:
        print("⚠️  Algunos videos tienen problemas de compatibilidad")
        print("💡 Verifica la configuración de FFmpeg")

if __name__ == "__main__":
    main()