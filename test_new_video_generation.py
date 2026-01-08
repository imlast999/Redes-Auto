#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la generación de videos con la nueva codificación mejorada
"""

import os
import sys
from datetime import datetime
from utils.video_processor import VideoProcessor
from utils.dynamic_video_processor import DynamicVideoProcessor
import subprocess
import json

def check_video_compatibility(video_path):
    """Verificar si un video tiene problemas de compatibilidad"""
    
    try:
        # Obtener información del video con ffprobe
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return False, f"Error ejecutando ffprobe: {result.stderr}"
        
        info = json.loads(result.stdout)
        
        # Verificar streams
        video_stream = None
        audio_stream = None
        
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        problems = []
        
        if video_stream:
            # Verificar pixel format
            pix_fmt = video_stream.get('pix_fmt', '')
            if pix_fmt != 'yuv420p':
                problems.append(f"Pixel format: {pix_fmt} (debería ser yuv420p)")
            
            # Verificar profile
            profile = video_stream.get('profile', '').lower()
            if 'baseline' not in profile and 'main' not in profile:
                problems.append(f"Profile: {profile} (debería ser baseline o main)")
        
        if audio_stream:
            # Verificar sample rate
            sample_rate = int(audio_stream.get('sample_rate', 0))
            if sample_rate not in [44100, 48000]:
                problems.append(f"Sample rate: {sample_rate} Hz (debería ser 44100 o 48000)")
        
        return len(problems) == 0, problems
    
    except Exception as e:
        return False, [f"Error analizando video: {str(e)}"]

def test_regular_video_generation():
    """Probar generación de video regular"""
    
    print("🧪 PROBANDO GENERACIÓN DE VIDEO REGULAR")
    print("=" * 50)
    
    # Crear procesador
    processor = VideoProcessor()
    
    # Buscar una imagen y audio de prueba
    test_image = None
    test_audio = None
    
    # Buscar imagen
    image_folders = ['generated/images', 'static/images', 'images']
    for folder in image_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_image = os.path.join(folder, file)
                    break
            if test_image:
                break
    
    # Buscar audio
    audio_folders = ['generated/audio', 'static/audio', 'audio']
    for folder in audio_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                    test_audio = os.path.join(folder, file)
                    break
            if test_audio:
                break
    
    if not test_image:
        print("❌ No se encontró imagen de prueba")
        print("💡 Coloca una imagen en generated/images/ para probar")
        return False
    
    if not test_audio:
        print("❌ No se encontró audio de prueba")
        print("💡 Coloca un archivo de audio en generated/audio/ para probar")
        return False
    
    print(f"📸 Imagen de prueba: {test_image}")
    print(f"🎵 Audio de prueba: {test_audio}")
    
    # Generar video
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"videos/processed/test_regular_{timestamp}.mp4"
    
    print(f"\n🎬 Generando video regular...")
    success, result = processor.create_video_from_image_and_audio(
        test_image, test_audio, output_path
    )
    
    if success:
        print(f"✅ Video generado: {result}")
        
        # Verificar compatibilidad
        print(f"\n🧪 Verificando compatibilidad...")
        is_compatible, problems = check_video_compatibility(result)
        
        if is_compatible:
            print("🎉 ¡VIDEO REGULAR COMPLETAMENTE COMPATIBLE!")
            return True
        else:
            print(f"⚠️  Problemas encontrados: {problems}")
            return False
    else:
        print(f"❌ Error generando video: {result}")
        return False

def test_dynamic_video_generation():
    """Probar generación de video dinámico"""
    
    print("\n🧪 PROBANDO GENERACIÓN DE VIDEO DINÁMICO")
    print("=" * 50)
    
    # Crear procesador dinámico
    processor = DynamicVideoProcessor()
    
    # Buscar imágenes y audio de prueba
    test_images = []
    test_audio = None
    
    # Buscar múltiples imágenes
    image_folders = ['generated/images', 'static/images', 'images']
    for folder in image_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(folder, file))
                    if len(test_images) >= 3:  # Máximo 3 imágenes para la prueba
                        break
            if test_images:
                break
    
    # Buscar audio
    audio_folders = ['generated/audio', 'static/audio', 'audio']
    for folder in audio_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                    test_audio = os.path.join(folder, file)
                    break
            if test_audio:
                break
    
    if len(test_images) < 2:
        print("❌ Se necesitan al menos 2 imágenes para video dinámico")
        print("💡 Coloca más imágenes en generated/images/ para probar")
        return False
    
    if not test_audio:
        print("❌ No se encontró audio de prueba")
        return False
    
    print(f"📸 Imágenes de prueba: {len(test_images)}")
    print(f"🎵 Audio de prueba: {test_audio}")
    
    # Preparar datos de imágenes
    images_data = []
    for i, img_path in enumerate(test_images):
        images_data.append({
            'image_path': img_path,
            'start_time': i * 5,  # 5 segundos por imagen
            'end_time': (i + 1) * 5,
            'concept': f'Imagen {i+1}',
            'style': 'test'
        })
    
    print(f"\n🎬 Generando video dinámico...")
    success, video_path, message = processor.create_dynamic_video(
        test_audio, images_data, "test_dynamic"
    )
    
    if success:
        print(f"✅ Video generado: {video_path}")
        print(f"📝 Mensaje: {message}")
        
        # Verificar compatibilidad
        print(f"\n🧪 Verificando compatibilidad...")
        is_compatible, problems = check_video_compatibility(video_path)
        
        if is_compatible:
            print("🎉 ¡VIDEO DINÁMICO COMPLETAMENTE COMPATIBLE!")
            return True
        else:
            print(f"⚠️  Problemas encontrados: {problems}")
            return False
    else:
        print(f"❌ Error generando video: {message}")
        return False

def main():
    """Función principal"""
    
    print("🧪 PRUEBA DE GENERACIÓN DE VIDEOS CON CODIFICACIÓN MEJORADA")
    print("=" * 70)
    
    # Verificar FFmpeg
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ FFmpeg no está disponible")
            return
    except:
        print("❌ FFmpeg no está instalado")
        return
    
    print("✅ FFmpeg disponible")
    
    # Probar generación de videos
    regular_success = test_regular_video_generation()
    dynamic_success = test_dynamic_video_generation()
    
    # Resultado final
    print(f"\n{'='*70}")
    print("📊 RESULTADO FINAL:")
    print(f"   ✅ Video regular: {'COMPATIBLE' if regular_success else 'PROBLEMAS'}")
    print(f"   ✅ Video dinámico: {'COMPATIBLE' if dynamic_success else 'PROBLEMAS'}")
    
    if regular_success and dynamic_success:
        print("\n🎉 ¡TODOS LOS TIPOS DE VIDEO SON COMPATIBLES!")
        print("   ✅ La codificación mejorada funciona perfectamente")
        print("   ✅ Los nuevos videos serán reproducibles en cualquier dispositivo")
    elif regular_success or dynamic_success:
        print("\n⚠️  Algunos tipos de video funcionan correctamente")
        print("💡 Revisa la configuración del tipo que falló")
    else:
        print("\n❌ Ambos tipos de video tienen problemas")
        print("💡 Verifica la configuración de FFmpeg")

if __name__ == "__main__":
    main()