# -*- coding: utf-8 -*-
"""
Instagram Video Dashboard - Versión Standalone
Esta versión funciona directamente sin PyInstaller
"""

import subprocess
import webbrowser
import time
import sys
import os
from threading import Thread

def check_dependencies():
    """Verificar e instalar dependencias necesarias"""
    required_packages = ['streamlit', 'schedule', 'pandas', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - faltante")
    
    if missing_packages:
        print(f"\n📦 Instalando {len(missing_packages)} paquetes...")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                    capture_output=True)
                print(f"✅ {package} instalado")
            except subprocess.CalledProcessError:
                print(f"❌ Error instalando {package}")
                return False
    
    return True

def start_streamlit_server():
    """Iniciar servidor Streamlit"""
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost", 
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        return subprocess.Popen(cmd, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None

def wait_for_server(max_attempts=30):
    """Esperar a que el servidor esté listo"""
    import urllib.request
    import urllib.error
    
    for i in range(max_attempts):
        try:
            with urllib.request.urlopen("http://localhost:8501/_stcore/health") as response:
                if response.status == 200:
                    return True
        except:
            pass
        time.sleep(1)
    
    return False

def main():
    """Función principal"""
    print("🎯 Instagram Video Dashboard")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encontró app.py")
        print("   Asegúrate de ejecutar este script desde el directorio del proyecto")
        input("\nPresiona Enter para cerrar...")
        return
    
    # Verificar dependencias
    print("🔍 Verificando dependencias...")
    if not check_dependencies():
        print("❌ Error con las dependencias")
        input("\nPresiona Enter para cerrar...")
        return
    
    print("✅ Dependencias listas")
    
    # Iniciar servidor
    print("\n🌐 Iniciando servidor Streamlit...")
    server_process = start_streamlit_server()
    
    if not server_process:
        print("❌ Error iniciando el servidor")
        input("\nPresiona Enter para cerrar...")
        return
    
    # Esperar a que el servidor esté listo
    print("⏳ Esperando que el servidor inicie...")
    if wait_for_server():
        print("✅ Servidor listo!")
        
        # Abrir navegador
        url = "http://localhost:8501"
        print(f"🌍 Abriendo navegador: {url}")
        webbrowser.open(url)
        
        print("\n" + "="*50)
        print("✅ DASHBOARD ACTIVO!")
        print("📱 Usa tu navegador para acceder al dashboard")
        print("⚠️  NO CIERRES esta ventana")
        print("🔴 Para cerrar el dashboard, presiona Ctrl+C")
        print("="*50)
        
        try:
            # Mantener vivo
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Cerrando dashboard...")
            server_process.terminate()
            server_process.wait()
    else:
        print("❌ El servidor no pudo iniciar correctamente")
        server_process.terminate()
        input("\nPresiona Enter para cerrar...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        input("\nPresiona Enter para cerrar...")