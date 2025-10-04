// Global variable to track current streaming message
let currentStreamingMessageSecond = null;

// Function to add a message to the chat
function addMessageSecond(content, isUser) {
    const chatContainer = document.getElementById('chat-container-second');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = isUser ? 'You' : 'Zero Tech';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;

    messageDiv.appendChild(label);
    messageDiv.appendChild(messageContent);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Function to add a streaming message placeholder
function addStreamingMessageSecond() {
    const chatContainer = document.getElementById('chat-container-second');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';
    messageDiv.id = 'streaming-message-second';

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = 'Zero Tech';

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = '';

    const typingIndicator = document.createElement('span');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.textContent = '▋';
    messageContent.appendChild(typingIndicator);

    messageDiv.appendChild(label);
    messageDiv.appendChild(messageContent);
    chatContainer.appendChild(messageDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;

    currentStreamingMessageSecond = messageContent;
    return messageDiv;
}

// Function called by Python to update streaming message
eel.expose(update_streaming_message_second_assistant);
function update_streaming_message_second_assistant(token) {
    if (currentStreamingMessageSecond) {
        const typingIndicator = currentStreamingMessageSecond.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }

        currentStreamingMessageSecond.textContent += token;

        const newTypingIndicator = document.createElement('span');
        newTypingIndicator.className = 'typing-indicator';
        newTypingIndicator.textContent = '▋';
        currentStreamingMessageSecond.appendChild(newTypingIndicator);

        document.getElementById('chat-container-second').scrollTop = document.getElementById('chat-container-second').scrollHeight;
    }
}

// Function called when streaming is complete
eel.expose(streaming_complete_second_assistant);
function streaming_complete_second_assistant() {
    if (currentStreamingMessageSecond) {
        const typingIndicator = currentStreamingMessageSecond.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }

        const streamingDiv = document.getElementById('streaming-message-second');
        if (streamingDiv) {
            streamingDiv.removeAttribute('id');
        }

        currentStreamingMessageSecond = null;
    }

    const input = document.getElementById('user-input-second');
    const sendBtn = document.getElementById('send-btn-second');
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
}

// Function called when streaming encounters an error
eel.expose(streaming_error_second_assistant);
function streaming_error_second_assistant(errorMsg) {
    if (currentStreamingMessageSecond) {
        currentStreamingMessageSecond.textContent = errorMsg;
        currentStreamingMessageSecond = null;
    }

    const input = document.getElementById('user-input-second');
    const sendBtn = document.getElementById('send-btn-second');
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
}

// Function to send a message with streaming
async function sendMessageSecond() {
    const input = document.getElementById('user-input-second');
    const sendBtn = document.getElementById('send-btn-second');
    const message = input.value.trim();

    if (!message) return;

    input.disabled = true;
    sendBtn.disabled = true;

    addMessageSecond(message, true);
    input.value = '';

    addStreamingMessageSecond();

    try {
        await eel.send_message_stream_second_assistant(message)();
    } catch (error) {
        streaming_error_second_assistant(`Error: ${error}`);
    }
}

// Handle Enter key in textarea
function handleKeyPressSecond(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessageSecond();
    }
}

// Function to clear the chat
async function clearChatSecond() {
    const chatContainer = document.getElementById('chat-container-second');
    chatContainer.innerHTML = '';

    try {
        await eel.clear_conversation_second_assistant()();
    } catch (error) {
        console.error('Error clearing conversation:', error);
    }
}

// Function to change the AI model for second assistant
async function changeModelSecond() {
    const selector = document.getElementById('model-selector-second');
    const selectedModel = selector.value;

    try {
        await eel.set_model_second_assistant(selectedModel)();

        // Update UI to show which model is active
        const modelName = selectedModel === 'claude' ? 'Claude 3.5 Sonnet' : 'GPT-4o';
        console.log(`Second assistant now powered by ${modelName}.`);

        // Optionally add a visual indicator
        addMessageSecond(`Now powered by ${modelName}.`, false);

    } catch (error) {
        console.error('Error switching model:', error);
        addMessageSecond('Error switching model', false);
    }
}

// Focus on input when page loads
window.onload = function() {
    document.getElementById('user-input-second').focus();
};
