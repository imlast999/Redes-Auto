# -*- coding: utf-8 -*-
"""
Gestor de dependencias automático para Instagram Video Dashboard
Instala automáticamente las librerías necesarias cuando se necesitan
"""

import subprocess
import sys
import importlib
from typing import Tuple, List

class DependencyManager:
    def __init__(self):
        self.required_packages = {
            'PIL': 'pillow',
            'gtts': 'gtts',
            'requests': 'requests',
            'flask': 'flask',
            'pandas': 'pandas'
        }
        
        self.optional_packages = {
            'moviepy': 'moviepy',
            'opencv': 'opencv-python',
            'numpy': 'numpy'
        }
    
    def check_and_install_package(self, package_name: str, pip_name: str = None) -> Tuple[bool, str]:
        """Verificar si un paquete está instalado y instalarlo si no lo está"""
        if pip_name is None:
            pip_name = package_name
        
        try:
            # Intentar importar el paquete
            importlib.import_module(package_name)
            return True, f"{package_name} ya está instalado"
        
        except ImportError:
            # El paquete no está instalado, intentar instalarlo
            try:
                print(f"Instalando {pip_name}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', pip_name
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    # Verificar que se instaló correctamente
                    try:
                        importlib.import_module(package_name)
                        return True, f"{package_name} instalado exitosamente"
                    except ImportError:
                        return False, f"Error: {package_name} se instaló pero no se puede importar"
                else:
                    return False, f"Error instalando {pip_name}: {result.stderr}"
            
            except subprocess.TimeoutExpired:
                return False, f"Timeout instalando {pip_name}"
            except Exception as e:
                return False, f"Error instalando {pip_name}: {str(e)}"
    
    def ensure_required_packages(self) -> Tuple[bool, List[str]]:
        """Asegurar que todos los paquetes requeridos están instalados"""
        results = []
        all_success = True
        
        for package, pip_name in self.required_packages.items():
            success, message = self.check_and_install_package(package, pip_name)
            results.append(message)
            if not success:
                all_success = False
        
        return all_success, results
    
    def install_optional_package(self, package_name: str) -> Tuple[bool, str]:
        """Instalar un paquete opcional"""
        if package_name in self.optional_packages:
            pip_name = self.optional_packages[package_name]
            return self.check_and_install_package(package_name, pip_name)
        else:
            return False, f"Paquete opcional {package_name} no reconocido"
    
    def check_system_requirements(self) -> dict:
        """Verificar requisitos del sistema"""
        requirements = {
            'python_version': sys.version,
            'pip_available': self._check_pip(),
            'ffmpeg_available': self._check_ffmpeg(),
            'packages_status': {}
        }
        
        # Verificar paquetes requeridos
        for package, pip_name in self.required_packages.items():
            try:
                importlib.import_module(package)
                requirements['packages_status'][package] = 'installed'
            except ImportError:
                requirements['packages_status'][package] = 'missing'
        
        return requirements
    
    def _check_pip(self) -> bool:
        """Verificar si pip está disponible"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _check_ffmpeg(self) -> bool:
        """Verificar si FFmpeg está disponible"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def get_installation_instructions(self) -> dict:
        """Obtener instrucciones de instalación para dependencias faltantes"""
        instructions = {
            'ffmpeg': {
                'windows': 'Descargar desde https://ffmpeg.org/download.html y agregar al PATH',
                'linux': 'sudo apt-get install ffmpeg',
                'macos': 'brew install ffmpeg'
            },
            'python_packages': {
                'command': f'{sys.executable} -m pip install -r requirements.txt',
                'individual': {
                    package: f'{sys.executable} -m pip install {pip_name}'
                    for package, pip_name in self.required_packages.items()
                }
            }
        }
        
        return instructions

# Instancia global
dependency_manager = DependencyManager()