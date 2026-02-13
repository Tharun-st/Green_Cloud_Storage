"""
GreenCloud - Personal Cloud Storage with AI Agent and GreenOps
Main Flask Application
"""

from flask import Flask, render_template, redirect, url_for
from flask_login import current_user
from config import Config
from extensions import db, login_manager

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    with app.app_context():
        # Import models
        from models.user import User
        from models.file import File
        from models.folder import Folder
        
        # Create tables
        db.create_all()
        
        # Register user loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Register blueprints
        from routes.auth import auth_bp
        from routes.files import files_bp
        from routes.folders import folders_bp
        from routes.ai_agent import ai_bp
        from routes.greenops import greenops_bp
        from routes.system import system_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(files_bp, url_prefix='/files')
        app.register_blueprint(folders_bp, url_prefix='/folders')
        app.register_blueprint(ai_bp, url_prefix='/ai')
        app.register_blueprint(greenops_bp, url_prefix='/greenops')
        app.register_blueprint(system_bp, url_prefix='/system')
    
    # Main routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    def dashboard():
        from flask_login import login_required
        from services.file_service import FileService
        from services.greenops import GreenOpsService
        from services.system_monitor import system_monitor
        from models.user import User
        from models.file import File
        
        @login_required
        def _dashboard():
            if current_user.is_admin:
                # ADMIN DASHBOARD
                total_users = User.query.count()
                total_files = File.query.count()
                
                # Calculate total storage used by all files
                # This is a bit inefficient for large DBs, but fine for now.
                # ideally use db.session.query(func.sum(File.size)).scalar()
                all_files = File.query.all()
                total_storage = sum(f.size for f in all_files)
                
                # Format storage
                def format_size(size):
                    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                        if size < 1024:
                            return f"{size:.2f} {unit}"
                        size /= 1024
                    return f"{size:.2f} PB"
                
                recent_files = File.query.order_by(File.created_at.desc()).limit(10).all()
                
                return render_template('dashboard_admin.html', 
                                     total_users=total_users,
                                     total_files=total_files,
                                     total_storage=format_size(total_storage),
                                     recent_files=recent_files)
            else:
                # USER DASHBOARD
                file_service = FileService(current_user.id)
                greenops_service = GreenOpsService(current_user.id)
                
                # Get system stats
                system_stats = system_monitor.get_system_summary()
                energy_score = system_monitor.calculate_energy_score({
                    'eco_mode_enabled': current_user.eco_mode_enabled
                })
                
                stats = {
                    'total_files': file_service.get_file_count(),
                    'total_folders': file_service.get_folder_count(),
                    'storage_used': file_service.get_storage_used(),
                    'storage_quota': current_user.storage_quota,
                    'storage_percentage': file_service.get_storage_percentage(),
                    'recent_files': file_service.get_recent_files(limit=5),
                    'greenops_score': greenops_service.calculate_greenops_score(),
                    'suggestions': greenops_service.get_suggestions(),
                    'system': system_stats,
                    'energy_score': energy_score
                }
                
                return render_template('dashboard.html', stats=stats)
        
        return _dashboard()
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.context_processor
    def inject_config():
        return {
            'AI_AGENT_ENABLED': app.config['AI_AGENT_ENABLED'],
            'AI_AGENT_NAME': app.config['AI_AGENT_NAME'],
            'GREENOPS_ENABLED': app.config['GREENOPS_ENABLED']
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Use ASCII-only console output for better Windows compatibility
    print("GreenCloud Starting...")
    print("Server running at: http://localhost:5000")
    print("GreenOps:", "ENABLED" if app.config['GREENOPS_ENABLED'] else "DISABLED")
    print("AI Agent:", "ENABLED" if app.config['AI_AGENT_ENABLED'] else "DISABLED")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
