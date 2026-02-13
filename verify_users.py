"""
Verify that users exist in the database
Run this to check if default users were created
"""

from app import app
from extensions import db
from models.user import User

def verify_users():
    """Verify users in database"""
    with app.app_context():
        print("\n" + "="*50)
        print("GreenCloud - User Verification")
        print("="*50)
        
        # Count total users
        total_users = User.query.count()
        print(f"\nTotal users in database: {total_users}")
        
        # Check admin user
        admin = User.query.filter_by(email='admin@greencloud.local').first()
        if admin:
            print("\n✓ Admin user EXISTS")
            print(f"  - Username: {admin.username}")
            print(f"  - Email: {admin.email}")
            print(f"  - Is Admin: {admin.is_admin}")
            print(f"  - Is Active: {admin.is_active}")
            # Test password
            if admin.check_password('admin123'):
                print("  - Password: ✓ CORRECT (admin123)")
            else:
                print("  - Password: ✗ WRONG")
        else:
            print("\n✗ Admin user NOT FOUND")
        
        # Check demo user
        demo = User.query.filter_by(email='demo@greencloud.local').first()
        if demo:
            print("\n✓ Demo user EXISTS")
            print(f"  - Username: {demo.username}")
            print(f"  - Email: {demo.email}")
            print(f"  - Is Admin: {demo.is_admin}")
            print(f"  - Is Active: {demo.is_active}")
            # Test password
            if demo.check_password('demo123'):
                print("  - Password: ✓ CORRECT (demo123)")
            else:
                print("  - Password: ✗ WRONG")
        else:
            print("\n✗ Demo user NOT FOUND")
        
        # List all users
        if total_users > 0:
            print("\n" + "="*50)
            print("All Users:")
            print("="*50)
            all_users = User.query.all()
            for user in all_users:
                print(f"  - {user.email} ({user.username}) - Admin: {user.is_admin}")
        
        print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    verify_users()
