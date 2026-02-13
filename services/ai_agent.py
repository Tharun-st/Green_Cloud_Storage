"""AI Agent service - Rule-based intelligent assistant"""

from models.user import User
from models.file import File
from models.folder import Folder
from services.greenops import GreenOpsService
from datetime import datetime, timedelta


class AIAgent:
    """Lightweight rule-based AI agent for assistance"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        self.greenops = GreenOpsService(user_id)
    
    def process_message(self, message):
        """Process user message and generate response"""
        message = message.lower().strip()
        
        # System/Resource queries
        if any(word in message for word in ['cpu', 'memory', 'ram', 'system', 'resources', 'performance']):
            return self._handle_system_query()
        
        # Energy queries
        elif any(word in message for word in ['energy', 'battery', 'power', 'energy score']):
            return self._handle_energy_query()
        
        # Storage queries
        elif any(word in message for word in ['storage', 'space', 'quota', 'how much']):
            return self._handle_storage_query()
        
        # File count queries
        elif any(word in message for word in ['how many files', 'file count', 'number of files']):
            return self._handle_file_count_query()
        
        # Cleanup suggestions
        elif any(word in message for word in ['cleanup', 'clean', 'optimize', 'free space']):
            return self._handle_cleanup_query()
        
        # Duplicate files
        elif any(word in message for word in ['duplicate', 'duplicates', 'same files']):
            return self._handle_duplicate_query()
        
        # GreenOps information
        elif any(word in message for word in ['greenops', 'green', 'eco', 'sustainable']):
            return self._handle_greenops_query()
        
        # Help queries
        elif any(word in message for word in ['help', 'how to', 'what can you do']):
            return self._handle_help_query()
        
        # Upload help
        elif any(word in message for word in ['upload', 'add file']):
            return self._handle_upload_help()
        
        # Organization help
        elif any(word in message for word in ['organize', 'manage', 'folder']):
            return self._handle_organization_help()
        
        # Recent activity
        elif any(word in message for word in ['recent', 'latest', 'new']):
            return self._handle_recent_query()
        
        # Default response
        else:
            return self._handle_default()
    
    def _handle_storage_query(self):
        """Handle storage-related queries"""
        used = self.user.storage_used / (1024**3)  # Convert to GB
        quota = self.user.storage_quota / (1024**3)
        percentage = self.user.get_storage_percentage()
        available = quota - used
        
        response = f"💾 **Storage Status**\n\n"
        response += f"• Used: {used:.2f} GB\n"
        response += f"• Total: {quota:.2f} GB\n"
        response += f"• Available: {available:.2f} GB\n"
        response += f"• Usage: {percentage:.1f}%\n\n"
        
        if percentage > 90:
            response += "⚠️ Your storage is almost full! Consider cleaning up old files."
        elif percentage > 70:
            response += "💡 You're using quite a bit of storage. Time for some cleanup?"
        else:
            response += "✅ You have plenty of storage space!"
        
        return {
            'text': response,
            'data': {
                'used': used,
                'quota': quota,
                'percentage': percentage
            }
        }
    
    def _handle_file_count_query(self):
        """Handle file count queries"""
        file_count = File.query.filter_by(user_id=self.user_id, is_deleted=False).count()
        folder_count = Folder.query.filter_by(user_id=self.user_id, is_deleted=False).count()
        trash_count = File.query.filter_by(user_id=self.user_id, is_deleted=True).count()
        
        response = f"📊 **Your Files Summary**\n\n"
        response += f"• Active Files: {file_count}\n"
        response += f"• Folders: {folder_count}\n"
        response += f"• Files in Trash: {trash_count}\n"
        
        return {'text': response}
    
    def _handle_cleanup_query(self):
        """Handle cleanup suggestions"""
        suggestions = self.greenops.get_suggestions()
        
        response = f"🧹 **Cleanup Suggestions**\n\n"
        
        if suggestions:
            for i, suggestion in enumerate(suggestions[:5], 1):
                response += f"{i}. {suggestion}\n"
        else:
            response += "✨ Your storage is well organized! No cleanup needed right now."
        
        return {'text': response, 'suggestions': suggestions}
    
    def _handle_duplicate_query(self):
        """Handle duplicate file queries"""
        duplicates = self.greenops.find_duplicate_files()
        
        response = f"🔍 **Duplicate Files**\n\n"
        
        if duplicates:
            total_waste = sum(d['size'] for d in duplicates) / (1024**2)
            response += f"Found {len(duplicates)} duplicate file groups.\n"
            response += f"Potential space savings: {total_waste:.2f} MB\n\n"
            response += "💡 Tip: Review and delete duplicate files to free up space!"
        else:
            response += "✅ No duplicate files found. Great job keeping your storage clean!"
        
        return {'text': response, 'data': {'duplicates': duplicates}}
    
    def _handle_greenops_query(self):
        """Handle GreenOps information queries"""
        score = self.greenops.calculate_greenops_score()
        
        response = f"🌱 **GreenOps Score: {score}/100**\n\n"
        response += "GreenOps helps you maintain an eco-friendly storage system:\n\n"
        response += "• 🔋 Energy Efficiency: Auto-logout saves power\n"
        response += "• 💾 Storage Optimization: Regular cleanup\n"
        response += "• ♻️ Resource Management: Duplicate detection\n"
        response += "• 🌍 Sustainable Computing: Minimal footprint\n\n"
        
        if score >= 80:
            response += "🌟 Excellent! You're a green computing champion!"
        elif score >= 60:
            response += "👍 Good job! A few improvements can make it even better."
        else:
            response += "💡 Let's improve! Enable eco mode and cleanup old files."
        
        return {'text': response, 'data': {'score': score}}
    
    def _handle_help_query(self):
        """Handle help queries"""
        response = f"🤖 **GreenBot Help**\n\n"
        response += "I can help you with:\n\n"
        response += "📊 **Storage**: Ask about storage usage and quota\n"
        response += "🧹 **Cleanup**: Get cleanup suggestions\n"
        response += "🔍 **Duplicates**: Find duplicate files\n"
        response += "🌱 **GreenOps**: Learn about eco-friendly features\n"
        response += "📁 **Organization**: Tips for organizing files\n"
        response += "📤 **Upload**: Help with uploading files\n"
        response += "🕒 **Recent**: See your recent activity\n\n"
        response += "Just ask me anything!"
        
        return {'text': response}
    
    def _handle_upload_help(self):
        """Handle upload help"""
        response = f"📤 **How to Upload Files**\n\n"
        response += "1. Click the **Upload** button\n"
        response += "2. Select files from your device\n"
        response += "3. Choose a folder (optional)\n"
        response += "4. Click **Upload**\n\n"
        response += "💡 **Tips:**\n"
        response += "• You can drag & drop files\n"
        response += "• Max file size: 100MB\n"
        response += f"• Available space: {(self.user.storage_quota - self.user.storage_used) / (1024**3):.2f} GB"
        
        return {'text': response}
    
    def _handle_organization_help(self):
        """Handle organization help"""
        response = f"📁 **Organization Tips**\n\n"
        response += "✨ **Best Practices:**\n\n"
        response += "1. Create folders by category (Work, Personal, Projects)\n"
        response += "2. Use descriptive file names\n"
        response += "3. Regularly move old files to archive folders\n"
        response += "4. Use the favorite feature for important files\n"
        response += "5. Enable auto-cleanup for trash\n\n"
        response += "🌱 Green Tip: Well-organized storage is eco-friendly storage!"
        
        return {'text': response}
    
    def _handle_recent_query(self):
        """Handle recent activity queries"""
        recent_files = File.query.filter_by(
            user_id=self.user_id,
            is_deleted=False
        ).order_by(File.created_at.desc()).limit(5).all()
        
        response = f"🕒 **Recent Files**\n\n"
        
        if recent_files:
            for file in recent_files:
                time_diff = datetime.utcnow() - file.created_at
                if time_diff.days == 0:
                    time_str = "Today"
                elif time_diff.days == 1:
                    time_str = "Yesterday"
                else:
                    time_str = f"{time_diff.days} days ago"
                
                response += f"• {file.original_filename} ({time_str})\n"
        else:
            response += "No files uploaded yet. Start by uploading your first file!"
        
        return {'text': response}
    
    def _handle_system_query(self):
        """Handle system resource queries"""
        from services.system_monitor import system_monitor
        
        summary = system_monitor.get_system_summary()
        
        response = f"💻 **System Resources**\n\n"
        response += f"• CPU Usage: {summary['cpu']['percent']}%\n"
        response += f"• Memory: {summary['memory']['percent']:.1f}% ({summary['memory']['used_gb']:.2f} / {summary['memory']['total_gb']:.2f} GB)\n"
        response += f"• Disk: {summary['disk']['percent']:.1f}% ({summary['disk']['free_gb']:.2f} GB free)\n"
        response += f"• Uptime: {summary['uptime']['formatted']}\n\n"
        
        if summary['alerts']:
            response += "⚠️ **Alerts:**\n"
            for alert in summary['alerts']:
                response += f"• {alert['message']}\n"
        else:
            response += "✅ All systems running smoothly!"
        
        return {'text': response, 'data': summary}
    
    def _handle_energy_query(self):
        """Handle energy/battery queries"""
        from services.system_monitor import system_monitor
        
        summary = system_monitor.get_system_summary()
        energy_score = system_monitor.calculate_energy_score({
            'eco_mode_enabled': self.user.eco_mode_enabled
        })
        
        response = f"⚡ **Energy Status**\n\n"
        response += f"Energy Score: {energy_score}/100\n"
        response += f"Status: {summary['energy_message']}\n\n"
        
        if summary['battery']:
            battery = summary['battery']
            response += f"🔋 Battery: {battery['percent']}%\n"
            response += f"Status: {'Charging' if battery['plugged'] else 'On Battery'}\n\n"
        
        recommendations = system_monitor.get_eco_recommendations(self.user_id)
        if recommendations:
            response += "💡 **Recommendations:**\n"
            for rec in recommendations[:3]:
                response += f"• {rec['message']}\n"
        
        return {'text': response}
    
    def _handle_default(self):
        """Handle default/unknown queries"""
        response = f"🤖 I'm here to help!\n\n"
        response += "Try asking me about:\n"
        response += "• System resources (CPU, memory, disk)\n"
        response += "• Energy usage and battery\n"
        response += "• Storage space\n"
        response += "• Cleanup suggestions\n"
        response += "• Duplicate files\n"
        response += "• GreenOps features\n"
        response += "• How to upload files\n\n"
        response += "Or just say 'help' for more options!"
        
        return {'text': response}
    
    def get_smart_suggestions(self):
        """Get smart suggestions for the user"""
        suggestions = []
        
        # Storage suggestions
        percentage = self.user.get_storage_percentage()
        if percentage > 80:
            suggestions.append("Your storage is getting full. Consider cleaning up old files.")
        
        # Trash suggestions
        trash_count = File.query.filter_by(user_id=self.user_id, is_deleted=True).count()
        if trash_count > 10:
            suggestions.append(f"You have {trash_count} files in trash. Empty it to free up space.")
        
        # Duplicate suggestions
        duplicates = self.greenops.find_duplicate_files()
        if len(duplicates) > 0:
            suggestions.append(f"Found {len(duplicates)} duplicate file groups. Review them to save space.")
        
        # Organization suggestions
        files_without_folder = File.query.filter_by(
            user_id=self.user_id,
            folder_id=None,
            is_deleted=False
        ).count()
        if files_without_folder > 5:
            suggestions.append("You have files without folders. Organize them for better management.")
        
        return suggestions
    
    def get_help_topics(self):
        """Get available help topics"""
        return [
            {'title': 'System Resources', 'query': 'system resources'},
            {'title': 'Energy Usage', 'query': 'energy'},
            {'title': 'Storage Management', 'query': 'storage'},
            {'title': 'File Organization', 'query': 'organize'},
            {'title': 'Upload Files', 'query': 'upload'},
            {'title': 'Cleanup Tips', 'query': 'cleanup'},
            {'title': 'Find Duplicates', 'query': 'duplicates'},
            {'title': 'GreenOps Features', 'query': 'greenops'},
        ]
