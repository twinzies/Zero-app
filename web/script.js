// Function to add a message to the chat
function addMessage(content, isUser) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You' : 'Claude';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    messageDiv.appendChild(label);
    messageDiv.appendChild(messageContent);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Function to send a message
async function sendMessage() {
    const input = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();

    if (!message) return;

    // Disable input while processing
    input.disabled = true;
    sendBtn.disabled = true;

    // Add user message to chat
    addMessage(message, true);

    // Clear input
    input.value = '';

    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Claude is typing...';
    loadingDiv.id = 'loading-indicator';
    document.getElementById('chat-container').appendChild(loadingDiv);

    try {
        // Send message to Python backend
        const response = await eel.send_message(message)();

        // Remove loading indicator
        const loading = document.getElementById('loading-indicator');
        if (loading) loading.remove();

        // Add assistant response to chat
        addMessage(response, false);
    } catch (error) {
        // Remove loading indicator
        const loading = document.getElementById('loading-indicator');
        if (loading) loading.remove();

        addMessage(`Error: ${error}`, false);
    }

    // Re-enable input
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
}

// Function to clear the chat
async function clearChat() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = '';

    try {
        await eel.clear_conversation()();
    } catch (error) {
        console.error('Error clearing conversation:', error);
    }
}

// Handle Enter key in textarea
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Focus on input when page loads
window.onload = function() {
    document.getElementById('user-input').focus();
};
