"""File service for file operations"""

import os
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db
from models.file import File
from models.folder import Folder
from models.user import User
from config import Config


class FileService:
    """Service for handling file operations"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
    
    def upload_file(self, file, folder_id=None, **kwargs):
        """Upload a file"""
        if not file or file.filename == '':
            raise ValueError('No file provided')
        
        # Check file extension
        if not self._allowed_file(file.filename):
            raise ValueError('File type not allowed')
        
        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        # Check storage quota
        if not self.user.has_storage_space(file_size):
            raise ValueError('Not enough storage space')
        
        # Generate secure filename
        original_filename = file.filename
        filename = self._generate_unique_filename(original_filename)
        
        # Create upload directory if doesn't exist
        upload_path = Config.UPLOAD_FOLDER
        if folder_id:
            folder = Folder.query.get(folder_id)
            # GLOBAL ACCESS: Allow uploads to any folder
            if folder:
                folder_path = folder.get_full_path().replace(' / ', '/')
                upload_path = os.path.join(Config.UPLOAD_FOLDER, str(self.user_id), folder_path)
        else:
            upload_path = os.path.join(Config.UPLOAD_FOLDER, str(self.user_id))
        
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        
        # Get file extension
        extension = os.path.splitext(original_filename)[1].lower().replace('.', '')
        
        # Create database record
        new_file = File(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            size=file_size,
            extension=extension,
            file_hash=file_hash,
            user_id=self.user_id,
            folder_id=folder_id,
            is_shared=kwargs.get('is_shared', False)
        )
        
        db.session.add(new_file)
        
        # Update user storage
        self.user.storage_used += file_size
        
        db.session.commit()
        
        return new_file
    
    def get_files(self, folder_id=None):
        """Get files in a folder"""
        # GLOBAL ACCESS: Show files from all users
        query = File.query.filter_by(
            is_deleted=False
        )
        
        if folder_id:
            query = query.filter_by(folder_id=folder_id)
        else:
            query = query.filter_by(folder_id=None)
        
        return query.order_by(File.created_at.desc()).all()
    
    def get_shared_files(self):
        """Get all shared files"""
        return File.query.filter_by(
            is_deleted=False,
            is_shared=True
        ).order_by(File.created_at.desc()).all()
    
    def get_folders(self, parent_id=None):
        """Get folders in a parent folder"""
        # GLOBAL ACCESS: Show folders from all users
        return Folder.query.filter_by(
            parent_id=parent_id,
            is_deleted=False
        ).order_by(Folder.name).all()
    
    def search_files(self, query):
        """Search files by name"""
        return File.query.filter(
            File.is_deleted == False,
            (File.user_id == self.user_id) | (File.is_shared == True),
            File.original_filename.ilike(f'%{query}%')
        ).order_by(File.created_at.desc()).all()
    
    def get_recent_files(self, limit=10):
        """Get recent files"""
        # GLOBAL ACCESS: Show recent files from everyone
        return File.query.filter_by(
            is_deleted=False
        ).order_by(File.created_at.desc()).limit(limit).all()
    
    def get_file_count(self):
        """Get total file count"""
        # GLOBAL COUNT or User count? 
        # For "Community" feel, let's show global count? 
        # Actually, user might want to know THEIR usage for quota.
        # Let's keep this as USER count for potential quota logic, but maybe dashboard needs global?
        # The user dashboard shows "Storage Used" which is personal.
        # But "Total Files" could be personal.
        # Let's keep these methods as "User Personal Stats" for now, as dashboard uses them for storage calc.
        # Wait, if "Total Files" on dashboard is meant to show community activity, I should change it.
        # But the User Dashboard usually shows "My Storage".
        # Let's leave these as user-specific for now to track QUOTA.
        # But `get_recent_files` DEFINITELY needs to be global for the "feed".
        return File.query.filter_by(
            is_deleted=False,
            user_id=self.user_id
        ).count()
    
    def get_folder_count(self):
        """Get total folder count"""
        return Folder.query.filter_by(
            is_deleted=False,
            user_id=self.user_id
        ).count()
    
    def get_storage_used(self):
        """Get storage used"""
        return self.user.storage_used
    
    def get_storage_percentage(self):
        """Get storage percentage"""
        return self.user.get_storage_percentage()
    
    def _allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    def _generate_unique_filename(self, filename):
        """Generate unique filename"""
        name, ext = os.path.splitext(filename)
        name = secure_filename(name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{name}_{timestamp}{ext}"
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
