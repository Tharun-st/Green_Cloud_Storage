"""File management routes"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from extensions import db
from models.file import File
from models.folder import Folder
from services.file_service import FileService
from config import Config

files_bp = Blueprint('files', __name__)


@files_bp.route('/')
@login_required
def index():
    """List all files (Global Access)"""
    folder_id = request.args.get('folder_id', type=int)
    search = request.args.get('search', '')
    
    file_service = FileService(current_user.id)
    
    if search:
        # Search all shared files
        files = File.query.filter(
            File.is_deleted == False,
            File.original_filename.ilike(f'%{search}%')
        ).all()
        current_folder = None
    else:
        if folder_id:
            # If in a folder, show folder contents (folders are still user-specific for now, or global?)
            # Validating folder access might be tricky if folders are private.
            # For simplicity, assuming "My Files" root view shows ALL files.
            files = file_service.get_files(folder_id)
            current_folder = Folder.query.get(folder_id)
        else:
            # GLOBAL VIEW: Show all files from all users
            files = File.query.filter_by(is_deleted=False, folder_id=None).order_by(File.created_at.desc()).all()
            current_folder = None
    
    # Folders are still user-specific in this implementation to avoid clutter, 
    # unless user wants global folders too. Sticky point.
    # Let's keep folders private for now, but files global.
    folders = file_service.get_folders(folder_id)
    breadcrumbs = current_folder.get_breadcrumbs() if current_folder else []
    
    return render_template('files/index.html', 
                         files=files, 
                         folders=folders,
                         current_folder=current_folder,
                         breadcrumbs=breadcrumbs,
                         search=search)


@files_bp.route('/shared')
@login_required
def shared():
    """List shared files (Redirect to index since everything is shared)"""
    return redirect(url_for('files.index'))


@files_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload file"""
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    file = request.files['file']
    folder_id = request.form.get('folder_id', type=int)
    
    # GLOBAL SHARING: Always true
    is_shared = True
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    file_service = FileService(current_user.id)
    
    try:
        uploaded_file = file_service.upload_file(file, folder_id, is_shared=is_shared)
        flash(f'File "{uploaded_file.original_filename}" uploaded successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')
    
    return redirect(request.referrer or url_for('files.index'))


@files_bp.route('/<int:file_id>/download')
@login_required
def download(file_id):
    """Download file"""
    file = File.query.get_or_404(file_id)
    
    # Shared file system: Allow download for all users if shared or owner
    if file.user_id != current_user.id and not file.is_shared:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))
    
    if file.is_deleted:
        flash('File is in trash.', 'error')
        return redirect(url_for('files.index'))
    
    file.update_access_time()
    
    return send_file(file.file_path, 
                    as_attachment=True, 
                    download_name=file.original_filename)


@files_bp.route('/<int:file_id>/delete', methods=['POST'])
@login_required
def delete(file_id):
    """Delete file (move to trash)"""
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))
    
    file.soft_delete()
    current_user.update_storage_used()
    
    flash(f'File "{file.original_filename}" moved to trash.', 'info')
    return redirect(request.referrer or url_for('files.index'))


@files_bp.route('/<int:file_id>/rename', methods=['POST'])
@login_required
def rename(file_id):
    """Rename file"""
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))
    
    new_name = request.form.get('new_name')
    
    if not new_name:
        flash('File name cannot be empty.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    file.original_filename = new_name
    db.session.commit()
    
    flash(f'File renamed to "{new_name}".', 'success')
    return redirect(request.referrer or url_for('files.index'))


@files_bp.route('/<int:file_id>/move', methods=['POST'])
@login_required
def move(file_id):
    """Move file to different folder"""
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))
    
    folder_id = request.form.get('folder_id', type=int)
    
    if folder_id:
        folder = Folder.query.get_or_404(folder_id)
        if folder.user_id != current_user.id:
            flash('Unauthorized access.', 'error')
            return redirect(url_for('files.index'))
    
    file.folder_id = folder_id
    db.session.commit()
    
    flash('File moved successfully.', 'success')
    return redirect(request.referrer or url_for('files.index'))


@files_bp.route('/<int:file_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(file_id):
    """Toggle file favorite status"""
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    file.is_favorite = not file.is_favorite
    db.session.commit()
    
    return jsonify({'success': True, 'is_favorite': file.is_favorite})


@files_bp.route('/trash')
@login_required
def trash():
    """View trash/deleted files"""
    files = File.query.filter_by(
        user_id=current_user.id,
        is_deleted=True
    ).order_by(File.deleted_at.desc()).all()
    
    return render_template('files/trash.html', files=files)


@files_bp.route('/<int:file_id>/restore', methods=['POST'])
@login_required
def restore(file_id):
    """Restore file from trash"""
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.trash'))
    
    file.restore()
    current_user.update_storage_used()
    
    flash(f'File "{file.original_filename}" restored.', 'success')
    return redirect(url_for('files.trash'))


@files_bp.route('/<int:file_id>/delete-permanent', methods=['POST'])
@login_required
def delete_permanent(file_id):
    """Permanently delete file"""
    file = File.query.get_or_404(file_id)
    
    if file.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.trash'))
    
    filename = file.original_filename
    file.hard_delete()
    
    # Update quota if user deleted their own file
    if file.user_id == current_user.id:
        current_user.update_storage_used()
    # If admin deleted another user's file, we should update that user's quota too
    else:
        file.owner.update_storage_used()
    
    flash(f'File "{filename}" permanently deleted.', 'success')
    return redirect(request.referrer or url_for('files.trash'))


@files_bp.route('/favorites')
@login_required
def favorites():
    """View favorite files"""
    files = File.query.filter_by(
        user_id=current_user.id,
        is_favorite=True,
        is_deleted=False
    ).order_by(File.created_at.desc()).all()
    
    return render_template('files/favorites.html', files=files)


@files_bp.route('/<int:file_id>/preview')
@login_required
def preview(file_id):
    """Preview a file (images and text-based files)"""
    file = File.query.get_or_404(file_id)

    # Shared file system: allow preview for owner, shared files, or admins
    if file.user_id != current_user.id and not file.is_shared and not current_user.is_admin:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))

    if file.is_deleted:
        flash('File is in trash.', 'error')
        return redirect(url_for('files.trash'))

    # Determine preview type based on extension
    ext = (file.extension or file.get_extension() or '').lower()
    image_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'}
    text_exts = {'txt', 'csv', 'json', 'xml', 'html', 'css', 'js'}

    is_image = ext in image_exts
    is_text = ext in text_exts

    file_url = None
    text_content = None

    # Build static file URL for images (files are stored under static/uploads)
    if is_image:
        try:
            rel_path = os.path.relpath(file.file_path, Config.BASE_DIR)
            # Expect something like "static/uploads/..."
            parts = rel_path.split(os.sep, 1)
            if len(parts) == 2 and parts[0] == 'static':
                static_rel = parts[1].replace(os.sep, '/')
                file_url = url_for('static', filename=static_rel)
        except Exception:
            file_url = None

    # Read small preview for text-based files
    if is_text:
        try:
            with open(file.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read(10000)  # limit preview size
        except Exception:
            text_content = None

    return render_template(
        'files/preview.html',
        file=file,
        is_image=is_image,
        is_text=is_text,
        file_url=file_url,
        text_content=text_content,
    )
