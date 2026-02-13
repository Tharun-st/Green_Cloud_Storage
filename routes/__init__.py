"""Route blueprints for GreenCloud"""

from routes.auth import auth_bp
from routes.files import files_bp
from routes.folders import folders_bp
from routes.ai_agent import ai_bp
from routes.greenops import greenops_bp

__all__ = ['auth_bp', 'files_bp', 'folders_bp', 'ai_bp', 'greenops_bp']
