# 🚀 Guía de Instalación y Configuración - Redes Auto

## 📋 Requisitos Previos

### Sistema Operativo
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+)

### Software Requerido
1. **Python 3.8+** - [Descargar aquí](https://www.python.org/downloads/)
2. **Git** - [Descargar aquí](https://git-scm.com/downloads)
3. **FFmpeg** - [Instrucciones de instalación](#instalación-de-ffmpeg)

## 🔧 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
# Clonar el proyecto
git clone https://github.com/imlast999/Redes-Auto.git

# Entrar al directorio
cd Redes-Auto
```

### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Si no existe requirements.txt, instalar manualmente:
pip install flask requests pillow openai anthropic google-generativeai moviepy pydub gtts langdetect schedule python-dotenv
```

### 4. Instalación de FFmpeg

#### Windows:
1. Descargar desde [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extraer en `C:\ffmpeg`
3. Agregar `C:\ffmpeg\bin` al PATH del sistema
4. Verificar: `ffmpeg -version`

#### macOS:
```bash
# Con Homebrew
brew install ffmpeg

# Verificar instalación
ffmpeg -version
```

#### Linux (Ubuntu/Debian):
```bash
# Instalar FFmpeg
sudo apt update
sudo apt install ffmpeg

# Verificar instalación
ffmpeg -version
```

### 5. Configuración de Variables de Entorno

#### Crear archivo .env
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus claves
nano .env  # o usar tu editor preferido
```

#### Variables Requeridas en .env:
```env
# APIs de IA (al menos una es requerida)
OPENAI_API_KEY=tu_clave_openai_aqui
ANTHROPIC_API_KEY=tu_clave_anthropic_aqui
GOOGLE_API_KEY=tu_clave_google_aqui

# Instagram (opcional, para publicación automática)
INSTAGRAM_USERNAME=tu_usuario_instagram
INSTAGRAM_PASSWORD=tu_password_instagram

# Configuración de la aplicación
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu_clave_secreta_aqui

# Configuración de archivos
MAX_CONTENT_LENGTH=100MB
UPLOAD_FOLDER=uploads
```

### 6. Crear Estructura de Directorios
```bash
# Crear directorios necesarios
mkdir -p uploads
mkdir -p generated/images
mkdir -p generated/audio
mkdir -p generated/videos
mkdir -p videos/processed
mkdir -p videos/dynamic
mkdir -p static/uploads
```

### 7. Verificar Instalación
```bash
# Probar la configuración
python test_new_video_generation.py

# Verificar codificación de videos
python test_video_encoding.py
```

## 🚀 Ejecutar la Aplicación

### Modo Desarrollo
```bash
# Activar entorno virtual (si no está activo)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Ejecutar la aplicación
python app_flask.py
```

La aplicación estará disponible en: `http://localhost:5000`

### Modo Producción
```bash
# Instalar servidor WSGI
pip install gunicorn

# Ejecutar con Gunicorn (Linux/macOS)
gunicorn -w 4 -b 0.0.0.0:5000 app_flask:app

# Para Windows, usar waitress
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app_flask:app
```

## 🔑 Obtener Claves de API

### OpenAI
1. Ir a [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Crear cuenta o iniciar sesión
3. Crear nueva clave API
4. Copiar la clave al archivo .env

### Anthropic (Claude)
1. Ir a [https://console.anthropic.com/](https://console.anthropic.com/)
2. Crear cuenta o iniciar sesión
3. Ir a "API Keys"
4. Crear nueva clave
5. Copiar la clave al archivo .env

### Google AI (Gemini)
1. Ir a [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Crear cuenta o iniciar sesión
3. Crear nueva clave API
4. Copiar la clave al archivo .env

## 📱 Funcionalidades Principales

### 1. Generación de Videos AI
- Crear scripts automáticamente
- Generar imágenes con IA
- Crear videos con audio TTS
- Videos dinámicos con múltiples imágenes

### 2. Procesamiento de Videos
- Redimensionar para redes sociales
- Agregar marcas de agua
- Subtítulos automáticos
- Optimización para Instagram

### 3. Publicación Automática
- Programar publicaciones
- Subir a Instagram automáticamente
- Gestión de biblioteca de contenido

### 4. Herramientas de Análisis
- Análisis de scripts
- Generación de personas realistas
- Plantillas de video personalizables

## 🛠️ Solución de Problemas Comunes

### Error: "FFmpeg no encontrado"
```bash
# Verificar instalación
ffmpeg -version

# Si no funciona, reinstalar FFmpeg
# Windows: Descargar y agregar al PATH
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### Error: "Módulo no encontrado"
```bash
# Reinstalar dependencias
pip install -r requirements.txt

# O instalar módulo específico
pip install nombre_del_modulo
```

### Error: "Puerto en uso"
```bash
# Cambiar puerto en app_flask.py
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Problemas de Codificación de Videos
```bash
# Ejecutar script de corrección
python fix_video_encoding.py

# Verificar compatibilidad
python test_video_encoding.py
```

## 📚 Estructura del Proyecto

```
Redes-Auto/
├── app_flask.py              # Aplicación principal Flask
├── requirements.txt          # Dependencias Python
├── .env.example             # Ejemplo de variables de entorno
├── .env                     # Variables de entorno (crear)
├── config/                  # Configuraciones
│   ├── api_config.py
│   └── free_api_alternatives.py
├── utils/                   # Utilidades y procesadores
│   ├── ai_script_generator.py
│   ├── ai_image_generator.py
│   ├── video_processor.py
│   ├── dynamic_video_processor.py
│   ├── instagram_publisher.py
│   └── ...
├── templates/               # Plantillas HTML
├── static/                  # Archivos estáticos
├── generated/               # Contenido generado
│   ├── images/
│   ├── audio/
│   └── videos/
├── videos/                  # Videos procesados
│   ├── processed/
│   └── dynamic/
└── uploads/                 # Archivos subidos
```

## 🎯 Próximos Pasos

1. **Configurar todas las claves API** en el archivo .env
2. **Probar la generación de contenido** con las herramientas incluidas
3. **Personalizar las plantillas** según tus necesidades
4. **Configurar la publicación automática** en Instagram
5. **Explorar las funcionalidades avanzadas** como videos dinámicos

## 📞 Soporte

Si encuentras problemas:
1. Revisa esta guía paso a paso
2. Verifica que todas las dependencias estén instaladas
3. Comprueba que las claves API sean válidas
4. Ejecuta los scripts de prueba para diagnosticar problemas

## 🔄 Actualizaciones

Para mantener el proyecto actualizado:
```bash
# Obtener últimos cambios
git pull origin main

# Actualizar dependencias si es necesario
pip install -r requirements.txt --upgrade
```

¡Listo para crear contenido automático para redes sociales! 🚀