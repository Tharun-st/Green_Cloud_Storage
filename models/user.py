"""User model"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from extensions import db

class User(UserMixin, db.Model):
    """User model for authentication and storage management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    # Storage management
    storage_quota = db.Column(db.BigInteger, default=Config.DEFAULT_STORAGE_QUOTA)
    storage_used = db.Column(db.BigInteger, default=0)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # GreenOps settings
    eco_mode_enabled = db.Column(db.Boolean, default=True)
    auto_cleanup_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    folders = db.relationship('Folder', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def get_storage_percentage(self):
        """Calculate storage usage percentage"""
        if self.storage_quota == 0:
            return 0
        return (self.storage_used / self.storage_quota) * 100
    
    def has_storage_space(self, file_size):
        """Check if user has enough storage space"""
        return (self.storage_used + file_size) <= self.storage_quota
    
    def update_storage_used(self):
        """Recalculate storage used from files"""
        from models.file import File
        total = db.session.query(db.func.sum(File.size)).filter(
            File.user_id == self.id,
            File.is_deleted == False
        ).scalar()
        self.storage_used = total or 0
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'
