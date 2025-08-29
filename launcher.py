
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
        print("\n🛑 Cerrando Dashboard...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error al iniciar: {e}")
        input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    main()
