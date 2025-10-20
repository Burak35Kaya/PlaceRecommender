// DOM Elements
const locationInput = document.getElementById('location');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const loadingSpinner = document.getElementById('loadingSpinner');

// State
let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    adjustTextareaHeight();
});

// Setup Event Listeners
function setupEventListeners() {
    sendButton.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    userInput.addEventListener('input', adjustTextareaHeight);
}

// Adjust Textarea Height
function adjustTextareaHeight() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

// Handle Send Message
async function handleSendMessage() {
    const message = userInput.value.trim();
    const location = locationInput.value.trim();

    if (!message || isProcessing) return;

    if (!location) {
        showError('Lütfen önce konum giriniz.');
        locationInput.focus();
        return;
    }

    // Clear input
    userInput.value = '';
    adjustTextareaHeight();

    // Add user message to chat
    addMessage(message, 'user');

    // Disable input while processing
    setProcessingState(true);

    try {
        // Show typing indicator
        const typingId = addTypingIndicator();

        // Send request to API
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                location: location
            })
        });

        // Remove typing indicator
        removeTypingIndicator(typingId);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Bir hata oluştu');
        }

        const data = await response.json();

        // Add bot response to chat
        addMessage(data.response, 'bot');

    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        showError(error.message || 'Bir hata oluştu. Lütfen tekrar deneyiniz.');
    } finally {
        setProcessingState(false);
    }
}

// Add Message to Chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Convert markdown links to HTML
    const htmlContent = convertMarkdownLinks(text);
    contentDiv.innerHTML = htmlContent;

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
}

// Convert Markdown Links to HTML
function convertMarkdownLinks(text) {
    // Convert markdown links [text](url) to HTML links
    let html = text.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Convert newlines to <br>
    html = html.replace(/\n/g, '<br>');

    // Convert **bold** to <strong>
    html = html.replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>');

    return html;
}

// Add Typing Indicator
function addTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'typing-indicator';
    indicatorDiv.innerHTML = '<span></span><span></span><span></span>';

    contentDiv.appendChild(indicatorDiv);
    typingDiv.appendChild(contentDiv);
    chatMessages.appendChild(typingDiv);

    scrollToBottom();

    return 'typing-indicator';
}

// Remove Typing Indicator
function removeTypingIndicator(id = 'typing-indicator') {
    const typingDiv = document.getElementById(id);
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Show Error Message
function showError(message) {
    addMessage(`❌ ${message}`, 'bot');
}

// Set Processing State
function setProcessingState(processing) {
    isProcessing = processing;
    sendButton.disabled = processing;
    userInput.disabled = processing;

    if (processing) {
        sendButton.style.opacity = '0.6';
    } else {
        sendButton.style.opacity = '1';
        userInput.focus();
    }
}

// Scroll to Bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show Loading Spinner
function showLoading() {
    loadingSpinner.classList.add('active');
}

// Hide Loading Spinner
function hideLoading() {
    loadingSpinner.classList.remove('active');
}

// Format Time
function formatTime(date) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// Auto-resize textarea on input
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});
