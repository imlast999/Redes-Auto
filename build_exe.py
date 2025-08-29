#!/usr/bin/env python3
"""
Script para generar ejecutable del Dashboard de Instagram
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Instalar PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado")

def create_spec_file():
    """Crear archivo de especificación para PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('utils/', 'utils/'),
        ('config/', 'config/'),
        ('videos/', 'videos/'),
        ('assets/', 'assets/'),
        ('.streamlit/', '.streamlit/'),
    ],
    hiddenimports=[
        'streamlit',
        'schedule',
        'pandas',
        'requests',
        'cv2',
        'moviepy',
        'moviepy.editor',
        'PIL',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Instagram_Video_Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('dashboard.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Archivo de especificación creado")

def create_launcher_script():
    """Crear script launcher que abre el navegador automáticamente"""
    launcher_content = '''
import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path

def main():
    print("🚀 Iniciando Instagram Video Dashboard...")
    
    # Obtener la ruta del ejecutable
    if getattr(sys, 'frozen', False):
        # Ejecutable creado con PyInstaller
        bundle_dir = sys._MEIPASS
    else:
        # Script normal de Python
        bundle_dir = Path(__file__).parent
    
    # Cambiar al directorio del bundle
    os.chdir(bundle_dir)
    
    print("📂 Directorio de trabajo:", os.getcwd())
    
    # Ejecutar Streamlit
    try:
        print("🌐 Iniciando servidor web...")
        
        # Crear proceso de Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Esperar un poco para que el servidor inicie
        time.sleep(3)
        
        # Abrir navegador
        url = "http://localhost:8501"
        print(f"🌍 Abriendo navegador en: {url}")
        webbrowser.open(url)
        
        print("✅ Dashboard iniciado correctamente!")
        print("⚠️  NO CIERRES esta ventana - mantiene el servidor activo")
        print("🔴 Para cerrar el dashboard, presiona Ctrl+C")
        
        # Mantener el proceso vivo
        process.wait()
        
    except KeyboardInterrupt:
        print("\\n🛑 Cerrando Dashboard...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")
        input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    main()
'''
    
    with open('launcher.py', 'w') as f:
        f.write(launcher_content)
    
    print("✅ Script launcher creado")

def build_executable():
    """Construir el ejecutable"""
    print("🔨 Construyendo ejecutable...")
    print("⏳ Esto puede tomar varios minutos...")
    
    try:
        # Usar el archivo spec personalizado
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "dashboard.spec"
        ])
        print("✅ Ejecutable creado exitosamente!")
        print("📁 Ubicación: dist/Instagram_Video_Dashboard.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al construir ejecutable: {e}")
        return False
    
    return True

def create_readme():
    """Crear archivo README para el ejecutable"""
    readme_content = '''# Instagram Video Dashboard - Ejecutable

## 🚀 Cómo usar

1. **Ejecutar el Dashboard:**
   - Haz doble clic en `Instagram_Video_Dashboard.exe`
   - El navegador se abrirá automáticamente
   - El dashboard estará disponible en http://localhost:8501

2. **Configurar el Bot:**
   - Ve a la página "Auto Scheduler"
   - Configura tus horarios de publicación
   - Agrega tu marca de agua personalizada
   - Haz clic en "🚀 Iniciar Bot"

3. **Agregar Videos:**
   - Ve a "Upload Videos"
   - Sube tus videos de vida lujosa
   - El bot los procesará automáticamente

## 📂 Estructura de Carpetas

- `videos/pending/` - Videos esperando ser procesados
- `videos/processed/` - Videos listos para publicar
- `videos/published/` - Videos ya publicados

## ⏰ Horarios de Publicación

- **Lunes a Viernes:** 2 videos (7-9am y 6-9pm)
- **Sábados y Domingos:** 1 video (10am-1pm)

## 🔧 Solución de Problemas

1. **El navegador no se abre:**
   - Abre manualmente: http://localhost:8501

2. **Error al iniciar:**
   - Verifica que no haya otro programa usando el puerto 8501
   - Reinicia el ejecutable

3. **Videos no se procesan:**
   - Verifica que los videos estén en formato MP4, AVI, MOV o MKV
   - Asegúrate de que los nombres contengan palabras relacionadas con lujo

## 🤖 Palabras Clave para Selección Automática

El bot busca estas palabras en los nombres de archivos:
luxury, lujo, rich, wealth, expensive, mansion, supercar, yacht, dubai, monaco, millionaire, billionaire, lifestyle, exclusive, premium

## 📞 Soporte

Para problemas técnicos, revisa los logs en la consola del ejecutable.
'''
    
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README creado")

def main():
    """Función principal"""
    print("🎯 Generador de Ejecutable - Instagram Video Dashboard")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encontró app.py")
        print("   Ejecuta este script desde el directorio del proyecto")
        return
    
    # Paso 1: Instalar PyInstaller
    install_pyinstaller()
    
    # Paso 2: Crear archivos necesarios
    create_spec_file()
    create_launcher_script()
    
    # Paso 3: Construir ejecutable
    if build_executable():
        # Paso 4: Crear documentación
        create_readme()
        
        print("\\n🎉 ¡Ejecutable creado exitosamente!")
        print("📁 Ubicación: dist/Instagram_Video_Dashboard.exe")
        print("📖 Lee el archivo README.txt para instrucciones")
        print("\\n💡 Consejos:")
        print("   - Copia toda la carpeta 'dist' donde quieras usar el dashboard")
        print("   - El ejecutable incluye todas las dependencias necesarias")
        print("   - Funciona sin necesidad de instalar Python")
    else:
        print("\\n❌ Error al crear el ejecutable")

if __name__ == "__main__":
    main()