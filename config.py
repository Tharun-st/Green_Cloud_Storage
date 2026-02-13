import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'greencloud-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "database", "greencloud.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 
        'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp3', 'mp4',
        'avi', 'mov', 'csv', 'json', 'xml', 'html', 'css', 'js'
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Storage quota (in bytes)
    DEFAULT_STORAGE_QUOTA = 5 * 1024 * 1024 * 1024  # 5GB per user
    
    # GreenOps configuration
    GREENOPS_ENABLED = True
    AUTO_CLEANUP_DAYS = 30  # Days before trash auto-cleanup
    SESSION_TIMEOUT_MINUTES = 30  # Auto-logout after inactivity
    DUPLICATE_FILE_CHECK = True
    VERSION_RETENTION_DAYS = 90
    
    # AI Agent configuration
    AI_AGENT_ENABLED = False
    AI_AGENT_NAME = "GreenBot"
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Trash configuration
    TRASH_FOLDER = '.trash'
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.BASE_DIR, 'database'), exist_ok=True)
        os.makedirs(os.path.join(Config.UPLOAD_FOLDER, Config.TRASH_FOLDER), exist_ok=True)
