"""GreenOps routes"""

from flask import Blueprint, jsonify, request, render_template, abort
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from services.greenops import GreenOpsService

greenops_bp = Blueprint('greenops', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@greenops_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """GreenOps dashboard"""
    service = GreenOpsService(current_user.id)
    
    stats = {
        'score': service.calculate_greenops_score(),
        'storage_optimization': service.get_storage_optimization_stats(),
        'duplicate_files': service.find_duplicate_files(),
        'old_files': service.get_old_files(),
        'suggestions': service.get_suggestions()
    }
    
    return render_template('greenops/dashboard.html', stats=stats)


@greenops_bp.route('/stats')
@login_required
@admin_required
def stats():
    """Get GreenOps statistics"""
    service = GreenOpsService(current_user.id)
    
    return jsonify({
        'greenops_score': service.calculate_greenops_score(),
        'storage_used': current_user.storage_used,
        'storage_quota': current_user.storage_quota,
        'storage_percentage': current_user.get_storage_percentage(),
        'file_count': service.get_file_count(),
        'folder_count': service.get_folder_count(),
        'trash_count': service.get_trash_count(),
        'eco_mode': current_user.eco_mode_enabled
    })


@greenops_bp.route('/optimize', methods=['POST'])
@login_required
@admin_required
def optimize():
    """Run optimization"""
    service = GreenOpsService(current_user.id)
    
    optimization_type = request.json.get('type', 'all')
    
    results = {}
    
    if optimization_type in ['all', 'trash']:
        results['trash_cleaned'] = service.cleanup_old_trash()
    
    if optimization_type in ['all', 'duplicates']:
        results['duplicates_found'] = len(service.find_duplicate_files())
    
    if optimization_type in ['all', 'storage']:
        current_user.update_storage_used()
        results['storage_recalculated'] = True
    
    return jsonify({
        'success': True,
        'results': results,
        'new_score': service.calculate_greenops_score()
    })


@greenops_bp.route('/duplicates')
@login_required
@admin_required
def duplicates():
    """Find duplicate files"""
    service = GreenOpsService(current_user.id)
    duplicates = service.find_duplicate_files()
    
    return jsonify({'duplicates': duplicates})


@greenops_bp.route('/eco-mode', methods=['POST'])
@login_required
@admin_required
def toggle_eco_mode():
    """Toggle eco mode"""
    current_user.eco_mode_enabled = not current_user.eco_mode_enabled
    db.session.commit()
    
    return jsonify({
        'success': True,
        'eco_mode': current_user.eco_mode_enabled
    })


@greenops_bp.route('/auto-cleanup', methods=['POST'])
@login_required
@admin_required
def toggle_auto_cleanup():
    """Toggle auto cleanup"""
    current_user.auto_cleanup_enabled = not current_user.auto_cleanup_enabled
    db.session.commit()
    
    return jsonify({
        'success': True,
        'auto_cleanup': current_user.auto_cleanup_enabled
    })

