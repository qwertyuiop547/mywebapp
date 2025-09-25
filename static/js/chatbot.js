/**
 * Barangay Portal AI Chatbot
 * Supports multi-language (English/Filipino) conversation
 */

class BarangayChatbot {
    constructor() {
        this.sessionId = null;
        this.isOpen = false;
        this.currentLanguage = this.getInitialLanguage();
        this.languagePrefix = this.getLanguagePrefix();
        this.apiEndpoints = {
            chat: `${this.languagePrefix}/chatbot/api/chat/`,
            startSession: `${this.languagePrefix}/chatbot/api/session/start/`,
            endSession: `${this.languagePrefix}/chatbot/api/session/end/`,
            feedback: `${this.languagePrefix}/chatbot/api/feedback/`,
            uploadImage: `${this.languagePrefix}/chatbot/api/upload-image/`,
            getAlerts: `${this.languagePrefix}/chatbot/api/alerts/`
        };
        
        // Voice recognition setup
        this.isListening = false;
        this.recognition = null;
        this.initSpeechRecognition();
        
        // Notification system
        this.notificationInterval = null;
        this.lastAlertCheck = Date.now();
        
        // Conversation tracking
        this.hasStartedConversation = false;
        
        this.translations = {
            en: {
                title: 'Barangay Assistant',
                placeholder: 'Type your message...',
                send: 'Send',
                helpful: 'Helpful',
                notHelpful: 'Not helpful',
                typing: 'Assistant is typing...',
                error: 'Sorry, something went wrong. Please try again.',
                networkError: 'Network error. Please check your connection.',
                close: 'Close chat',
                voiceStart: 'Start voice input',
                voiceStop: 'Stop voice input',
                voiceListening: 'Listening...',
                uploadImage: 'Upload image',
                imageUploaded: 'Image uploaded successfully',
                imageError: 'Error uploading image'
            },
            fil: {
                title: 'Barangay Assistant',
                placeholder: 'I-type ang inyong mensahe...',
                send: 'Ipadala',
                helpful: 'Nakatulong',
                notHelpful: 'Hindi nakatulong',
                typing: 'Sumasagot ang assistant...',
                error: 'Pasensya na, may problema. Subukan ulit.',
                networkError: 'May problema sa network. Tingnan ang connection.',
                close: 'Isara ang chat',
                voiceStart: 'Simulan ang voice input',
                voiceStop: 'Itigil ang voice input', 
                voiceListening: 'Nakikinig...',
                uploadImage: 'Mag-upload ng larawan',
                imageUploaded: 'Successfully na-upload ang larawan',
                imageError: 'May error sa pag-upload ng larawan'
            }
        };
        
        this.init();
    }
    
    getInitialLanguage() {
        // Get language from Django context or URL
        const html = document.documentElement;
        const lang = html.getAttribute('lang') || 
                    window.location.pathname.match(/^\/(en|fil)\//) ? 
                    window.location.pathname.match(/^\/(en|fil)\//)[1] : 'en';
        return lang;
    }
    
    getLanguagePrefix() {
        // Extract language prefix from current URL for API calls
        const pathMatch = window.location.pathname.match(/^\/(en|fil)\//);
        return pathMatch ? `/${pathMatch[1]}` : '/en';
    }
    
    init() {
        this.createChatInterface();
        this.attachEventListeners();
        this.loadStoredSession();
        this.startNotificationSystem();
    }
    
    initSpeechRecognition() {
        // Initialize Web Speech API
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.currentLanguage === 'fil' ? 'tl-PH' : 'en-US';
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.inputField.value = transcript;
                this.stopVoiceRecognition();
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopVoiceRecognition();
            };
            
            this.recognition.onend = () => {
                this.stopVoiceRecognition();
            };
        }
    }
    
    createChatInterface() {
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'chatbot-toggle';
        toggleButton.innerHTML = '<i class="fas fa-comments"></i>';
        toggleButton.setAttribute('aria-label', this.translations[this.currentLanguage].title);
        document.body.appendChild(toggleButton);
        
        // Create chatbot container
        const container = document.createElement('div');
        container.className = 'chatbot-container';
        container.innerHTML = this.getChatHTML();
        document.body.appendChild(container);
        
        this.toggleButton = toggleButton;
        this.container = container;
        this.messagesContainer = container.querySelector('.chatbot-messages');
        this.inputField = container.querySelector('.chatbot-input');
        this.sendButton = container.querySelector('.chatbot-send-btn');
        this.voiceButton = container.querySelector('.chatbot-voice-btn');
        this.imageButton = container.querySelector('.chatbot-image-btn');
        this.imageInput = container.querySelector('.chatbot-image-input');
        this.suggestionsContainer = container.querySelector('.chatbot-suggestions');
        this.typingIndicator = container.querySelector('.typing-indicator');
    }
    
    getChatHTML() {
        const t = this.translations[this.currentLanguage];
        return `
            <div class="chatbot-header">
                <div class="chatbot-title">
                    <i class="fas fa-robot"></i>
                    ${t.title}
                </div>
                <button class="chatbot-close" aria-label="${t.close}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="chatbot-language">
                <button class="language-btn ${this.currentLanguage === 'en' ? 'active' : ''}" data-lang="en">
                    English
                </button>
                <button class="language-btn ${this.currentLanguage === 'fil' ? 'active' : ''}" data-lang="fil">
                    Filipino
                </button>
            </div>
            
            <div class="chatbot-messages">
                <!-- Messages will be added here -->
            </div>
            
            <div class="typing-indicator">
                <div class="message-avatar bot">
                    <i class="fas fa-robot"></i>
                </div>
                <span>${t.typing}</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
            
            <div class="chatbot-suggestions">
                <!-- Suggestions will be added here -->
            </div>
            
            <div class="chatbot-input-area">
                <input type="text" class="chatbot-input" placeholder="${t.placeholder}" maxlength="500">
                <input type="file" class="chatbot-image-input" accept="image/*" style="display: none;">
                <button class="chatbot-image-btn" aria-label="${t.uploadImage}" title="${t.uploadImage}">
                    <i class="fas fa-image"></i>
                </button>
                <button class="chatbot-voice-btn" aria-label="${t.voiceStart}" title="${t.voiceStart}">
                    <i class="fas fa-microphone"></i>
                </button>
                <button class="chatbot-send-btn" aria-label="${t.send}">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
    }
    
    attachEventListeners() {
        // Toggle button
        this.toggleButton.addEventListener('click', () => this.toggleChat());
        
        // Close button
        this.container.querySelector('.chatbot-close').addEventListener('click', () => this.closeChat());
        
        // Send button
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Voice button
        this.voiceButton.addEventListener('click', () => this.toggleVoiceRecognition());
        
        // Image button
        this.imageButton.addEventListener('click', () => this.imageInput.click());
        
        // Image input
        this.imageInput.addEventListener('change', (e) => this.handleImageUpload(e));
        
        // Input field
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Hide suggestions when user starts typing
        this.inputField.addEventListener('input', () => {
            if (this.inputField.value.trim().length > 0) {
                this.hideSuggestions();
            } else if (!this.hasStartedConversation) {
                // Only show default suggestions when input is cleared AND conversation hasn't started
                this.showDefaultSuggestions();
            }
        });
        
        // Language buttons
        this.container.querySelectorAll('.language-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.changeLanguage(e.target.dataset.lang));
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.container.contains(e.target) && !this.toggleButton.contains(e.target)) {
                // Don't close if clicking on a suggestion button or any chatbot element
                if (!e.target.closest('.suggestion-btn') && !e.target.closest('.chatbot-container')) {
                    this.closeChat();
                }
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
        });
    }
    
    async toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            await this.openChat();
        }
    }
    
    async openChat() {
        this.isOpen = true;
        this.container.classList.add('show');
        this.toggleButton.classList.add('active');
        this.toggleButton.innerHTML = '<i class="fas fa-times"></i>';
        
        // Start session if not exists
        if (!this.sessionId) {
            await this.startSession();
        }
        
        // Focus input
        setTimeout(() => {
            this.inputField.focus();
        }, 300);
    }
    
    closeChat() {
        this.isOpen = false;
        this.container.classList.remove('show');
        this.toggleButton.classList.remove('active');
        this.toggleButton.innerHTML = '<i class="fas fa-comments"></i>';
    }
    
    async startSession() {
        try {
            console.log('Starting session with URL:', this.apiEndpoints.startSession);
            const response = await fetch(this.apiEndpoints.startSession, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    language: this.currentLanguage
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionId = data.session_id;
                
                // Add welcome message
                this.addMessage('bot', data.welcome_message);
                
                // Show suggestions
                if (data.suggestions && data.suggestions.length > 0) {
                    this.showSuggestions(data.suggestions);
                }
                
                // Store session
                localStorage.setItem('chatbot_session_id', this.sessionId);
            }
        } catch (error) {
            console.error('Failed to start chat session:', error);
        }
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Disable send button during processing
        this.sendButton.disabled = true;
        
        // Mark conversation as started and hide suggestions permanently
        this.hasStartedConversation = true;
        this.hideSuggestions();
        
        // Add user message
        this.addMessage('user', message);
        this.inputField.value = '';
        
        // Show typing indicator
        this.showTyping();
        
        try {
            console.log('Sending message to URL:', this.apiEndpoints.chat);
            const response = await fetch(this.apiEndpoints.chat, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    language: this.currentLanguage
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Update session ID if new
                if (data.session_id && data.session_id !== this.sessionId) {
                    this.sessionId = data.session_id;
                    localStorage.setItem('chatbot_session_id', this.sessionId);
                }
                
                // Hide typing and add bot response
                this.hideTyping();
                const messageElement = this.addMessage('bot', data.response, data.message_id);
                
                // Add feedback buttons
                this.addFeedbackButtons(messageElement, data.message_id);
                
                // Only show suggestions if conversation hasn't started yet
                if (data.suggestions && data.suggestions.length > 0 && !this.hasStartedConversation) {
                    this.showSuggestions(data.suggestions);
                }
                
            } else {
                throw new Error('Network response was not ok');
            }
        } catch (error) {
            console.error('Chat error:', error);
            console.error('API endpoint used:', this.apiEndpoints.chat);
            console.error('Current language:', this.currentLanguage);
            this.hideTyping();
            this.addMessage('bot', this.translations[this.currentLanguage].networkError);
        } finally {
            this.sendButton.disabled = false;
        }
    }
    
    addMessage(type, content, messageId = null, messageClass = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${type}`;
        messageDiv.dataset.messageId = messageId;
        
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${type}`;
        avatar.innerHTML = type === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = `message-content ${messageClass || ''}`;
        
        // Ensure proper text display and wrapping
        messageContent.style.whiteSpace = 'pre-wrap';
        messageContent.style.wordWrap = 'break-word';
        messageContent.textContent = content;
        
        // Special styling for alerts
        if (messageClass === 'alert') {
            messageContent.style.backgroundColor = '#fff3cd';
            messageContent.style.borderLeft = '4px solid #ffc107';
            messageContent.style.fontWeight = 'bold';
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addFeedbackButtons(messageElement, messageId) {
        if (!messageId) return;
        
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'message-feedback';
        
        const helpfulBtn = document.createElement('button');
        helpfulBtn.className = 'feedback-btn';
        helpfulBtn.innerHTML = '<i class="fas fa-thumbs-up"></i>';
        helpfulBtn.title = this.translations[this.currentLanguage].helpful;
        helpfulBtn.addEventListener('click', () => this.submitFeedback(messageId, true, helpfulBtn));
        
        const notHelpfulBtn = document.createElement('button');
        notHelpfulBtn.className = 'feedback-btn';
        notHelpfulBtn.innerHTML = '<i class="fas fa-thumbs-down"></i>';
        notHelpfulBtn.title = this.translations[this.currentLanguage].notHelpful;
        notHelpfulBtn.addEventListener('click', () => this.submitFeedback(messageId, false, notHelpfulBtn));
        
        feedbackDiv.appendChild(helpfulBtn);
        feedbackDiv.appendChild(notHelpfulBtn);
        
        const messageContent = messageElement.querySelector('.message-content');
        messageContent.appendChild(feedbackDiv);
    }
    
    async submitFeedback(messageId, isHelpful, button) {
        try {
            const response = await fetch(this.apiEndpoints.feedback, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    message_id: messageId,
                    is_helpful: isHelpful
                })
            });
            
            if (response.ok) {
                // Update button appearance
                button.classList.add(isHelpful ? 'helpful' : 'not-helpful');
                
                // Disable both feedback buttons
                const feedbackContainer = button.parentNode;
                feedbackContainer.querySelectorAll('.feedback-btn').forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.6';
                });
            }
        } catch (error) {
            console.error('Feedback submission error:', error);
        }
    }
    
    showSuggestions(suggestions) {
        this.clearSuggestions();
        
        suggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.className = 'suggestion-btn';
            btn.textContent = suggestion;
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.inputField.value = suggestion;
                this.sendMessage();
            });
            this.suggestionsContainer.appendChild(btn);
        });
    }
    
    clearSuggestions() {
        this.suggestionsContainer.innerHTML = '';
    }
    
    hideSuggestions() {
        this.clearSuggestions();
    }
    
    showDefaultSuggestions() {
        // Only show default suggestions if input is empty and conversation hasn't started
        if (this.inputField.value.trim().length === 0 && !this.hasStartedConversation) {
            const defaultSuggestions = this.getDefaultSuggestions();
            this.showSuggestions(defaultSuggestions);
        }
    }
    
    getDefaultSuggestions() {
        const suggestions = {
            'en': [
                "File a complaint",
                "Available services", 
                "Contact information",
                "Office hours"
            ],
            'fil': [
                "Mag-file ng reklamo",
                "Available na serbisyo",
                "Contact information", 
                "Office hours"
            ]
        };
        return suggestions[this.currentLanguage] || suggestions['en'];
    }
    
    showTyping() {
        this.typingIndicator.classList.add('show');
        this.scrollToBottom();
    }
    
    hideTyping() {
        this.typingIndicator.classList.remove('show');
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    changeLanguage(newLang) {
        if (newLang === this.currentLanguage) return;
        
        this.currentLanguage = newLang;
        
        // Update API endpoints with new language prefix
        const newPrefix = `/${newLang}`;
        this.apiEndpoints = {
            chat: `${newPrefix}/chatbot/api/chat/`,
            startSession: `${newPrefix}/chatbot/api/session/start/`,
            endSession: `${newPrefix}/chatbot/api/session/end/`,
            feedback: `${newPrefix}/chatbot/api/feedback/`
        };
        
        // Update language buttons
        this.container.querySelectorAll('.language-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === newLang);
        });
        
        // Update placeholder
        this.inputField.placeholder = this.translations[newLang].placeholder;
        
        // Update typing indicator text
        this.typingIndicator.querySelector('span').textContent = this.translations[newLang].typing;
        
        // Add language change message
        const changeMessage = newLang === 'en' 
            ? "Language changed to English. How can I help you?"
            : "Nabago ang wika sa Filipino. Paano kita matutulungan?";
        
        this.addMessage('bot', changeMessage);
    }
    
    toggleVoiceRecognition() {
        if (!this.recognition) {
            alert('Voice recognition not supported in this browser');
            return;
        }
        
        if (this.isListening) {
            this.stopVoiceRecognition();
        } else {
            this.startVoiceRecognition();
        }
    }
    
    startVoiceRecognition() {
        if (!this.recognition) return;
        
        this.isListening = true;
        this.voiceButton.classList.add('listening');
        this.voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
        this.voiceButton.title = this.translations[this.currentLanguage].voiceStop;
        
        // Update recognition language
        this.recognition.lang = this.currentLanguage === 'fil' ? 'tl-PH' : 'en-US';
        
        try {
            this.recognition.start();
            this.inputField.placeholder = this.translations[this.currentLanguage].voiceListening;
        } catch (error) {
            console.error('Voice recognition error:', error);
            this.stopVoiceRecognition();
        }
    }
    
    stopVoiceRecognition() {
        if (!this.recognition) return;
        
        this.isListening = false;
        this.voiceButton.classList.remove('listening');
        this.voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        this.voiceButton.title = this.translations[this.currentLanguage].voiceStart;
        this.inputField.placeholder = this.translations[this.currentLanguage].placeholder;
        
        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Error stopping voice recognition:', error);
        }
    }
    
    async handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert('Image size should be less than 10MB');
            return;
        }
        
        // Show loading
        this.showTyping();
        
        const formData = new FormData();
        formData.append('image', file);
        formData.append('session_id', this.sessionId);
        formData.append('language', this.currentLanguage);
        
        try {
            const response = await fetch(this.apiEndpoints.uploadImage, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                this.hideTyping();
                
                // Add image message
                this.addImageMessage(file);
                
                // Add AI response
                this.addMessage('bot', data.response);
                
                // Show suggestions if any
                if (data.suggestions && data.suggestions.length > 0) {
                    this.showSuggestions(data.suggestions);
                }
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Image upload error:', error);
            this.hideTyping();
            this.addMessage('bot', this.translations[this.currentLanguage].imageError);
        }
        
        // Clear file input
        event.target.value = '';
    }
    
    addImageMessage(file) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chatbot-message user';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar user';
        avatar.innerHTML = '<i class="fas fa-user"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = '200px';
        img.style.maxHeight = '200px';
        img.style.borderRadius = '8px';
        
        const caption = document.createElement('div');
        caption.textContent = `📸 ${file.name}`;
        caption.style.fontSize = '12px';
        caption.style.marginTop = '5px';
        caption.style.opacity = '0.8';
        
        messageContent.appendChild(img);
        messageContent.appendChild(caption);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    async startNotificationSystem() {
        // Check for proactive alerts every 5 minutes
        this.notificationInterval = setInterval(() => {
            this.checkProactiveAlerts();
        }, 5 * 60 * 1000);
        
        // Check immediately on start
        this.checkProactiveAlerts();
    }
    
    async checkProactiveAlerts() {
        try {
            const response = await fetch(this.apiEndpoints.getAlerts, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.alerts && data.alerts.length > 0) {
                    data.alerts.forEach(alert => {
                        this.showProactiveAlert(alert);
                    });
                }
            }
        } catch (error) {
            console.error('Error checking alerts:', error);
        }
    }
    
    showProactiveAlert(alert) {
        // Create notification badge on toggle button
        if (!this.isOpen) {
            this.toggleButton.classList.add('has-alert');
            
            // Show browser notification if permission granted
            if (Notification.permission === 'granted') {
                new Notification('Barangay Alert', {
                    body: alert.message,
                    icon: '/static/images/basey-seal.png'
                });
            }
        }
        
        // Add alert message to chat
        this.addMessage('bot', `🚨 ${alert.message}`, null, 'alert');
    }
    
    loadStoredSession() {
        const storedSessionId = localStorage.getItem('chatbot_session_id');
        if (storedSessionId) {
            this.sessionId = storedSessionId;
        }
    }
    
    async endSession() {
        if (!this.sessionId) return;
        
        try {
            await fetch(this.apiEndpoints.endSession, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
        } catch (error) {
            console.error('Failed to end session:', error);
        } finally {
            this.sessionId = null;
            localStorage.removeItem('chatbot_session_id');
        }
    }
    
    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        return cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not in admin pages
    if (!window.location.pathname.includes('/admin/')) {
        window.barangayChatbot = new BarangayChatbot();
        
        // Handle page unload
        window.addEventListener('beforeunload', () => {
            if (window.barangayChatbot) {
                window.barangayChatbot.endSession();
            }
        });
    }
});

// Export for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BarangayChatbot;
}
