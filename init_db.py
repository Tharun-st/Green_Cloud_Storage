"""
Database initialization script
Run this to create the database and tables
"""

from app import app
from extensions import db
from models.user import User
from models.file import File
from models.folder import Folder

def init_database():
    """Initialize database with tables"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        # Use ASCII-only output for Windows consoles
        print("Database tables created successfully!")
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@greencloud.local').first()
        if not admin:
            print("\nCreating admin user...")
            admin = User(
                username='admin',
                email='admin@greencloud.local',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            
            print("Admin user created successfully!")
            print("   Email: admin@greencloud.local")
            print("   Password: admin123")
        else:
            print("\n⚠️  Admin user already exists!")
        
        # Create demo user
        demo = User.query.filter_by(email='demo@greencloud.local').first()
        if not demo:
            print("\nCreating demo user...")
            demo = User(
                username='demo',
                email='demo@greencloud.local',
                first_name='Demo',
                last_name='User'
            )
            demo.set_password('demo123')
            
            db.session.add(demo)
            db.session.commit()
            
            print("Demo user created successfully!")
            print("   Email: demo@greencloud.local")
            print("   Password: demo123")
        else:
            print("⚠️  Demo user already exists!")
        
        print("\nGreenCloud database is ready!")

if __name__ == '__main__':
    init_database()
