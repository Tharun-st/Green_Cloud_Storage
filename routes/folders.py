"""Folder management routes"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.folder import Folder

folders_bp = Blueprint('folders', __name__)


@folders_bp.route('/create', methods=['POST'])
@login_required
def create():
    """Create new folder"""
    name = request.form.get('name')
    parent_id = request.form.get('parent_id', type=int)
    
    if not name:
        flash('Folder name is required.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    # Check if folder with same name exists in parent
    existing = Folder.query.filter_by(
        user_id=current_user.id,
        name=name,
        parent_id=parent_id,
        is_deleted=False
    ).first()
    
    if existing:
        flash(f'Folder "{name}" already exists in this location.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    folder = Folder(
        name=name,
        user_id=current_user.id,
        parent_id=parent_id
    )
    
    db.session.add(folder)
    db.session.commit()
    
    # Update path
    folder.path = folder.get_full_path()
    db.session.commit()
    
    flash(f'Folder "{name}" created successfully!', 'success')
    return redirect(request.referrer or url_for('files.index'))


@folders_bp.route('/<int:folder_id>/rename', methods=['POST'])
@login_required
def rename(folder_id):
    """Rename folder"""
    folder = Folder.query.get_or_404(folder_id)
    
    if folder.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))
    
    new_name = request.form.get('new_name')
    
    if not new_name:
        flash('Folder name cannot be empty.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    # Check for duplicate name
    existing = Folder.query.filter_by(
        user_id=current_user.id,
        name=new_name,
        parent_id=folder.parent_id,
        is_deleted=False
    ).filter(Folder.id != folder_id).first()
    
    if existing:
        flash(f'Folder "{new_name}" already exists in this location.', 'error')
        return redirect(request.referrer or url_for('files.index'))
    
    folder.name = new_name
    folder.path = folder.get_full_path()
    db.session.commit()
    
    flash(f'Folder renamed to "{new_name}".', 'success')
    return redirect(request.referrer or url_for('files.index'))


@folders_bp.route('/<int:folder_id>/delete', methods=['POST'])
@login_required
def delete(folder_id):
    """Delete folder"""
    folder = Folder.query.get_or_404(folder_id)
    
    if folder.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.index'))
    
    folder.soft_delete()
    current_user.update_storage_used()
    
    flash(f'Folder "{folder.name}" and its contents moved to trash.', 'info')
    return redirect(request.referrer or url_for('files.index'))


@folders_bp.route('/<int:folder_id>/restore', methods=['POST'])
@login_required
def restore(folder_id):
    """Restore folder from trash"""
    folder = Folder.query.get_or_404(folder_id)
    
    if folder.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('files.trash'))
    
    folder.restore()
    current_user.update_storage_used()
    
    flash(f'Folder "{folder.name}" and its contents restored.', 'success')
    return redirect(url_for('files.index'))


@folders_bp.route('/<int:folder_id>/info')
@login_required
def info(folder_id):
    """Get folder information"""
    folder = Folder.query.get_or_404(folder_id)
    
    if folder.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': folder.id,
        'name': folder.name,
        'path': folder.get_full_path(),
        'file_count': folder.get_file_count(),
        'created_at': folder.created_at.isoformat(),
        'breadcrumbs': folder.get_breadcrumbs()
    })
