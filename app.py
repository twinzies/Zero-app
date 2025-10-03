import eel
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Initialize Eel with the web folder
eel.init('web')

# Store conversation history
conversation_history = []

@eel.expose
def send_message(user_message):
    """Send a message to Claude and get a response"""
    try:
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Get response from Claude
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=conversation_history
        )

        # Extract assistant's response
        assistant_message = response.content[0].text

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
