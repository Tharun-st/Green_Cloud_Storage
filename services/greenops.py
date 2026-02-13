"""GreenOps service - Sustainable computing features"""

from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models.user import User
from models.file import File
from models.folder import Folder
from config import Config


class GreenOpsService:
    """Service for GreenOps features and optimization"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
    
    def calculate_greenops_score(self):
        """Calculate GreenOps score (0-100)"""
        score = 0
        
        # Storage efficiency (30 points)
        storage_percentage = self.user.get_storage_percentage()
        if storage_percentage < 50:
            score += 30
        elif storage_percentage < 70:
            score += 20
        elif storage_percentage < 90:
            score += 10
        
        # Eco mode enabled (20 points)
        if self.user.eco_mode_enabled:
            score += 20
        
        # Auto cleanup enabled (15 points)
        if self.user.auto_cleanup_enabled:
            score += 15
        
        # No duplicates (15 points)
        duplicates = self.find_duplicate_files()
        if len(duplicates) == 0:
            score += 15
        elif len(duplicates) < 5:
            score += 10
        elif len(duplicates) < 10:
            score += 5
        
        # Trash management (10 points)
        trash_count = File.query.filter_by(user_id=self.user_id, is_deleted=True).count()
        if trash_count == 0:
            score += 10
        elif trash_count < 5:
            score += 7
        elif trash_count < 10:
            score += 4
        
        # Organization (10 points) - files in folders
        total_files = File.query.filter_by(user_id=self.user_id, is_deleted=False).count()
        files_in_folders = File.query.filter(
            File.user_id == self.user_id,
            File.is_deleted == False,
            File.folder_id != None
        ).count()
        
        if total_files > 0:
            org_percentage = (files_in_folders / total_files) * 100
            if org_percentage >= 80:
                score += 10
            elif org_percentage >= 50:
                score += 6
            elif org_percentage >= 30:
                score += 3
        else:
            score += 10  # No files yet, perfect score
        
        return min(score, 100)
    
    def get_suggestions(self):
        """Get optimization suggestions"""
        suggestions = []
        
        # Storage suggestions
        percentage = self.user.get_storage_percentage()
        if percentage > 90:
            suggestions.append("Critical: Storage almost full. Delete unused files immediately.")
        elif percentage > 70:
            suggestions.append("Warning: Storage usage is high. Consider cleanup.")
        
        # Trash suggestions
        trash_count = File.query.filter_by(user_id=self.user_id, is_deleted=True).count()
        if trash_count > 0:
            old_trash = self._get_old_trash_count()
            if old_trash > 0:
                suggestions.append(f"Empty {old_trash} old files from trash to free up space.")
        
        # Duplicate suggestions
        duplicates = self.find_duplicate_files()
        if len(duplicates) > 0:
            total_waste = sum(d['size'] for d in duplicates)
            waste_mb = total_waste / (1024**2)
            suggestions.append(f"Remove {len(duplicates)} duplicate file groups to save {waste_mb:.1f} MB.")
        
        # Organization suggestions
        files_without_folder = File.query.filter_by(
            user_id=self.user_id,
            folder_id=None,
            is_deleted=False
        ).count()
        if files_without_folder > 10:
            suggestions.append(f"Organize {files_without_folder} files into folders for better management.")
        
        # Eco mode suggestion
        if not self.user.eco_mode_enabled:
            suggestions.append("Enable Eco Mode to activate energy-saving features.")
        
        # Auto cleanup suggestion
        if not self.user.auto_cleanup_enabled:
            suggestions.append("Enable Auto Cleanup to automatically remove old trash files.")
        
        # Old files suggestion
        old_files = self.get_old_files(days=180)
        if len(old_files) > 5:
            suggestions.append(f"Archive or delete {len(old_files)} files not accessed in 6 months.")
        
        return suggestions
    
    def find_duplicate_files(self):
        """Find duplicate files based on hash"""
        # Get files with duplicate hashes
        duplicates_query = db.session.query(
            File.file_hash,
            func.count(File.id).label('count'),
            func.sum(File.size).label('total_size')
        ).filter(
            File.user_id == self.user_id,
            File.is_deleted == False,
            File.file_hash != None
        ).group_by(File.file_hash).having(func.count(File.id) > 1).all()
        
        duplicates = []
        for hash_value, count, total_size in duplicates_query:
            files = File.query.filter_by(
                user_id=self.user_id,
                file_hash=hash_value,
                is_deleted=False
            ).all()
            
            duplicates.append({
                'hash': hash_value,
                'count': count,
                'size': total_size,
                'files': [{'id': f.id, 'name': f.original_filename, 'size': f.size} for f in files]
            })
        
        return duplicates
    
    def get_old_files(self, days=180):
        """Get files not accessed in specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return File.query.filter(
            File.user_id == self.user_id,
            File.is_deleted == False,
            File.last_accessed < cutoff_date
        ).all()
    
    def cleanup_old_trash(self, days=None):
        """Cleanup old trash files"""
        if days is None:
            days = Config.AUTO_CLEANUP_DAYS
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_trash_files = File.query.filter(
            File.user_id == self.user_id,
            File.is_deleted == True,
            File.deleted_at < cutoff_date
        ).all()
        
        count = 0
        for file in old_trash_files:
            file.hard_delete()
            count += 1
        
        self.user.update_storage_used()
        
        return count
    
    def get_storage_optimization_stats(self):
        """Get storage optimization statistics"""
        total_files = File.query.filter_by(user_id=self.user_id, is_deleted=False).count()
        trash_files = File.query.filter_by(user_id=self.user_id, is_deleted=True).count()
        
        # Calculate potential savings
        trash_size = db.session.query(func.sum(File.size)).filter(
            File.user_id == self.user_id,
            File.is_deleted == True
        ).scalar() or 0
        
        duplicates = self.find_duplicate_files()
        duplicate_waste = sum(d['size'] for d in duplicates)
        
        return {
            'total_files': total_files,
            'trash_files': trash_files,
            'trash_size': trash_size,
            'duplicate_groups': len(duplicates),
            'duplicate_waste': duplicate_waste,
            'potential_savings': trash_size + duplicate_waste
        }
    
    def get_file_count(self):
        """Get total file count"""
        return File.query.filter_by(user_id=self.user_id, is_deleted=False).count()
    
    def get_folder_count(self):
        """Get total folder count"""
        return Folder.query.filter_by(user_id=self.user_id, is_deleted=False).count()
    
    def get_trash_count(self):
        """Get trash file count"""
        return File.query.filter_by(user_id=self.user_id, is_deleted=True).count()
    
    def _get_old_trash_count(self):
        """Get count of old trash files"""
        cutoff_date = datetime.utcnow() - timedelta(days=Config.AUTO_CLEANUP_DAYS)
        
        return File.query.filter(
            File.user_id == self.user_id,
            File.is_deleted == True,
            File.deleted_at < cutoff_date
        ).count()
