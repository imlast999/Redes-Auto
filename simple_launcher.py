# -*- coding: utf-8 -*-
import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("🚀 Instagram Video Dashboard")
    print("=" * 40)
    
    try:
        # Intentar ejecutar streamlit
        print("🌐 Iniciando servidor...")
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], shell=True)
        
        # Esperar y abrir navegador
        print("⏳ Esperando servidor...")
        time.sleep(3)
        
        url = "http://localhost:8501"
        print(f"🌍 Abriendo: {url}")
        webbrowser.open(url)
        
        print("✅ Dashboard activo!")
        print("❌ NO cierres esta ventana")
        
        # Esperar
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Cerrando...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Presiona Enter...")

if __name__ == "__main__":
    main()