"""File model"""

from datetime import datetime
import os
from extensions import db


class File(db.Model):
    """File model for uploaded files"""
    
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    
    # File information
    file_path = db.Column(db.String(500), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100))
    extension = db.Column(db.String(10))
    
    # Hash for duplicate detection
    file_hash = db.Column(db.String(64), index=True)  # SHA-256 hash
    
    # Ownership
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True, index=True)
    
    # Status
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    is_shared = db.Column(db.Boolean, default=False)
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Metadata
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Version control
    version = db.Column(db.Integer, default=1)
    parent_file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=True)
    
    # Relationships
    versions = db.relationship('File', backref=db.backref('parent_file', remote_side=[id]),
                               lazy='dynamic', cascade='all, delete-orphan')
    
    def get_size_formatted(self):
        """Get human-readable file size"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def get_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower().replace('.', '')
    
    def get_icon_class(self):
        """Get Font Awesome icon class based on file type"""
        ext = self.extension or self.get_extension()
        
        icon_map = {
            # Documents
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word', 'docx': 'fa-file-word',
            'xls': 'fa-file-excel', 'xlsx': 'fa-file-excel',
            'ppt': 'fa-file-powerpoint', 'pptx': 'fa-file-powerpoint',
            'txt': 'fa-file-alt',
            
            # Images
            'jpg': 'fa-file-image', 'jpeg': 'fa-file-image',
            'png': 'fa-file-image', 'gif': 'fa-file-image',
            'bmp': 'fa-file-image', 'svg': 'fa-file-image',
            
            # Videos
            'mp4': 'fa-file-video', 'avi': 'fa-file-video',
            'mov': 'fa-file-video', 'mkv': 'fa-file-video',
            
            # Audio
            'mp3': 'fa-file-audio', 'wav': 'fa-file-audio',
            'flac': 'fa-file-audio', 'ogg': 'fa-file-audio',
            
            # Archives
            'zip': 'fa-file-archive', 'rar': 'fa-file-archive',
            '7z': 'fa-file-archive', 'tar': 'fa-file-archive',
            
            # Code
            'py': 'fa-file-code', 'js': 'fa-file-code',
            'html': 'fa-file-code', 'css': 'fa-file-code',
            'java': 'fa-file-code', 'cpp': 'fa-file-code',
        }
        
        return icon_map.get(ext, 'fa-file')
    
    def soft_delete(self):
        """Soft delete file (move to trash)"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        """Restore file from trash"""
        self.is_deleted = False
        self.deleted_at = None
        db.session.commit()
    
    def hard_delete(self):
        """Permanently delete file from database and storage"""
        # Delete physical file
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        # Delete from database
        db.session.delete(self)
        db.session.commit()
    
    def update_access_time(self):
        """Update last accessed timestamp"""
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<File {self.original_filename}>'
