import streamlit as st
import os
import pandas as pd
from pathlib import Path
import tempfile
from datetime import datetime
import json

from utils.video_processor import VideoProcessor
from utils.instagram_api import InstagramAPI
from utils.file_manager import FileManager
from utils.scheduler import AutoScheduler
from config.settings import SETTINGS

# Initialize components
video_processor = VideoProcessor()
instagram_api = InstagramAPI()
file_manager = FileManager()
auto_scheduler = AutoScheduler()

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
            ["Dashboard", "Upload Videos", "Process Videos", "Manage Library", "Auto Scheduler", "Instagram Stats", "Settings"]
        )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload Videos":
        show_upload_page()
    elif page == "Process Videos":
        show_process_page()
    elif page == "Manage Library":
        show_library_page()
    elif page == "Auto Scheduler":
        show_scheduler_page()
    elif page == "Instagram Stats":
        show_instagram_stats()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    # Get video counts
    pending_count = len(file_manager.get_pending_videos())
    processed_count = len(file_manager.get_processed_videos())
    published_count = len(file_manager.get_published_videos())
    
    # Display metrics
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
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Get recent files
    recent_videos = file_manager.get_recent_activity()
    if recent_videos:
        df = pd.DataFrame(recent_videos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No recent activity found.")
    
    # Quick actions
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
    
    # Upload method selection
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
                    
                    # Save file to pending folder
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
    
    # Get pending videos
    pending_videos = file_manager.get_pending_videos()
    
    if not pending_videos:
        st.info("No pending videos to process.")
        return
    
    # Processing options
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
    
    # Video selection
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
            
            # Show video preview
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
    
    # Process selected videos
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
            # Process video
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
                # Move to processed folder
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
    
    # Folder tabs
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
                
                # Get file info
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
    
    # Estado del programador
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
    
    # Controles principales
    st.subheader("Controles del Bot")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Iniciar Bot", type="primary"):
            auto_scheduler.config["enabled"] = True
            auto_scheduler.save_config()
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
    
    # Configuración del bot
    st.subheader("Configuración")
    
    with st.form("scheduler_config"):
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
            # Actualizar configuración
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
            
            # Reprogramar si está activo
            if auto_scheduler.is_running:
                auto_scheduler.schedule_daily_posts()
            
            st.success("Configuración guardada!")
    
    # Próximas publicaciones programadas
    st.subheader("Próximas Publicaciones")
    next_times = auto_scheduler.get_next_scheduled_times()
    
    if next_times:
        for i, schedule_info in enumerate(next_times[:5]):
            st.write(f"📅 **Publicación {i+1}:** {schedule_info['next_run']}")
    else:
        st.info("No hay publicaciones programadas. Inicia el bot para programar automáticamente.")
    
    # Cola de publicación
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
                    # Guardar cola actualizada
                    with open("config/publish_queue.json", 'w') as f:
                        import json
                        json.dump(queue, f, indent=2)
                    st.rerun()
    else:
        st.info("No hay videos en la cola de publicación.")
    
    # Instrucciones
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

def show_instagram_stats():
    st.header("📊 Instagram Account Statistics")
    
    # Check if Instagram API is configured
    if not instagram_api.is_configured():
        st.warning("Instagram API not configured. Please add your Instagram credentials in the Settings page.")
        return
    
    try:
        # Get account info
        account_info = instagram_api.get_account_info()
        
        if account_info:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Followers", account_info.get('followers_count', 'N/A'))
            
            with col2:
                st.metric("Following", account_info.get('follows_count', 'N/A'))
            
            with col3:
                st.metric("Media Count", account_info.get('media_count', 'N/A'))
            
            st.subheader("Account Information")
            st.write(f"**Username:** {account_info.get('username', 'N/A')}")
            st.write(f"**Account Type:** {account_info.get('account_type', 'N/A')}")
        
        # Get recent media
        st.subheader("Recent Posts")
        recent_media = instagram_api.get_recent_media()
        
        if recent_media:
            for media in recent_media[:5]:  # Show last 5 posts
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
    
    # Instagram API Settings
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
    
    # Video Processing Settings
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
                'default_watermark': default_watermark,
                'default_quality': default_quality,
                'max_file_size': max_file_size
            }
            
            # Save settings
            with open('config/user_settings.json', 'w') as f:
                json.dump(new_settings, f, indent=2)
            
            st.success("Processing settings saved!")
    
    # Folder Management
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
    
    with col3:
        if st.button("Backup All Videos"):
            backup_path = file_manager.create_backup()
            if backup_path:
                st.success(f"Backup created at: {backup_path}")
            else:
                st.error("Failed to create backup")

if __name__ == "__main__":
    main()
