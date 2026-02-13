"""Folder model"""

from datetime import datetime
from extensions import db


class Folder(db.Model):
    """Folder model for organizing files"""
    
    __tablename__ = 'folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    
    # Ownership
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True, index=True)
    path = db.Column(db.String(1000))  # Full path for quick lookups
    
    # Metadata
    color = db.Column(db.String(7), default='#3498db')  # Hex color for UI
    is_shared = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    children = db.relationship('Folder', backref=db.backref('parent', remote_side=[id]), 
                               lazy='dynamic', cascade='all, delete-orphan')
    files = db.relationship('File', backref='folder', lazy='dynamic')
    
    def get_full_path(self):
        """Get full path including all parent folders"""
        if self.parent_id is None:
            return self.name
        
        path_parts = [self.name]
        current = self
        
        while current.parent_id is not None:
            current = Folder.query.get(current.parent_id)
            if current:
                path_parts.insert(0, current.name)
            else:
                break
        
        return ' / '.join(path_parts)
    
    def get_breadcrumbs(self):
        """Get breadcrumb trail for navigation"""
        breadcrumbs = [{'id': self.id, 'name': self.name}]
        current = self
        
        while current.parent_id is not None:
            current = Folder.query.get(current.parent_id)
            if current:
                breadcrumbs.insert(0, {'id': current.id, 'name': current.name})
            else:
                break
        
        return breadcrumbs
    
    def get_file_count(self):
        """Get total number of files in this folder and subfolders"""
        from models.file import File
        count = File.query.filter_by(folder_id=self.id, is_deleted=False).count()
        
        for child in self.children.filter_by(is_deleted=False):
            count += child.get_file_count()
        
        return count
    
    def soft_delete(self):
        """Soft delete folder and all contents"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        
        # Soft delete all files in folder
        from models.file import File
        for file in self.files.filter_by(is_deleted=False):
            file.soft_delete()
        
        # Soft delete all subfolders
        for child in self.children.filter_by(is_deleted=False):
            child.soft_delete()
        
        db.session.commit()
    
    def restore(self):
        """Restore folder and all contents"""
        self.is_deleted = False
        self.deleted_at = None
        
        # Restore all files
        from models.file import File
        for file in self.files.filter_by(is_deleted=True):
            file.restore()
        
        # Restore all subfolders
        for child in self.children.filter_by(is_deleted=True):
            child.restore()
        
        db.session.commit()
    
    def __repr__(self):
        return f'<Folder {self.name}>'
