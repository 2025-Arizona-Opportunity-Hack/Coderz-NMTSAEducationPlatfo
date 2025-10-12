/**
 * NMTSA LMS Chat System
 * 
 * Modular chat interface with backend API integration
 * All components are organized as methods within the ChatManager class
 * 
 * Features:
 * - Chat Window Management
 * - Message Rendering
 * - Input Handling & Validation
 * - Typing Indicators
 * - Auto-refresh
 * - Error Handling
 * - Accessibility-friendly (no animations)
 */

class ChatManager {
    constructor() {
        // State management
        this.currentRoomId = 1; // Default to support chat
        this.isOpen = false;
        this.messages = [];
        this.typingTimeout = null;
        this.refreshInterval = null;
        this.isLoading = false;
        this.isSending = false;
        
        // DOM elements (will be set after initialization)
        this.chatContainer = null;
        this.toggleButton = null;
        this.messagesContainer = null;
        this.inputField = null;
        this.sendButton = null;
        this.typingIndicator = null;
        
        // Configuration
        this.config = {
            maxMessageLength: 2000,
            refreshInterval: 3000, // 3 seconds
            typingTimeout: 2000, // 2 seconds
            apiBaseUrl: '/lms/api/chat'
        };
    }
    
    // ========================================================================
    // INITIALIZATION MODULE
    // ========================================================================
    
    /**
     * Initialize the chat system
     * Creates DOM elements and sets up event listeners
     */
    init() {
        this.createChatElements();
        this.attachEventListeners();
        console.log('[Chat] Initialized successfully');
    }
    
    /**
     * Create all chat DOM elements
     */
    createChatElements() {
        // Create main chat container
        this.chatContainer = document.getElementById('chat-container');
        if (!this.chatContainer) {
            console.error('[Chat] Container element not found');
            return;
        }
        
        // Get references to key elements
        this.toggleButton = document.getElementById('chat-toggle-btn');
        this.messagesContainer = document.getElementById('chat-messages');
        this.inputField = document.getElementById('chat-input');
        this.sendButton = document.getElementById('chat-send-btn');
        this.typingIndicator = document.getElementById('chat-typing');
        this.closeButton = document.getElementById('chat-close-btn');
    }
    
    /**
     * Attach event listeners to chat elements
     */
    attachEventListeners() {
        // Toggle button
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => this.toggleChat());
        }
        
        // Close button
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.closeChat());
        }
        
        // Send button
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Input field
        if (this.inputField) {
            // Enter key to send
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Typing indicator
            this.inputField.addEventListener('input', () => this.handleTyping());
        }
    }
    
    // ========================================================================
    // CHAT WINDOW MODULE
    // ========================================================================
    
    /**
     * Toggle chat window visibility
     */
    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }
    
    /**
     * Open chat window
     */
    openChat() {
        this.isOpen = true;
        this.chatContainer.classList.remove('hidden');
        this.toggleButton.setAttribute('aria-expanded', 'true');
        
        // Hide the floating action button when chat is open
        if (this.toggleButton) {
            this.toggleButton.style.display = 'none';
        }
        
        // Load messages
        this.loadMessages();
        
        // Start refresh interval
        this.startRefreshInterval();
        
        // Focus input
        if (this.inputField) {
            this.inputField.focus();
        }
        
        console.log('[Chat] Opened');
    }
    
    /**
     * Close chat window
     */
    closeChat() {
        this.isOpen = false;
        this.chatContainer.classList.add('hidden');
        this.toggleButton.setAttribute('aria-expanded', 'false');
        
        // Show the floating action button when chat is closed
        if (this.toggleButton) {
            this.toggleButton.style.display = 'flex';
        }
        
        // Stop refresh interval
        this.stopRefreshInterval();
        
        console.log('[Chat] Closed');
    }
    
    /**
     * Start auto-refresh interval
     */
    startRefreshInterval() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.loadMessages(true); // Silent refresh
            this.checkTypingStatus();
        }, this.config.refreshInterval);
    }
    
    /**
     * Stop auto-refresh interval
     */
    stopRefreshInterval() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    // ========================================================================
    // MESSAGES MODULE
    // ========================================================================
    
    /**
     * Load messages from backend
     * @param {boolean} silent - If true, don't show loading state
     */
    async loadMessages(silent = false) {
        if (!silent) {
            this.isLoading = true;
            this.showLoadingState();
        }
        
        try {
            const response = await fetch(
                `${this.config.apiBaseUrl}/rooms/${this.currentRoomId}/messages/`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                }
            );
            
            const data = await response.json();
            
            if (data.success) {
                this.messages = data.messages;
                this.renderMessages();
            } else {
                this.showError('Failed to load messages');
            }
        } catch (error) {
            console.error('[Chat] Error loading messages:', error);
            if (!silent) {
                this.showError('Network error. Please try again.');
            }
        } finally {
            this.isLoading = false;
        }
    }
    
    /**
     * Render all messages in the chat window
     */
    renderMessages() {
        if (!this.messagesContainer) return;
        
        // Clear existing messages
        this.messagesContainer.innerHTML = '';
        
        // Render each message
        this.messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            this.messagesContainer.appendChild(messageElement);
        });
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    /**
     * Create a message element
     * @param {Object} message - Message data
     * @returns {HTMLElement}
     */
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.is_own_message ? 'own-message' : 'other-message'}`;
        
        // Message type styling
        if (message.message_type === 'system') {
            messageDiv.classList.add('system-message');
        }
        
        // Message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Sender name (if not own message)
        if (!message.is_own_message) {
            const senderSpan = document.createElement('div');
            senderSpan.className = 'message-sender';
            senderSpan.textContent = message.sender;
            contentDiv.appendChild(senderSpan);
        }
        
        // Message text (render markdown)
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text markdown-content';
        textDiv.innerHTML = this.renderMarkdown(message.content);
        contentDiv.appendChild(textDiv);
        
        // Timestamp
        const timeSpan = document.createElement('div');
        timeSpan.className = 'message-time';
        timeSpan.textContent = this.formatTimestamp(message.timestamp);
        contentDiv.appendChild(timeSpan);
        
        messageDiv.appendChild(contentDiv);
        
        return messageDiv;
    }
    
    /**
     * Scroll chat to bottom (instant, no animation)
     */
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    // ========================================================================
    // INPUT MODULE
    // ========================================================================
    
    /**
     * Send a message
     */
    async sendMessage() {
        if (this.isSending) return;
        
        const content = this.inputField.value.trim();
        
        // Validation
        const validationError = this.validateMessage(content);
        if (validationError) {
            this.showError(validationError);
            return;
        }
        
        this.isSending = true;
        this.sendButton.disabled = true;
        this.sendButton.textContent = 'Sending...';
        
        try {
            const response = await fetch(
                `${this.config.apiBaseUrl}/rooms/${this.currentRoomId}/send/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ content })
                }
            );
            
            const data = await response.json();
            
            if (data.success) {
                // Clear input
                this.inputField.value = '';
                
                // Reload messages
                await this.loadMessages(true);
            } else {
                this.showError(data.error || 'Failed to send message');
            }
        } catch (error) {
            console.error('[Chat] Error sending message:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.isSending = false;
            this.sendButton.disabled = false;
            this.sendButton.textContent = 'Send';
            this.inputField.focus();
        }
    }
    
    /**
     * Handle typing event
     */
    handleTyping() {
        // Clear previous timeout
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Send typing indicator to backend
        this.sendTypingIndicator();
        
        // Set timeout to stop typing indicator
        this.typingTimeout = setTimeout(() => {
            // Typing stopped
        }, this.config.typingTimeout);
    }
    
    /**
     * Send typing indicator to backend
     */
    async sendTypingIndicator() {
        try {
            await fetch(
                `${this.config.apiBaseUrl}/rooms/${this.currentRoomId}/typing/`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    credentials: 'same-origin'
                }
            );
        } catch (error) {
            // Silently fail - typing indicator is not critical
        }
    }
    
    // ========================================================================
    // TYPING INDICATOR MODULE
    // ========================================================================
    
    /**
     * Check and update typing status
     */
    async checkTypingStatus() {
        try {
            const response = await fetch(
                `${this.config.apiBaseUrl}/rooms/${this.currentRoomId}/typing/status/`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                }
            );
            
            const data = await response.json();
            
            if (data.success) {
                this.updateTypingIndicator(data.typing_users);
            }
        } catch (error) {
            // Silently fail
        }
    }
    
    /**
     * Update typing indicator display
     * @param {Array} typingUsers - List of user names typing
     */
    updateTypingIndicator(typingUsers) {
        if (!this.typingIndicator) return;
        
        if (typingUsers.length > 0) {
            let text = '';
            if (typingUsers.length === 1) {
                text = `${typingUsers[0]} is typing...`;
            } else if (typingUsers.length === 2) {
                text = `${typingUsers[0]} and ${typingUsers[1]} are typing...`;
            } else {
                text = `${typingUsers.length} people are typing...`;
            }
            
            this.typingIndicator.textContent = text;
            this.typingIndicator.classList.remove('hidden');
        } else {
            this.typingIndicator.classList.add('hidden');
        }
    }
    
    // ========================================================================
    // UTILITIES MODULE
    // ========================================================================
    
    /**
     * Validate message content
     * @param {string} content - Message content
     * @returns {string|null} - Error message or null if valid
     */
    validateMessage(content) {
        if (!content) {
            return 'Message cannot be empty';
        }
        
        if (content.length > this.config.maxMessageLength) {
            return `Message too long (max ${this.config.maxMessageLength} characters)`;
        }
        
        return null;
    }
    
    /**
     * Format timestamp for display
     * @param {string} timestamp - ISO timestamp
     * @returns {string} - Formatted time
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        
        // Check if today
        const isToday = date.toDateString() === now.toDateString();
        
        if (isToday) {
            return date.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        } else {
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit'
            });
        }
    }
    
    /**
     * Render markdown content safely
     * @param {string} text - Markdown text to render
     * @returns {string} - Sanitized HTML
     */
    renderMarkdown(text) {
        // Check if marked and DOMPurify are available
        if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
            console.warn('[Chat] Markdown libraries not loaded, falling back to plain text');
            return this.escapeHtml(text);
        }
        
        try {
            // Configure marked options for better rendering
            marked.setOptions({
                breaks: true,        // Convert \n to <br>
                gfm: true,           // GitHub Flavored Markdown
                headerIds: false,    // Don't add IDs to headers
                mangle: false,       // Don't escape autolinked email addresses
                sanitize: false      // We'll use DOMPurify instead
            });
            
            // Parse markdown
            const rawHtml = marked.parse(text);
            
            // Sanitize HTML to prevent XSS attacks
            const cleanHtml = DOMPurify.sanitize(rawHtml, {
                ALLOWED_TAGS: [
                    'p', 'br', 'strong', 'em', 'u', 's', 'code', 'pre',
                    'a', 'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3',
                    'h4', 'h5', 'h6', 'hr', 'table', 'thead', 'tbody', 'tr',
                    'th', 'td', 'img'
                ],
                ALLOWED_ATTR: ['href', 'title', 'target', 'rel', 'src', 'alt', 'class'],
                ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
            });
            
            return cleanHtml;
        } catch (error) {
            console.error('[Chat] Markdown rendering error:', error);
            return this.escapeHtml(text);
        }
    }
    
    /**
     * Escape HTML to prevent XSS (fallback for plain text)
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Get CSRF token from cookie
     * @returns {string} - CSRF token
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    /**
     * Show loading state
     */
    showLoadingState() {
        if (this.messagesContainer) {
            this.messagesContainer.innerHTML = '<div class="loading-state">Loading messages...</div>';
        }
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'chat-error';
        errorDiv.textContent = message;
        
        // Insert at top of chat
        if (this.messagesContainer) {
            this.messagesContainer.insertBefore(errorDiv, this.messagesContainer.firstChild);
            
            // Remove after 5 seconds
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
    }
}

// Initialize chat when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize chat for all users (authenticated or not)
    const chatContainer = document.getElementById('chat-container');
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    
    if (chatContainer && chatToggleBtn) {
        window.chatManager = new ChatManager();
        window.chatManager.init();
        
        // Add pulse animation for first-time visitors
        const hasSeenChat = localStorage.getItem('nmtsa-chat-seen');
        if (!hasSeenChat) {
            chatToggleBtn.classList.add('pulse');
            
            // Remove pulse after first interaction
            chatToggleBtn.addEventListener('click', () => {
                chatToggleBtn.classList.remove('pulse');
                localStorage.setItem('nmtsa-chat-seen', 'true');
            }, { once: true });
        }
        
        console.log('[Chat] System initialized and ready');
    } else {
        console.warn('[Chat] Required elements not found in DOM');
    }
});
