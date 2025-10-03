import os
import time

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
streaming_delay = 0.05  # Default delay between tokens (in seconds)

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
def clear_conversation():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    return True

# Start the Eel app
if __name__ == '__main__':
    eel.start('index.html', size=(800, 600))
