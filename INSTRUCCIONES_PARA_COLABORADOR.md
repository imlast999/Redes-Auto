# 👥 Instrucciones para Colaborador - Redes Auto

## 🎯 Resumen del Proyecto

**Redes Auto** es un sistema completo para generar automáticamente contenido para redes sociales usando IA. Incluye generación de scripts, imágenes, videos dinámicos, y publicación automática en Instagram.

## 🚀 Cómo Empezar

### 1. Clonar el Repositorio
```bash
git clone https://github.com/imlast999/Redes-Auto.git
cd Redes-Auto
```

### 2. Configuración Automática
```bash
# Ejecutar script de configuración (hace todo automáticamente)
python setup.py
```

### 3. Configurar APIs
```bash
# Editar archivo .env con tus claves
nano .env  # o usar tu editor preferido
```

### 4. Ejecutar
```bash
python app_flask.py
```

## 🔑 APIs Necesarias (Obtener Claves)

### Obligatorias (al menos una):
1. **OpenAI**: https://platform.openai.com/api-keys
2. **Anthropic**: https://console.anthropic.com/
3. **Google AI**: https://makersuite.google.com/app/apikey

### Opcionales:
- **Instagram**: Para publicación automática
- **Telegram**: Para notificaciones

## 📁 Estructura del Proyecto

```
Redes-Auto/
├── app_flask.py                    # 🚀 Aplicación principal Flask
├── setup.py                       # ⚙️ Configuración automática
├── requirements.txt               # 📦 Dependencias Python
├── .env.example                   # 🔑 Ejemplo de configuración
├── .gitignore                     # 🚫 Archivos a ignorar
├── README.md                      # 📖 Documentación principal
├── INSTALACION_Y_CONFIGURACION.md # 📋 Guía detallada
├── SOLUCION_CODIFICACION_VIDEOS.md # 🎬 Solución de videos
├── 
├── config/                        # ⚙️ Configuraciones
│   ├── api_config.py             # APIs principales
│   └── free_api_alternatives.py  # APIs gratuitas
├── 
├── utils/                         # 🛠️ Herramientas principales
│   ├── video_processor.py        # 🎬 Procesador de video regular
│   ├── dynamic_video_processor.py # 🎭 Procesador de video dinámico
│   ├── ai_script_generator.py    # 🤖 Generador de scripts IA
│   ├── ai_image_generator.py     # 🎨 Generador de imágenes IA
│   ├── instagram_publisher.py    # 📱 Publicador de Instagram
│   └── ... (otros procesadores)
├── 
├── templates/                     # 🌐 Interfaz web
│   ├── index.html                # 🏠 Página principal
│   ├── generate_ai_videos.html   # 🤖 Generación IA
│   ├── process_videos.html       # 🎬 Procesamiento
│   └── ... (otras páginas)
├── 
├── generated/                     # 📁 Contenido generado
│   ├── images/                   # 🖼️ Imágenes generadas
│   ├── audio/                    # 🎵 Audio generado
│   └── videos/                   # 🎬 Videos generados
├── 
└── videos/                        # 📁 Videos procesados
    ├── processed/                # ✅ Videos listos
    └── dynamic/                  # 🎭 Videos dinámicos
```

## 🎯 Funcionalidades Principales

### 1. **Generación de Videos IA** (`utils/ai_*`)
- Scripts automáticos con IA
- Imágenes personalizadas
- Audio text-to-speech
- Videos dinámicos con múltiples imágenes

### 2. **Procesamiento de Videos** (`utils/video_processor.py`)
- Redimensionado para redes sociales
- Marcas de agua
- Subtítulos automáticos
- **IMPORTANTE**: Codificación ultra compatible (problema resuelto)

### 3. **Videos Dinámicos** (`utils/dynamic_video_processor.py`)
- Múltiples imágenes con transiciones
- Sincronización con audio
- **RECIÉN CORREGIDO**: Problemas de codificación solucionados

### 4. **Publicación Automática** (`utils/instagram_publisher.py`)
- Subida automática a Instagram
- Programación de publicaciones
- Gestión de biblioteca de contenido

## 🔧 Problemas Resueltos Recientemente

### ✅ Codificación de Videos
- **Problema**: Videos no reproducibles en algunos dispositivos
- **Solución**: Implementada codificación ultra compatible
- **Archivos**: `SOLUCION_CODIFICACION_VIDEOS.md`
- **Scripts**: `fix_video_encoding.py`, `test_video_encoding.py`

### ✅ Videos Dinámicos
- **Problema**: Formato de pixel incorrecto
- **Solución**: Filtros FFmpeg mejorados
- **Resultado**: 100% compatibilidad garantizada

## 🛠️ Herramientas de Desarrollo

### Scripts de Prueba:
```bash
# Probar codificación de videos
python test_video_encoding.py

# Probar generación de nuevos videos
python test_new_video_generation.py

# Corregir videos existentes con problemas
python fix_video_encoding.py
```

### Configuración Automática:
```bash
# Configurar todo automáticamente
python setup.py
```

## 🎯 Áreas de Mejora / Próximas Tareas

### 1. **Interfaz de Usuario**
- Mejorar diseño de templates HTML
- Agregar más opciones de personalización
- Implementar drag & drop para archivos

### 2. **Funcionalidades IA**
- Agregar más proveedores de IA
- Mejorar prompts para mejor contenido
- Implementar análisis de tendencias

### 3. **Redes Sociales**
- Agregar soporte para TikTok
- Implementar YouTube Shorts
- Mejorar programación automática

### 4. **Optimizaciones**
- Mejorar velocidad de procesamiento
- Implementar cache inteligente
- Optimizar uso de memoria

## 🔍 Archivos Importantes a Revisar

### Configuración:
- `config/api_config.py` - Configuración de APIs
- `.env.example` - Variables de entorno

### Procesamiento:
- `utils/video_processor.py` - Procesamiento básico
- `utils/dynamic_video_processor.py` - Videos dinámicos
- `utils/ai_script_generator.py` - Generación de scripts

### Interfaz:
- `app_flask.py` - Aplicación principal
- `templates/` - Todas las páginas web

### Documentación:
- `INSTALACION_Y_CONFIGURACION.md` - Guía completa
- `SOLUCION_CODIFICACION_VIDEOS.md` - Problema resuelto

## 🚫 Archivos Eliminados (No Necesarios)

- `config.env.example` (duplicado)
- `.replit` (específico de Replit)
- `app.py` (duplicado de app_flask.py)
- `WARP.md` (no relacionado)
- `start.bat` (específico de Windows)
- Archivos generados en `generated/` y `videos/`

## 💡 Consejos para Desarrollo

### 1. **Entorno de Desarrollo**
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Testing**
- Siempre probar con `test_video_encoding.py` después de cambios
- Usar `setup.py` para verificar configuración
- Probar con diferentes tipos de archivos

### 3. **Git Workflow**
```bash
# Crear rama para nueva funcionalidad
git checkout -b nueva-funcionalidad

# Hacer cambios y commit
git add .
git commit -m "Descripción del cambio"

# Push y crear PR
git push origin nueva-funcionalidad
```

## 📞 Contacto y Soporte

- **Documentación**: Lee todos los archivos .md
- **Problemas**: Usa los scripts de diagnóstico
- **Dudas**: Revisa el código, está bien comentado

## 🎉 ¡Listo para Desarrollar!

El proyecto está completamente funcional y documentado. Los problemas principales ya están resueltos. ¡Puedes empezar a desarrollar nuevas funcionalidades inmediatamente!

**¡Éxito con el proyecto!** 🚀