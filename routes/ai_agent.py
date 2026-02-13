"""AI Agent routes"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.ai_agent import AIAgent

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    """Handle AI agent chat messages"""
    data = request.get_json()
    message = data.get('message', '').strip().lower()
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    agent = AIAgent(current_user.id)
    response = agent.process_message(message)
    
    return jsonify({
        'response': response['text'],
        'data': response.get('data'),
        'suggestions': response.get('suggestions', [])
    })


@ai_bp.route('/suggestions')
@login_required
def suggestions():
    """Get AI agent suggestions"""
    agent = AIAgent(current_user.id)
    suggestions = agent.get_smart_suggestions()
    
    return jsonify({'suggestions': suggestions})


@ai_bp.route('/help')
@login_required
def help():
    """Get AI agent help topics"""
    agent = AIAgent(current_user.id)
    help_topics = agent.get_help_topics()
    
    return jsonify({'topics': help_topics})
