// Function to add a message to the chat
function addMessage(content, isUser) {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You' : 'Zero';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    messageDiv.appendChild(label);
    messageDiv.appendChild(messageContent);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Global variable to track current streaming message
let currentStreamingMessage = null;

// Function to add a streaming message placeholder
function addStreamingMessage() {
    const chatContainer = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.id = 'streaming-message';

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = 'Zero';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = '';

    // Add typing indicator
    const typingIndicator = document.createElement('span');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.textContent = '▋';
    messageContent.appendChild(typingIndicator);

    messageDiv.appendChild(label);
    messageDiv.appendChild(messageContent);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    currentStreamingMessage = messageContent;
    return messageDiv;
}

// Function called by Python to update streaming message
eel.expose(update_streaming_message);
function update_streaming_message(token) {
    if (currentStreamingMessage) {
        // Remove typing indicator if it exists
        const typingIndicator = currentStreamingMessage.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        // Add the new token
        currentStreamingMessage.textContent += token;
        
        // Add typing indicator back
        const newTypingIndicator = document.createElement('span');
        newTypingIndicator.className = 'typing-indicator';
        newTypingIndicator.textContent = '▋';
        currentStreamingMessage.appendChild(newTypingIndicator);
        
        // Scroll to bottom
        document.getElementById('chat-container').scrollTop = document.getElementById('chat-container').scrollHeight;
    }
}

// Function called when streaming is complete
eel.expose(streaming_complete);
function streaming_complete() {
    if (currentStreamingMessage) {
        // Remove typing indicator
        const typingIndicator = currentStreamingMessage.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        
        // Remove streaming ID
        const streamingDiv = document.getElementById('streaming-message');
        if (streamingDiv) {
            streamingDiv.removeAttribute('id');
        }
        
        currentStreamingMessage = null;
    }
    
    // Re-enable input
    const input = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
}

// Function called when streaming encounters an error
eel.expose(streaming_error);
function streaming_error(errorMsg) {
    if (currentStreamingMessage) {
        currentStreamingMessage.textContent = errorMsg;
        currentStreamingMessage = null;
    }
    
    // Re-enable input
    const input = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
}

// Function to send a message with streaming
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

    // Add streaming message placeholder
    addStreamingMessage();

    try {
        // Send message to Python backend (streaming)
        await eel.send_message_stream(message)();
    } catch (error) {
        streaming_error(`Error: ${error}`);
    }
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

// Function to change the AI model
async function changeModel() {
    const selector = document.getElementById('model-selector');
    const selectedModel = selector.value;
    
    try {
        await eel.set_model(selectedModel)();
        
        // Update UI to show which model is active
        const modelName = selectedModel === 'claude' ? 'Claude 3.5 Sonnet' : 'GPT-4o';
        console.log(`Now powered by ${modelName}.`);
        
        // Optionally add a visual indicator
        addMessage(`Now powered by ${modelName}.`, false);
        
    } catch (error) {
        console.error('Error switching model:', error);
        addMessage('Error switching model', false);
    }
}

// Focus on input when page loads
window.onload = function() {
    document.getElementById('user-input').focus();
};
