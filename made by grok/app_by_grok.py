import streamlit as st
import os
import pandas as pd
from pathlib import Path
import tempfile
from datetime import datetime
import json
import openai
from diffusers import StableDiffusionPipeline
import torch
from elevenlabs import generate, save
from moviepy.editor import TextClip, CompositeVideoClip, ImageClip, AudioFileClip
import whisper
import random

from utils.video_processor import VideoProcessor
from utils.instagram_api import InstagramAPI
from utils.instagram_publisher import InstagramPublisher
from utils.file_manager import FileManager
from utils.scheduler import AutoScheduler
from config.settings import SETTINGS

# Initialize components
video_processor = VideoProcessor()
instagram_api = InstagramAPI()
instagram_publisher = InstagramPublisher()
file_manager = FileManager()
auto_scheduler = AutoScheduler()

# Configura claves de IA (deberías mover esto a config/settings.py o .env)
openai.api_key = st.secrets.get("OPENAI_KEY", "tu_openai_key")
elevenlabs_api_key = st.secrets.get("ELEVENLABS_KEY", "tu_elevenlabs_key")

def main():
    st.set_page_config(
        page_title="Instagram Video Manager",
        page_icon="📹",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📹 Instagram Video Management Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Upload Videos", "Process Videos", "Generate AI Videos", "Manage Library", "Auto Scheduler", "Instagram Publisher", "Instagram Stats", "Settings"]
        )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload Videos":
        show_upload_page()
    elif page == "Process Videos":
        show_process_page()
    elif page == "Generate AI Videos":
        show_generate_ai_videos_page()
    elif page == "Manage Library":
        show_library_page()
    elif page == "Auto Scheduler":
        show_scheduler_page()
    elif page == "Instagram Publisher":
        show_publisher_page()
    elif page == "Instagram Stats":
        show_instagram_stats()
    elif page == "Settings":
        show_settings()

def show_generate_ai_videos_page():
    st.header("🤖 Generate AI Videos")
    st.markdown("Generate videos with AI-generated scripts, backgrounds, voiceovers, and subtitles.")
    
    # Temas de inversión
    temas_inversion = [
        "acciones para principiantes", "bienes raíces rentables", "crypto memecoins",
        "mindset de lujo", "inversiones en startups", "finanzas personales para el éxito"
    ]
    
    # Configuración de generación
    st.subheader("Generation Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        tema_seleccionado = st.selectbox("Select Theme", temas_inversion)
        duracion_max = st.slider("Max Video Duration (seconds)", 15, 60, 30)
        imagen_prompt = st.text_input(
            "Background Image Prompt",
            value="Luxurious mansion with gold accents, cinematic, vibrant colors, 1080x1920"
        )
    
    with col2:
        voz = st.selectbox("Voice", ["Adam", "Bella"], help="ElevenLabs voice")
        subtitulos = st.checkbox("Add Subtitles", value=True)
        cta_telegram = st.text_input("Telegram CTA", value="t.me/tucanalgratis")
    
    # Generar guion
    if st.button("Generate Script"):
        with st.spinner("Generating script..."):
            prompt = (
                f"Escribe un guion corto ({duracion_max} segundos) para un video de Instagram sobre {tema_seleccionado}. "
                f"Estilo motivacional, para principiantes. Incluye un call-to-action para {cta_telegram}. Máximo 100 palabras."
            )
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=100,
                temperature=0.7
            )
            guion = response.choices[0].text.strip()
            st.session_state["generated_script"] = guion
            st.session_state["script_path"] = f"scripts/guion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Guardar guion para revisión
            os.makedirs("scripts", exist_ok=True)
            with open(st.session_state["script_path"], "w") as f:
                f.write(guion)
            st.success("Script generated and saved!")
            st.text_area("Generated Script", guion, height=150)
    
    # Revisión y generación de video
    if "generated_script" in st.session_state:
        st.subheader("Review and Generate Video")
        approved = st.radio("Approve Script?", ["Yes", "No"], index=1)
        
        if approved == "Yes":
            if st.button("Generate Video", type="primary"):
                with st.spinner("Generating video..."):
                    try:
                        # Generar imagen de fondo
                        model_id = "stabilityai/stable-diffusion-2-1"
                        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
                        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
                        imagen = pipe(imagen_prompt).images[0]
                        imagen_path = "temp/fondo_temp.jpg"
                        os.makedirs("temp", exist_ok=True)
                        imagen.save(imagen_path)
                        
                        # Generar voz
                        audio = generate(
                            text=st.session_state["generated_script"],
                            voice=voz,
                            model="eleven_monolingual_v1",
                            api_key=elevenlabs_api_key
                        )
                        audio_path = "temp/voz_temp.mp3"
                        save(audio, audio_path)
                        
                        # Generar subtítulos
                        subtitulos = []
                        if subtitulos:
                            model = whisper.load_model("base")
                            result = model.transcribe(audio_path)
                            subtitulos = [(segment["start"], segment["end"], segment["text"]) for segment in result["segments"]]
                        
                        # Crear video
                        imagen_clip = ImageClip(imagen_path).set_duration(AudioFileClip(audio_path).duration)
                        audio_clip = AudioFileClip(audio_path)
                        clips = [imagen_clip]
                        
                        if subtitulos:
                            subtitulos_clips = [
                                TextClip(txt, fontsize=40, color='white', stroke_color='black', stroke_width=2)
                                .set_position(('center', 'bottom'))
                                .set_start(start)
                                .set_end(end)
                                for start, end, txt in subtitulos
                            ]
                            clips.extend(subtitulos_clips)
                        
                        video = CompositeVideoClip(clips).set_audio(audio_clip)
                        video_path = f"videos/pending/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                        os.makedirs("videos/pending", exist_ok=True)
                        video.write_videofile(video_path, fps=24)
                        
                        # Limpiar temporales
                        os.remove(imagen_path)
                        os.remove(audio_path)
                        
                        st.success(f"Video generated and saved to {video_path}")
                        st.video(video_path)
                        
                        # Integrar con tu flujo
                        file_manager.save_uploaded_file(video_path)
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error generating video: {str(e)}")

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    pending_count = len(file_manager.get_pending_videos())
    processed_count = len(file_manager.get_processed_videos())
    published_count = len(file_manager.get_published_videos())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pending Videos", pending_count)
    
    with col2:
        st.metric("Processed Videos", processed_count)
    
    with col3:
        st.metric("Published Videos", published_count)
    
    with col4:
        total_videos = pending_count + processed_count + published_count
        st.metric("Total Videos", total_videos)
    
    st.subheader("Recent Activity")
    recent_videos = file_manager.get_recent_activity()
    if recent_videos:
        df = pd.DataFrame(recent_videos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No recent activity found.")
    
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎬 Process All Pending", use_container_width=True):
            st.switch_page("Process Videos")
    
    with col2:
        if st.button("📤 Upload New Videos", use_container_width=True):
            st.switch_page("Upload Videos")
    
    with col3:
        if st.button("📚 Manage Library", use_container_width=True):
            st.switch_page("Manage Library")

def show_upload_page():
    st.header("📤 Upload Videos")
    
    upload_method = st.radio(
        "Choose upload method:",
        ["Upload Files", "Select from Local Folder"]
    )
    
    if upload_method == "Upload Files":
        uploaded_files = st.file_uploader(
            "Choose video files",
            type=['mp4', 'avi', 'mov', 'mkv'],
            accept_multiple_files=True,
            help="Select one or more video files to upload"
        )
        
        if uploaded_files:
            if st.button("Upload Videos"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Uploading {uploaded_file.name}...")
                    file_path = file_manager.save_uploaded_file(uploaded_file)
                    
                    if file_path:
                        st.success(f"✅ {uploaded_file.name} uploaded successfully")
                    else:
                        st.error(f"❌ Failed to upload {uploaded_file.name}")
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.text("Upload complete!")
                st.rerun()
    
    else:
        st.subheader("Select from Local Folder")
        folder_path = st.text_input(
            "Enter folder path:",
            placeholder="/path/to/your/videos"
        )
        
        if folder_path and os.path.exists(folder_path):
            video_files = file_manager.scan_folder_for_videos(folder_path)
            
            if video_files:
                st.write(f"Found {len(video_files)} video files:")
                selected_files = st.multiselect(
                    "Select files to import:",
                    video_files,
                    default=video_files
                )
                
                if st.button("Import Selected Files"):
                    success_count = 0
                    for file_path in selected_files:
                        if file_manager.copy_video_to_pending(file_path):
                            success_count += 1
                    
                    st.success(f"✅ Imported {success_count} of {len(selected_files)} files")
                    st.rerun()
            else:
                st.warning("No video files found in the specified folder.")
        elif folder_path:
            st.error("Folder path does not exist.")

def show_process_page():
    st.header("🎬 Process Videos")
    
    pending_videos = file_manager.get_pending_videos()
    
    if not pending_videos:
        st.info("No pending videos to process.")
        return
    
    st.subheader("Processing Options")
    col1, col2 = st.columns(2)
    
    with col1:
        add_watermark = st.checkbox("Add Watermark", value=True)
        watermark_text = "@yourusername"
        watermark_position = "bottom-right"
        if add_watermark:
            watermark_text = st.text_input("Watermark Text", value="@yourusername")
            watermark_position = st.selectbox(
                "Watermark Position",
                ["bottom-right", "bottom-left", "top-right", "top-left", "center"]
            )
    
    with col2:
        resize_video = st.checkbox("Resize for Instagram", value=True)
        aspect_ratio = "9:16 (Stories/Reels)"
        quality = "Medium"
        if resize_video:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["9:16 (Stories/Reels)", "1:1 (Square)", "4:5 (Portrait)"]
            )
            quality = st.selectbox("Quality", ["High", "Medium", "Low"])
    
    st.subheader("Select Videos to Process")
    selected_videos = []
    select_all = st.checkbox("Select All")
    
    for video in pending_videos:
        video_name = os.path.basename(video)
        if select_all:
            is_selected = True
        else:
            is_selected = st.checkbox(video_name, key=f"video_{video_name}")
        
        if is_selected:
            selected_videos.append(video)
            with st.expander(f"Preview: {video_name}"):
                try:
                    video_info = video_processor.get_video_info(video)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.video(video)
                    
                    with col2:
                        st.write("**Video Information:**")
                        st.write(f"Duration: {video_info.get('duration', 'Unknown')} seconds")
                        st.write(f"Resolution: {video_info.get('width', 'Unknown')}x{video_info.get('height', 'Unknown')}")
                        st.write(f"FPS: {video_info.get('fps', 'Unknown')}")
                        st.write(f"Size: {video_info.get('size', 'Unknown')} MB")
                
                except Exception as e:
                    st.error(f"Could not load video preview: {str(e)}")
    
    if selected_videos and st.button("🎬 Process Selected Videos", type="primary"):
        process_videos(selected_videos, add_watermark, resize_video, watermark_text if add_watermark else None, 
                      watermark_position if add_watermark else None, aspect_ratio if resize_video else None, 
                      quality if resize_video else None)

def process_videos(videos, add_watermark, resize_video, watermark_text, watermark_position, aspect_ratio, quality):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, video_path in enumerate(videos):
        video_name = os.path.basename(video_path)
        status_text.text(f"Processing {video_name}...")
        
        try:
            output_path = video_processor.process_video(
                video_path,
                add_watermark=add_watermark,
                watermark_text=watermark_text,
                watermark_position=watermark_position,
                resize=resize_video,
                aspect_ratio=aspect_ratio,
                quality=quality
            )
            
            if output_path:
                file_manager.move_to_processed(video_path, output_path)
                st.success(f"✅ {video_name} processed successfully")
            else:
                st.error(f"❌ Failed to process {video_name}")
        
        except Exception as e:
            st.error(f"❌ Error processing {video_name}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(videos))
    
    status_text.text("Processing complete!")
    st.rerun()

def show_library_page():
    st.header("📚 Video Library Management")
    
    tab1, tab2, tab3 = st.tabs(["Pending", "Processed", "Published"])
    
    with tab1:
        st.subheader("Pending Videos")
        pending_videos = file_manager.get_pending_videos()
        display_video_list(pending_videos, "pending")
    
    with tab2:
        st.subheader("Processed Videos")
        processed_videos = file_manager.get_processed_videos()
        display_video_list(processed_videos, "processed")
    
    with tab3:
        st.subheader("Published Videos")
        published_videos = file_manager.get_published_videos()
        display_video_list(published_videos, "published")

def display_video_list(videos, folder_type):
    if not videos:
        st.info(f"No {folder_type} videos found.")
        return
    
    for video in videos:
        video_name = os.path.basename(video)
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            
            with col1:
                st.write(f"**{video_name}**")
                try:
                    stat = os.stat(video)
                    size_mb = stat.st_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    st.caption(f"Size: {size_mb:.1f} MB | Modified: {modified_time.strftime('%Y-%m-%d %H:%M')}")
                except:
                    st.caption("Could not get file info")
            
            with col2:
                if st.button(f"Preview", key=f"preview_{video_name}"):
                    st.video(video)
            
            with col3:
                if folder_type == "processed":
                    if st.button("Mark Published", key=f"publish_{video_name}"):
                        file_manager.move_to_published(video)
                        st.rerun()
            
            with col4:
                if st.button("Delete", key=f"delete_{video_name}"):
                    if file_manager.delete_video(video):
                        st.success(f"Deleted {video_name}")
                        st.rerun()
            
            st.markdown("---")

def show_scheduler_page():
    st.header("🤖 Auto Scheduler - Bot de Publicación")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scheduler_status = "🟢 Activo" if auto_scheduler.is_running else "🔴 Inactivo"
        st.metric("Estado del Bot", scheduler_status)
    
    with col2:
        queue_count = len(auto_scheduler.get_publish_queue())
        st.metric("Videos en Cola", queue_count)
    
    with col3:
        published_count = len(file_manager.get_published_videos())
        st.metric("Videos Publicados", published_count)
    
    st.subheader("Controles del Bot")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Iniciar Bot", type="primary"):
            auto_scheduler.config["enabled"] = True
            auto{GPa0auto_scheduler.save_config()
            auto_scheduler.start_scheduler()
            st.success("Bot iniciado!")
            st.rerun()
    
    with col2:
        if st.button("⏸️ Pausar Bot"):
            auto_scheduler.stop_scheduler()
            auto_scheduler.config["enabled"] = False
            auto_scheduler.save_config()
            st.success("Bot pausado!")
            st.rerun()
    
    with col3:
        if st.button("📤 Publicar Ahora"):
            success, message = auto_scheduler.manual_publish_next()
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()
    
    st.subheader("Configuración")
    with st.form("scheduler/config"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuración General**")
            watermark_text = st.text_input("Texto de Marca de Agua", value=auto_scheduler.config.get("watermark_text", "@tuusuario"))
            auto_watermark = st.checkbox("Agregar marca de agua automáticamente", value=auto_scheduler.config.get("auto_watermark", True))
            auto_resize = st.checkbox("Redimensionar automáticamente", value=auto_scheduler.config.get("auto_resize", True))
            preferred_format = st.selectbox("Formato preferido", 
                                          ["9:16 (Stories/Reels)", "1:1 (Square)", "4:5 (Portrait)"],
                                          index=0)
        
        with col2:
            st.write("**Horarios de Publicación**")
            st.write("*Lunes a Viernes:*")
            morning_start = st.time_input("Inicio mañana", value=datetime.strptime("07:00", "%H:%M").time())
            morning_end = st.time_input("Fin mañana", value=datetime.strptime("09:00", "%H:%M").time())
            evening_start = st.time_input("Inicio tarde", value=datetime.strptime("18:00", "%H:%M").time())
            evening_end = st.time_input("Fin tarde", value=datetime.strptime("21:00", "%H:%M").time())
            
            st.write("*Fines de Semana:*")
            weekend_start = st.time_input("Inicio", value=datetime.strptime("10:00", "%H:%M").time())
            weekend_end = st.time_input("Fin", value=datetime.strptime("13:00", "%H:%M").time())
        
        if st.form_submit_button("💾 Guardar Configuración"):
            auto_scheduler.config.update({
                "watermark_text": watermark_text,
                "auto_watermark": auto_watermark,
                "auto_resize": auto_resize,
                "preferred_format": preferred_format,
                "weekday_slots": {
                    "morning": {"start": morning_start.strftime("%H:%M"), "end": morning_end.strftime("%H:%M")},
                    "evening": {"start": evening_start.strftime("%H:%M"), "end": evening_end.strftime("%H:%M")}
                },
                "weekend_slots": {
                    "midday": {"start": weekend_start.strftime("%H:%M"), "end": weekend_end.strftime("%H:%M")}
                }
            })
            auto_scheduler.save_config()
            if auto_scheduler.is_running:
                auto_scheduler.schedule_daily_posts()
            st.success("Configuración guardada!")
    
    st.subheader("Próximas Publicaciones")
    next_times = auto_scheduler.get_next_scheduled_times()
    
    if next_times:
        for i, schedule_info in enumerate(next_times[:5]):
            st.write(f"📅 **Publicación {i+1}:** {schedule_info['next_run']}")
    else:
        st.info("No hay publicaciones programadas. Inicia el bot para programar automáticamente.")
    
    st.subheader("Cola de Publicación")
    queue = auto_scheduler.get_publish_queue()
    
    if queue:
        for i, video_entry in enumerate(queue):
            video_name = os.path.basename(video_entry['video_path'])
            processed_time = video_entry['processed_at'][:19].replace('T', ' ')
            
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{i+1}. {video_name}**")
            
            with col2:
                st.caption(f"Procesado: {processed_time}")
            
            with col3:
                if st.button("🗑️", key=f"remove_queue_{i}"):
                    queue.pop(i)
                    with open("config/publish_queue.json", 'w') as f:
                        json.dump(queue, f, indent=2)
                    st.rerun()
    else:
        st.info("No hay videos en la cola de publicación.")
    
    with st.expander("📖 Cómo funciona el Bot"):
        st.markdown("""
        **El bot automático funciona así:**
        
        1. **Selección inteligente**: Busca videos en la carpeta 'pending' que contengan palabras relacionadas con lujo
        2. **Procesamiento automático**: Agrega marca de agua y redimensiona según tu configuración
        3. **Programación**: Publica 2 videos por día en horarios aleatorios dentro de tus slots configurados
        4. **Gestión de archivos**: Mueve automáticamente los videos procesados a 'published'
        
        **Horarios configurados:**
        - **Lunes a Viernes**: 2 videos (mañana 7-9am, tarde 6-9pm)
        - **Sábados y Domingos**: 1 video (mediodía 10am-1pm)
        
        **Palabras clave para selección automática:**
        luxury, lujo, rich, wealth, expensive, mansion, supercar, yacht, dubai, monaco, millionaire, billionaire, lifestyle, exclusive, premium
        """)

def show_publisher_page():
    st.header("📤 Instagram Publisher - Publicación Directa")
    
    with st.expander("⚠️ LIMITACIONES IMPORTANTES - Lee antes de usar"):
        st.markdown("""
        **🚨 La API de Instagram tiene estas limitaciones:**
        
        **✅ LO QUE SÍ FUNCIONA:**
        - Ver estadísticas de tu cuenta
        - Obtener información de posts existentes
        - Gestionar contenido ya publicado
        
        **❌ LO QUE NO FUNCIONA (Limitaciones de Instagram):**
        - **Publicación automática directa**: Instagram no permite bots que publiquen sin supervisión humana
        - **Cuentas personales**: SoloraspbianSolo funciona con cuentas Business/Creator verificadas
        - **Aprobación de Meta**: Necesitas aprobación de Meta para publicar automáticamente
        
        **🔧 ALTERNATIVAS RECOMENDADAS:**
        1. **Usar Creator Studio de Meta** - Permite programar publicaciones oficialmente
        2. **Buffer/Hootsuite** - Servicios especializados con permisos de Meta
        3. **Publicación manual** - El bot prepara todo, tú publicas manualmente
        
        **💡 CÓMO USAR ESTE DASHBOARD:**
        - El bot procesa y prepara tus videos automáticamente  
        - Los organiza en horarios optimizados
        - Tú publicas manualmente cuando sea conveniente
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        config_status = "🟢 Configurado" if instagram_publisher.is_configured() else "🔴 No configurado"
        st.metric("Estado API", config_status)
    
    with col2:
        account_info = instagram_publisher.get_account_type()
        account_type = account_info.get('account_type', 'Desconocido') if account_info else 'N/A'
        st.metric("Tipo de Cuenta", account_type)
    
    with col3:
        processed_count = len(file_manager.get_processed_videos())
        st.metric("Videos Listos", processed_count)
    
    st.subheader("Configuración de Instagram API")
    
    if not instagram_publisher.is_configured():
        st.warning("Para usar la publicación directa, necesitas configurar la API de Instagram.")
        
        with st.expander("📖 Cómo obtener credenciales de Instagram"):
            st.markdown("""
            **Para obtener las credenciales:**
            
            1. Ve a [Facebook Developers](https://developers.facebook.com/)
            2. Crea una aplicación
            3. Agrega el producto "Instagram Basic Display"
            4. Configura los permisos necesarios
            5. Obtén tu Access Token y User ID
            
            **NOTA:** Este proceso requiere que tengas una cuenta Business/Creator de Instagram.
            """)
        
        with st.form("instagram_publisher_config"):
            access_token = st.text_input("Instagram Access Token", type="password")
            user_id = st.text_input("Instagram User ID")
            
            if st.form_submit_button("💾 Guardar Configuración"):
                if access_token and user_id:
                    instagram_publisher.configure(access_token, user_id)
                    st.success("Configuración guardada!")
                    st.rerun()
                else:
                    st.error("Por favor completa ambos campos")
    
    else:
        account_info = instagram_publisher.get_account_type()
        
        if account_info:
            st.success(f"✅ Conectado como: **{account_info.get('username', 'Unknown')}**")
            st.info(f"Tipo de cuenta: **{account_info.get('account_type', 'Unknown')}**")
            
            if account_info.get('account_type') not in ['BUSINESS', 'CREATOR']:
                st.warning("⚠️ Tu cuenta no es Business/Creator. La publicación automática no funcionará.")
        
        st.subheader("Publicar Videos Procesados")
        
        processed_videos = file_manager.get_processed_videos()
        
        if processed_videos:
            selected_video = st.selectbox(
                "Seleccionar video para publicar:",
                processed_videos,
                format_func=lambda x: os.path.basename(x)
            )
            
            if selected_video:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    caption = st.text_area(
                        "Caption para Instagram:",
                        placeholder="Escribe aquí la descripción de tu video...\n\n#luxury #lifestyle #wealth",
                        height=100
                    )
                
                with col2:
                    st.video(selected_video)
                    is_valid, validation_msg = instagram_publisher.validate_video_for_instagram(selected_video)
                    
                    if is_valid:
                        st.success("✅ Video válido para Instagram")
                    else:
                        st.error(f"❌ {validation_msg}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📤 Publicar a Instagram", type="primary", disabled=not is_valid):
                        if caption.strip():
                            with st.spinner("Publicando video..."):
                                success, message = instagram_publisher.upload_video_to_instagram(selected_video, caption)
                            
                            if success:
                                st.success(message)
                                file_manager.move_to_published(selected_video)
                                st.rerun()
                            else:
                                st.error(f"Error: {message}")
                        else:
                            st.error("Por favor agrega una descripción")
                
                with col2:
                    if st.button("📁 Mover a Publicados"):
                        file_manager.move_to_published(selected_video)
                        st.success("Video movido a publicados")
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Eliminar Video"):
                        file_manager.delete_video(selected_video)
                        st.success("Video eliminado")
                        st.rerun()
        
        else:
            st.info("No hay videos procesados disponibles para publicar.")
            if st.button("🎬 Ir a Procesar Videos"):
                st.switch_page("Process Videos")
    
    st.subheader("📋 Límites de Instagram")
    limits = instagram_publisher.get_publishing_limits()
    
    for key, value in limits.items():
        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.subheader("📊 Estadísticas de Publicación")
    published_videos = file_manager.get_published_videos()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Videos Publicados Hoy", "0")  # Implementar contador real
        st.metric("Videos Publicados Esta Semana", len(published_videos))
    
    with col2:
        if published_videos:
            st.write("**Últimos videos publicados:**")
            for video in published_videos[-3:]:
                st.write(f"• {os.path.basename(video)}")

def show_instagram_stats():
    st.header("📊 Instagram Account Statistics")
    
    if not instagram_api.is_configured():
        st.warning("Instagram API not configured. Please add your Instagram credentials in the Settings page.")
        return
    
    try:
        account_info = instagram_api.get_account_info()
        
        if account_info:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Followers", account_info.get('followers_count', 'N/A'))
            
            with col2:
                st.metric("Following", account_info.get('follows_count', 'N/A'))
            
            with col3:
                st.metric("Media Count", account_info.get('media_count', 'N/A'))
            
 Lublin            st.subheader("Account Information")
            st.write(f"**Username:** {account_info.get('username', 'N/A')}")
            st.write(f"**Account Type:** {account_info.get('account_type', 'N/A')}")
        
        st.subheader("Recent Posts")
        recent_media = instagram_api.get_recent_media()
        
        if recent_media:
            for media in recent_media[:5]:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if media.get('media_url'):
                            st.image(media['media_url'], width=100)
                    
                    with col2:
                        st.write(f"**Caption:** {media.get('caption', 'No caption')[:100]}...")
                        st.write(f"**Posted:** {media.get('timestamp', 'Unknown')}")
                        st.write(f"**Type:** {media.get('media_type', 'Unknown')}")
                
                st.markdown("---")
        else:
            st.info("No recent media found.")
    
    except Exception as e:
        st.error(f"Error fetching Instagram data: {str(e)}")

def show_settings():
    st.header("⚙️ Settings")
    
    st.subheader("Instagram API Configuration")
    with st.form("instagram_api_form"):
        access_token = st.text_input(
            "Instagram Access Token",
            type="password",
            help="Your Instagram Basic Display API access token"
        )
        user_id = st.text_input(
            "Instagram User ID",
            help="Your Instagram user ID"
        )
        if st.form_submit_button("Save Instagram Settings"):
            instagram_api.configure(access_token, user_id)
            st.success("Instagram API settings saved!")
    
    st.subheader("Video Processing Settings")
    with st.form("processing_settings_form"):
        default_watermark = st.text_input(
            "Default Watermark Text",
            value=SETTINGS.get('default_watermark', '@yourusername')
        )
        default_quality = st.selectbox(
            "Default Video Quality",
            ["High", "Medium", "Low"],
            index=["High", "Medium", "Low"].index(SETTINGS.get('default_quality', 'Medium'))
        )
        max_file_size = st.number_input(
            "Maximum File Size (MB)",
            min_value=1,
            max_value=1000,
            value=SETTINGS.get('max_file_size', 100)
        )
        if st.form_submit_button("Save Processing Settings"):
            new_settings = {
                'default_watermark': defa
            ult_watermark,
                'default_quality': default_quality,
                'max_file_size': max_file_size
            }
            with open('config/user_settings.json', 'w') as f:
                json.dump(new_settings, f, indent=2)
            st.success("Processing settings saved!")
    
    st.subheader("Folder Management")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Processed Folder"):
            count = file_manager.clear_folder('processed')
            st.success(f"Cleared {count} files from processed folder")
    
    with col2:
        if st.button("Clear Published Folder"):
            count = file_manager.clear_folder('published')
            st.success(f"Cleared {count} files from published folder")
    
    with col3:+
        if st.button("Backup All Videos"):
            backup_path = file_manager.create_backup()
            if backup_path:
                st.success(f"Backup created at: {backup_path}")
            else:
                st.error("Failed to create backup")

if __name__ == "__main__":
    main()