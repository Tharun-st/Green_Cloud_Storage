// GreenCloud - AI Agent JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    const aiAgentBtn = document.getElementById('aiAgentBtn');
    const aiChat = document.getElementById('aiChat');
    const aiChatClose = document.getElementById('aiChatClose');
    const aiInput = document.getElementById('aiInput');
    const aiSend = document.getElementById('aiSend');
    const aiChatMessages = document.getElementById('aiChatMessages');
    
    // Toggle chat window
    if (aiAgentBtn) {
        aiAgentBtn.addEventListener('click', function() {
            aiChat.classList.toggle('active');
            if (aiChat.classList.contains('active')) {
                aiInput.focus();
            }
        });
    }
    
    // Close chat
    if (aiChatClose) {
        aiChatClose.addEventListener('click', function() {
            aiChat.classList.remove('active');
        });
    }
    
    // Send message
    if (aiSend) {
        aiSend.addEventListener('click', sendMessage);
    }
    
    // Send message on Enter
    if (aiInput) {
        aiInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    function sendMessage() {
        const message = aiInput.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        aiInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send to server
        fetch('/ai/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add AI response
            addMessage(data.response, 'ai');
            
            // Scroll to bottom
            scrollToBottom();
        })
        .catch(error => {
            removeTypingIndicator();
            addMessage('Sorry, I encountered an error. Please try again.', 'ai');
            console.error('Error:', error);
        });
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = sender === 'ai' ? 'ai-message' : 'user-message';
        
        if (sender === 'ai') {
            messageDiv.innerHTML = `
                <div class="ai-avatar">🤖</div>
                <div class="ai-text">${formatMessage(text)}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="user-avatar">${getUserInitial()}</div>
                <div class="user-text">${escapeHtml(text)}</div>
            `;
        }
        
        aiChatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'ai-message typing-indicator';
        indicator.innerHTML = `
            <div class="ai-avatar">🤖</div>
            <div class="ai-text">Thinking...</div>
        `;
        indicator.id = 'typingIndicator';
        aiChatMessages.appendChild(indicator);
        scrollToBottom();
    }
    
    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    function scrollToBottom() {
        aiChatMessages.scrollTop = aiChatMessages.scrollHeight;
    }
    
    function getUserInitial() {
        const userName = document.querySelector('.user-name');
        if (userName) {
            return userName.textContent.charAt(0).toUpperCase();
        }
        return 'U';
    }
    
    function formatMessage(text) {
        // Convert markdown-like formatting to HTML
        text = escapeHtml(text);
        
        // Bold text
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Line breaks
        text = text.replace(/\n/g, '<br>');
        
        // Bullet points
        text = text.replace(/^• /gm, '&bull; ');
        
        return text;
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Quick suggestions
    const quickSuggestions = [
        'How much storage do I have?',
        'Show me cleanup suggestions',
        'Find duplicate files',
        'What is GreenOps?',
        'Help me organize my files'
    ];
    
    // Add quick suggestions on first load
    if (aiChatMessages.children.length === 1) {
        setTimeout(() => {
            const suggestionsDiv = document.createElement('div');
            suggestionsDiv.className = 'ai-message';
            suggestionsDiv.innerHTML = `
                <div class="ai-avatar">🤖</div>
                <div class="ai-text">
                    You can ask me things like:<br>
                    ${quickSuggestions.map(s => `<br>• "${s}"`).join('')}
                </div>
            `;
            aiChatMessages.appendChild(suggestionsDiv);
        }, 1000);
    }
});
