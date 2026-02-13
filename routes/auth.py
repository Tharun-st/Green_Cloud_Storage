"""Authentication routes"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from functools import wraps
from flask import abort
from extensions import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        # Debug logging (only in development)
        import os
        if os.environ.get('FLASK_ENV') != 'production':
            print(f"Login attempt - Email: {email}")
            print(f"User found: {user is not None}")
            if user:
                print(f"Password check: {user.check_password(password)}")
                print(f"User active: {user.is_active}")
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact admin.', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page) if next_page else redirect(url_for('auth.admin_users'))
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            if not user:
                flash('No account found with that email address.', 'error')
            else:
                flash('Invalid password.', 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    current_user.first_name = first_name
    current_user.last_name = last_name
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    
    return redirect(url_for('auth.profile'))


@auth_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('auth.profile'))
    
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))


@auth_bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin user management"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@auth_bp.route('/admin/users/add', methods=['POST'])
@login_required
@admin_required
def admin_add_user():
    """Admin add user"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_admin = request.form.get('is_admin') == 'on'
    
    if User.query.filter_by(username=username).first():
        flash('Username already taken.', 'error')
        return redirect(url_for('auth.admin_users'))
        
    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'error')
        return redirect(url_for('auth.admin_users'))
    
    user = User(
        username=username,
        email=email,
        is_admin=is_admin,
        is_active=True
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash('User created successfully.', 'success')
    return redirect(url_for('auth.admin_users'))


@auth_bp.route('/admin/files')
@login_required
@admin_required
def admin_files():
    """Admin files management"""
    from models.file import File
    files = File.query.all()
    return render_template('admin/files.html', files=files)


@auth_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Admin delete user"""
    if current_user.id == user_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('auth.admin_users'))
    
    user = User.query.get_or_404(user_id)
    
    # Delete user (cascade should handle files/folders if configured, otherwise we might need manual cleanup)
    # The User model has cascade='all, delete-orphan' on files and folders relationships, so it should be fine.
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User "{username}" deleted successfully.', 'success')
    return redirect(url_for('auth.admin_users'))
