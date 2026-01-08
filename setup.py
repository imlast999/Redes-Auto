#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuración inicial para Redes Auto
Automatiza la creación de directorios y verificación de dependencias
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Mostrar header del script"""
    print("🚀 CONFIGURACIÓN INICIAL - REDES AUTO")
    print("=" * 50)
    print("Este script configurará automáticamente el proyecto")
    print()

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando versión de Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_ffmpeg():
    """Verificar si FFmpeg está instalado"""
    print("\n🎬 Verificando FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg instalado correctamente")
            return True
        else:
            print("❌ FFmpeg no funciona correctamente")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg no está instalado")
        print_ffmpeg_instructions()
        return False
    except Exception as e:
        print(f"❌ Error verificando FFmpeg: {e}")
        return False

def print_ffmpeg_instructions():
    """Mostrar instrucciones de instalación de FFmpeg"""
    system = platform.system().lower()
    
    print("\n📋 INSTRUCCIONES DE INSTALACIÓN DE FFMPEG:")
    
    if system == "windows":
        print("   1. Descargar desde: https://ffmpeg.org/download.html")
        print("   2. Extraer en C:\\ffmpeg")
        print("   3. Agregar C:\\ffmpeg\\bin al PATH del sistema")
        print("   4. Reiniciar la terminal")
    elif system == "darwin":  # macOS
        print("   1. Instalar Homebrew: https://brew.sh")
        print("   2. Ejecutar: brew install ffmpeg")
    else:  # Linux
        print("   1. Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("   2. CentOS/RHEL: sudo yum install ffmpeg")
        print("   3. Arch: sudo pacman -S ffmpeg")

def create_directories():
    """Crear estructura de directorios"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        'uploads',
        'generated/images',
        'generated/audio',
        'generated/videos',
        'generated/scripts',
        'generated/subtitles',
        'generated/templates',
        'generated/dynamic_images',
        'videos/processed',
        'videos/dynamic',
        'static/uploads',
        'logs'
    ]
    
    created_count = 0
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Creado: {directory}")
            created_count += 1
        else:
            print(f"   ℹ️  Ya existe: {directory}")
    
    print(f"\n📊 Directorios creados: {created_count}/{len(directories)}")

def check_env_file():
    """Verificar archivo .env"""
    print("\n🔑 Verificando archivo de configuración...")
    
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        return True
    elif os.path.exists('.env.example'):
        print("⚠️  Archivo .env no encontrado")
        print("📋 Copiando .env.example a .env...")
        
        try:
            with open('.env.example', 'r', encoding='utf-8') as source:
                content = source.read()
            
            with open('.env', 'w', encoding='utf-8') as target:
                target.write(content)
            
            print("✅ Archivo .env creado desde .env.example")
            print("⚠️  IMPORTANTE: Edita el archivo .env con tus claves API")
            return True
        except Exception as e:
            print(f"❌ Error creando .env: {e}")
            return False
    else:
        print("❌ No se encontró .env.example")
        return False

def install_dependencies():
    """Instalar dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ Archivo requirements.txt no encontrado")
        return False
    
    try:
        print("   Ejecutando: pip install -r requirements.txt")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Dependencias instaladas correctamente")
            return True
        else:
            print(f"❌ Error instalando dependencias: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print("❌ Timeout instalando dependencias")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_tests():
    """Ejecutar pruebas básicas"""
    print("\n🧪 Ejecutando pruebas básicas...")
    
    # Verificar importaciones principales
    try:
        import flask
        print("   ✅ Flask importado correctamente")
    except ImportError:
        print("   ❌ Error importando Flask")
        return False
    
    try:
        from utils.video_processor import VideoProcessor
        print("   ✅ VideoProcessor importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando VideoProcessor: {e}")
        return False
    
    # Verificar estructura de archivos principales
    main_files = [
        'app_flask.py',
        'utils/video_processor.py',
        'utils/dynamic_video_processor.py',
        'config/api_config.py'
    ]
    
    for file in main_files:
        if os.path.exists(file):
            print(f"   ✅ {file} encontrado")
        else:
            print(f"   ❌ {file} no encontrado")
            return False
    
    return True

def print_next_steps():
    """Mostrar próximos pasos"""
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Editar el archivo .env con tus claves API")
    print("2. Instalar FFmpeg si no está instalado")
    print("3. Ejecutar: python app_flask.py")
    print("4. Abrir http://localhost:5000 en tu navegador")
    print("\n📚 Consulta INSTALACION_Y_CONFIGURACION.md para más detalles")

def main():
    """Función principal"""
    print_header()
    
    # Verificaciones
    if not check_python_version():
        sys.exit(1)
    
    ffmpeg_ok = check_ffmpeg()
    
    # Configuración
    create_directories()
    env_ok = check_env_file()
    
    # Instalación de dependencias
    deps_ok = install_dependencies()
    
    # Pruebas
    if deps_ok:
        tests_ok = run_tests()
    else:
        tests_ok = False
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DE LA CONFIGURACIÓN:")
    print(f"   🐍 Python: ✅")
    print(f"   🎬 FFmpeg: {'✅' if ffmpeg_ok else '❌'}")
    print(f"   🔑 Archivo .env: {'✅' if env_ok else '❌'}")
    print(f"   📦 Dependencias: {'✅' if deps_ok else '❌'}")
    print(f"   🧪 Pruebas: {'✅' if tests_ok else '❌'}")
    
    if ffmpeg_ok and env_ok and deps_ok and tests_ok:
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("✅ El proyecto está listo para usar")
        print_next_steps()
    else:
        print("\n⚠️  Configuración completada con advertencias")
        print("💡 Revisa los errores anteriores antes de continuar")
        if not ffmpeg_ok:
            print_ffmpeg_instructions()

if __name__ == "__main__":
    main()