# replit.md

## Overview

This is an Instagram Video Management Dashboard built with Streamlit that provides a comprehensive solution for processing, managing, and publishing videos to Instagram. The application allows users to upload videos, apply watermarks, resize content for different Instagram formats (stories, square, portrait), and manage their video library through different stages of the workflow (pending, processed, published).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The application uses Streamlit as the web framework, providing a multi-page dashboard interface with sidebar navigation. The main pages include Dashboard, Upload Videos, Process Videos, Manage Library, Instagram Stats, and Settings. The UI is designed with a wide layout and expandable sidebar for easy navigation between different video management functions.

### Backend Architecture
The system follows a modular architecture with separate utility classes handling specific responsibilities:

- **VideoProcessor**: Handles video manipulation using MoviePy and OpenCV for operations like watermarking, resizing, and format conversion
- **InstagramAPI**: Manages Instagram API interactions for publishing and retrieving statistics
- **FileManager**: Handles file operations and organizes videos into workflow stages (pending, processed, published)

### Data Storage Solutions
The application uses a file-based storage system with organized folder structures:
- Videos are categorized into three main folders: pending, processed, and published
- Configuration data is stored in JSON files (user_settings.json, instagram_config.json)
- No traditional database is used; metadata is managed through file system organization

### Configuration Management
Settings are managed through a layered configuration system:
- Default settings are defined in code with sensible defaults
- User customizations are saved to JSON configuration files
- Settings include video quality presets, Instagram format specifications, watermark styling, and processing parameters

### Video Processing Pipeline
The video processing workflow supports:
- Multiple input formats (MP4, AVI, MOV, MKV, etc.)
- Watermark application with customizable positioning and styling
- Aspect ratio conversion for Instagram formats (1080x1920 stories, 1080x1080 square, 1080x1350 portrait)
- Quality compression with predefined bitrate settings (High: 8000k, Medium: 4000k, Low: 2000k)

## External Dependencies

### Third-party Libraries
- **Streamlit**: Web application framework for the user interface
- **MoviePy**: Video processing and editing capabilities
- **OpenCV (cv2)**: Computer vision operations for video manipulation
- **NumPy**: Numerical operations supporting video processing
- **Pandas**: Data manipulation for analytics and file management
- **Requests**: HTTP client for Instagram API communications

### Instagram API Integration
The application integrates with Instagram's Graph API for:
- Publishing videos to Instagram accounts
- Retrieving account statistics and analytics
- Managing authentication tokens and user credentials

### File System Dependencies
- Local file system for video storage and organization
- Temporary file management for processing operations
- Asset management for watermarks and configuration files

### Environment Variables
The system expects Instagram API credentials to be provided via environment variables:
- `INSTAGRAM_ACCESS_TOKEN`: For API authentication
- `INSTAGRAM_USER_ID`: For account identification