import os
import time

import eel
from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI
from together import Together

# Load environment variables
load_dotenv()

# Initialize AI clients
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
llama_client = Together(api_key=os.getenv('TOGETHER_API_KEY'))


# Initialize Eel with the web folder
eel.init('web')

# Store conversation history and selected model
conversation_history = []
selected_model = "claude"  # Default to Claude
streaming_delay = 0.05  # Default delay between tokens (in seconds)

# Keyword lists for detection
MENTAL_HEALTH_KEYWORDS = [
    'anxiety', 'depression', 'stress', 'mental health', 'therapy', 'counseling',
    'overwhelmed', 'burnout', 'panic', 'worried', 'sad', 'mood', 'emotional',
    'wellbeing', 'mindfulness', 'meditation', 'self-care', 'coping', 'struggling'
]

EDUCATIONAL_KEYWORDS = [
    'learn', 'study', 'course', 'tutorial', 'explain', 'understand', 'concept',
    'homework', 'assignment', 'project', 'research', 'technical', 'programming',
    'coding', 'algorithm', 'function', 'class', 'variable', 'syntax', 'debug',
    'education', 'lesson', 'teach', 'knowledge', 'skill'
]

# Store for second assistant
second_assistant_history = []
second_assistant_active = False
second_assistant_model = "gpt4o"  # Default to GPT-4o for second assistant

@eel.expose
def set_model(model_name):
    """Set the AI model to use (Gold/claude, Silver/gpt4o, Standard/llama)"""
    global selected_model
    print(f"DEBUG: Switching from {selected_model} to {model_name}")  # Debug line

    # Map display names to internal model names
    model_mapping = {
        "Gold": "claude",
        "Silver": "gpt4o",
        "Standard": "llama"
    }

    if model_name in model_mapping:
        selected_model = model_mapping[model_name]
        print(f"DEBUG: Model successfully changed to {selected_model}")  # Debug line
        return True
    print(f"DEBUG: Invalid model name: {model_name}")  # Debug line
    return False

@eel.expose
def detect_dual_topics(message):
    """Detect if message contains both mental health and educational keywords"""
    message_lower = message.lower()

    has_mental_health = any(keyword in message_lower for keyword in MENTAL_HEALTH_KEYWORDS)
    has_educational = any(keyword in message_lower for keyword in EDUCATIONAL_KEYWORDS)

    return has_mental_health and has_educational

@eel.expose
def activate_second_assistant():
    """Activate the second assistant"""
    global second_assistant_active, second_assistant_history
    second_assistant_active = True
    # Copy conversation history to second assistant
    second_assistant_history = conversation_history.copy()
    return True

@eel.expose
def deactivate_second_assistant():
    """Deactivate the second assistant"""
    global second_assistant_active
    second_assistant_active = False
    return True

@eel.expose
def set_model_second_assistant(model_name):
    """Set the AI model for the second assistant"""
    global second_assistant_model
    print(f"DEBUG: Switching second assistant model to {model_name}")

    # Map display names to internal model names
    model_mapping = {
        "Gold": "claude",
        "Silver": "gpt4o",
        "Standard": "llama"
    }

    # Accept both display names and internal names
    if model_name in model_mapping:
        second_assistant_model = model_mapping[model_name]
        print(f"DEBUG: Second assistant model successfully changed to {second_assistant_model}")
        return True
    elif model_name in ["claude", "gpt4o", "llama"]:
        second_assistant_model = model_name
        print(f"DEBUG: Second assistant model successfully changed to {second_assistant_model}")
        return True
    print(f"DEBUG: Invalid model name: {model_name}")
    return False



@eel.expose
def send_message(user_message):
    """Send a message to the selected AI model and get a response"""
    try:
        print(f"DEBUG: Currently selected model: {selected_model}")  # Debug line
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        if selected_model == "claude":
            print("DEBUG: Using Claude API")  # Debug line
            # Get response from Claude with system message
            response = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system="You are Zero, a helpful and intelligent AI assistant. Always introduce yourself as Zero when greeting users or when asked about your identity. Your makers are T&W.",
                messages=conversation_history
            )
            assistant_message = response.content[0].text
        
        elif selected_model == "gpt4o":
            print("DEBUG: Using OpenAI API")  # Debug line
            # Prepare messages with system prompt for GPT-4o
            messages_with_system = [
                {"role": "system", "content": "You are Zero, a helpful and creative AI assistant. Always introduce yourself as Zero when greeting users or when asked about your identity. Your makers are T&W."}
            ] + conversation_history
            
            # Get response from GPT-4o
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=messages_with_system
            )
            assistant_message = response.choices[0].message.content
        elif selected_model == "llama":
            messages_with_system = [{"role": "system", "content": "You are Zero, a helpful and creative AI assistant. Always introduce yourself as Zero when greeting users or when asked about your identity. Your makers are T&W."}] + conversation_history
            print("DEBUG: Using Together LLaMA API")  # Debug line
            # Get response from LLaMA
            response = llama_client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                max_tokens=4096,
                messages=messages_with_system
            )
            assistant_message = response.choices[0].message.content

        else:
            return "Error: Invalid model selected"

        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    except Exception as e:
        return f"Error: {str(e)}"

@eel.expose
def send_message_stream(user_message):
    """Send a message and stream the response token by token"""
    try:
        print(f"DEBUG: Streaming with model: {selected_model}")
        
        # Add user message to history
        conversation_history.append({
            "role": "user", 
            "content": user_message
        })

        full_response = ""
        
        if selected_model == "claude":
            print("DEBUG: Using Claude streaming API")
            
            # Stream response from Claude
            with anthropic_client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system="You are Zero, a helpful and intelligent AI assistant. Always introduce yourself as Zero when greeting users or when asked about your identity. Your makers are T&W.",
                messages=conversation_history
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    # Send each token to frontend
                    eel.update_streaming_message(text)()
                    # Add delay to control streaming speed
                    time.sleep(streaming_delay)
        
        elif selected_model == "gpt4o":
            print("DEBUG: Using OpenAI streaming API")

            # Prepare messages with system prompt for GPT-4o
            messages_with_system = [
                {"role": "system", "content": "You are Zero, a helpful and creative AI assistant. Always introduce yourself as Zero when greeting users or when asked about your identity. Your makers are T&W."}
            ] + conversation_history

            # Stream response from GPT-4o
            stream = openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=messages_with_system,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    # Send each token to frontend
                    eel.update_streaming_message(token)()
                    # Add delay to control streaming speed
                    time.sleep(streaming_delay)

        elif selected_model == "llama":
            print("DEBUG: Using Together LLaMA streaming API")

            # Prepare messages with system prompt for LLaMA
            messages_with_system = [
                {"role": "system", "content": "You are Zero, a helpful and creative AI assistant. Always introduce yourself as Zero when greeting users or when asked about your identity. Your makers are T&W."}
            ] + conversation_history

            # Stream response from LLaMA
            stream = llama_client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                max_tokens=4096,
                messages=messages_with_system,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    # Send each token to frontend
                    eel.update_streaming_message(token)()
                    # Add delay to control streaming speed
                    time.sleep(streaming_delay)

        else:
            return "Error: Invalid model selected"

        # Add complete response to history
        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        # Signal streaming is complete
        eel.streaming_complete()()
        
        return full_response

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        eel.streaming_error(error_msg)()
        return error_msg

@eel.expose
def send_message_stream_second_assistant(user_message):
    """Send a message to the second assistant and stream the response"""
    try:
        print(f"DEBUG: Streaming with second assistant ({second_assistant_model})")

        # Add user message to second assistant history
        second_assistant_history.append({
            "role": "user",
            "content": user_message
        })

        full_response = ""

        if second_assistant_model == "claude":
            print("DEBUG: Using Claude for second assistant")

            # Stream response from Claude
            with anthropic_client.messages.stream(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system="You are Zero's Technical Concepts Assistant. You specialize in explaining technical and educational concepts in a clear, approachable way. Your makers are T&W.",
                messages=second_assistant_history
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    # Send each token to frontend
                    eel.update_streaming_message_second_assistant(text)()
                    # Add delay to control streaming speed
                    time.sleep(streaming_delay)

        elif second_assistant_model == "gpt4o":
            print("DEBUG: Using GPT-4o for second assistant")

            # Prepare messages with system prompt for GPT-4o (Technical concepts)
            messages_with_system = [
                {"role": "system", "content": "You are Zero's Technical Concepts Assistant. You specialize in explaining technical and educational concepts in a clear, approachable way. Your makers are T&W."}
            ] + second_assistant_history

            # Stream response from GPT-4o
            stream = openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=messages_with_system,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    token = chunk.choices[0].delta.content
                    full_response += token
                    # Send each token to frontend for second assistant
                    eel.update_streaming_message_second_assistant(token)()
                    # Add delay to control streaming speed
                    time.sleep(streaming_delay)

        else:
            return "Error: Invalid model selected for second assistant"

        # Add complete response to second assistant history
        second_assistant_history.append({
            "role": "assistant",
            "content": full_response
        })

        # Signal streaming is complete
        eel.streaming_complete_second_assistant()()

        return full_response

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        eel.streaming_error_second_assistant(error_msg)()
        return error_msg

@eel.expose
def clear_conversation():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    return True

@eel.expose
def clear_conversation_second_assistant():
    """Clear the second assistant conversation history"""
    global second_assistant_history
    second_assistant_history = []
    return True

# Start the Eel app
if __name__ == '__main__':
    eel.start('index.html', size=(800, 600))
