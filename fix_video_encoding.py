#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la codificación de videos existentes
Convierte videos con problemas de compatibilidad a formato ultra compatible
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

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

def fix_video_encoding(input_path, output_path=None):
    """Corregir la codificación de un video"""
    
    if not output_path:
        # Crear nombre de archivo corregido
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_fixed{ext}"
    
    print(f"🔧 Corrigiendo codificación: {os.path.basename(input_path)}")
    
    try:
        # Comando FFmpeg para recodificar con configuración ultra compatible
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            
            # Filtros de video para forzar conversión correcta
            '-vf', 'scale=in_range=full:out_range=tv,format=yuv420p',
            
            # Configuración de video ULTRA COMPATIBLE
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',  # Calidad balanceada
            '-pix_fmt', 'yuv420p',  # CRÍTICO: Formato compatible
            '-profile:v', 'baseline',  # Perfil más compatible
            '-level', '3.0',  # Nivel compatible con dispositivos antiguos
            '-movflags', '+faststart',  # Optimización para streaming
            '-colorspace', 'bt709',  # Espacio de color estándar
            '-color_primaries', 'bt709',
            '-color_trc', 'bt709',
            '-color_range', 'tv',  # Rango de color TV (limitado)
            
            # Configuración de audio ULTRA COMPATIBLE
            '-c:a', 'aac',
            '-b:a', '128k',  # Bitrate fijo
            '-ar', '44100',  # Sample rate estándar
            '-ac', '2',  # Estéreo
            '-aac_coder', 'twoloop',  # Codificador AAC más compatible
            
            # Optimizaciones adicionales
            '-avoid_negative_ts', 'make_zero',
            '-fflags', '+genpts',
            '-max_muxing_queue_size', '1024',
            
            output_path
        ]
        
        print(f"   📝 Ejecutando recodificación...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_path):
            # Verificar que el video corregido es compatible
            is_compatible, issues = check_video_compatibility(output_path)
            
            if is_compatible:
                print(f"   ✅ Video corregido exitosamente")
                
                # Mostrar información del archivo corregido
                original_size = os.path.getsize(input_path) / (1024 * 1024)
                fixed_size = os.path.getsize(output_path) / (1024 * 1024)
                
                print(f"   📊 Tamaño original: {original_size:.1f}MB")
                print(f"   📊 Tamaño corregido: {fixed_size:.1f}MB")
                
                return True, output_path
            else:
                print(f"   ⚠️  Video corregido pero aún tiene problemas: {issues}")
                return False, f"Problemas persistentes: {issues}"
        else:
            print(f"   ❌ Error en FFmpeg: {result.stderr}")
            return False, f"Error FFmpeg: {result.stderr}"
    
    except Exception as e:
        print(f"   ❌ Error corrigiendo video: {str(e)}")
        return False, f"Error: {str(e)}"

def batch_fix_videos(video_folders, replace_originals=False):
    """Corregir múltiples videos en lote"""
    
    print("🔧 CORRECCIÓN MASIVA DE CODIFICACIÓN DE VIDEOS")
    print("=" * 60)
    
    # Buscar videos en las carpetas especificadas
    videos_to_fix = []
    
    for folder in video_folders:
        if os.path.exists(folder):
            print(f"📁 Escaneando carpeta: {folder}")
            
            for file in os.listdir(folder):
                if file.endswith('.mp4') and not file.endswith('_fixed.mp4'):
                    video_path = os.path.join(folder, file)
                    
                    # Verificar si necesita corrección
                    is_compatible, problems = check_video_compatibility(video_path)
                    
                    if not is_compatible:
                        videos_to_fix.append({
                            'path': video_path,
                            'problems': problems
                        })
                        print(f"   ⚠️  {file}: {len(problems)} problemas")
                    else:
                        print(f"   ✅ {file}: Compatible")
    
    if not videos_to_fix:
        print("\n🎉 ¡Todos los videos ya son compatibles!")
        return
    
    print(f"\n📊 Videos que necesitan corrección: {len(videos_to_fix)}")
    
    # Procesar cada video
    fixed_count = 0
    
    for video_info in videos_to_fix:
        video_path = video_info['path']
        problems = video_info['problems']
        
        print(f"\n{'='*60}")
        print(f"🎬 Procesando: {os.path.basename(video_path)}")
        print(f"   Problemas: {', '.join(problems)}")
        
        # Determinar ruta de salida
        if replace_originals:
            # Crear backup del original
            backup_path = video_path.replace('.mp4', '_backup.mp4')
            os.rename(video_path, backup_path)
            output_path = video_path
            print(f"   💾 Backup creado: {os.path.basename(backup_path)}")
        else:
            output_path = video_path.replace('.mp4', '_fixed.mp4')
        
        # Corregir video
        success, result = fix_video_encoding(video_path if not replace_originals else backup_path, output_path)
        
        if success:
            fixed_count += 1
            
            if replace_originals:
                # Eliminar backup si la corrección fue exitosa
                os.remove(backup_path)
                print(f"   🗑️  Backup eliminado (corrección exitosa)")
        else:
            print(f"   ❌ Error: {result}")
            
            if replace_originals:
                # Restaurar backup si falló
                os.rename(backup_path, video_path)
                print(f"   🔄 Original restaurado desde backup")
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTADO FINAL:")
    print(f"   ✅ Videos corregidos: {fixed_count}/{len(videos_to_fix)}")
    print(f"   📁 Videos procesados en total: {len(videos_to_fix)}")
    
    if fixed_count == len(videos_to_fix):
        print("🎉 ¡TODOS LOS VIDEOS FUERON CORREGIDOS EXITOSAMENTE!")
        print("   ✅ Ahora todos los videos son compatibles con cualquier reproductor")
        print("   ✅ Optimizados para redes sociales y streaming")
    else:
        print("⚠️  Algunos videos no pudieron ser corregidos")
        print("💡 Verifica que FFmpeg esté instalado correctamente")

def main():
    """Función principal"""
    
    print("🔧 CORRECTOR DE CODIFICACIÓN DE VIDEOS")
    print("Convierte videos a formato ultra compatible")
    print("=" * 50)
    
    # Carpetas donde buscar videos
    video_folders = [
        'videos/dynamic',
        'videos/processed',
        'generated/videos'
    ]
    
    # Verificar si FFmpeg está disponible
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ FFmpeg no está disponible")
            print("💡 Instala FFmpeg para usar este script")
            return
    except:
        print("❌ FFmpeg no está instalado")
        print("💡 Instala FFmpeg desde: https://ffmpeg.org/download.html")
        return
    
    print("✅ FFmpeg disponible")
    
    # Preguntar si reemplazar originales
    print("\n¿Cómo quieres proceder?")
    print("1. Crear videos corregidos (mantener originales)")
    print("2. Reemplazar videos originales (crear backup)")
    
    try:
        choice = input("\nElige una opción (1 o 2): ").strip()
        replace_originals = choice == '2'
        
        if replace_originals:
            print("⚠️  ATENCIÓN: Se crearán backups antes de reemplazar")
        else:
            print("ℹ️  Se crearán archivos '_fixed.mp4'")
        
        # Ejecutar corrección masiva
        batch_fix_videos(video_folders, replace_originals)
        
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()