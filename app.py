import os

import eel
from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize AI clients
anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize Eel with the web folder
eel.init('web')

# Store conversation history and selected model
conversation_history = []
selected_model = "claude"  # Default to Claude

@eel.expose
def set_model(model_name):
    """Set the AI model to use (claude or gpt4o)"""
    global selected_model
    print(f"DEBUG: Switching from {selected_model} to {model_name}")  # Debug line
    if model_name in ["claude", "gpt4o"]:
        selected_model = model_name
        print(f"DEBUG: Model successfully changed to {selected_model}")  # Debug line
        return True
    print(f"DEBUG: Invalid model name: {model_name}")  # Debug line
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
def clear_conversation():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    return True

# Start the Eel app
if __name__ == '__main__':
    eel.start('index.html', size=(800, 600))
