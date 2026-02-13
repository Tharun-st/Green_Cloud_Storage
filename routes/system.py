"""System monitoring routes"""

from flask import Blueprint, jsonify, render_template, abort
from flask_login import login_required, current_user
from functools import wraps
from services.system_monitor import system_monitor

system_bp = Blueprint('system', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@system_bp.route('/monitor')
@login_required
@admin_required
def monitor_dashboard():
    """System monitoring dashboard"""
    summary = system_monitor.get_system_summary()
    energy_score = system_monitor.calculate_energy_score({
        'eco_mode_enabled': current_user.eco_mode_enabled
    })
    recommendations = system_monitor.get_eco_recommendations(current_user.id)
    
    return render_template('system/monitor.html', 
                         summary=summary, 
                         energy_score=energy_score,
                         recommendations=recommendations)


@system_bp.route('/api/stats')
@login_required
@admin_required
def get_system_stats():
    """Get real-time system statistics"""
    summary = system_monitor.get_system_summary()
    energy_score = system_monitor.calculate_energy_score({
        'eco_mode_enabled': current_user.eco_mode_enabled
    })
    
    return jsonify({
        'success': True,
        'stats': summary,
        'energy_score': energy_score
    })


@system_bp.route('/api/alerts')
@login_required
@admin_required
def get_alerts():
    """Get system alerts"""
    alerts = system_monitor.get_resource_alerts()
    return jsonify({
        'success': True,
        'alerts': alerts
    })


@system_bp.route('/api/recommendations')
@login_required
@admin_required
def get_recommendations():
    """Get eco recommendations"""
    recommendations = system_monitor.get_eco_recommendations(current_user.id)
    return jsonify({
        'success': True,
        'recommendations': recommendations
    })
