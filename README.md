# Zero - App (Python)

Zero - AI assistants that align with you is an agentic AI assistant platform. Zero lets you engage multiple LLM assistants that coordinate across tasks and models. Multiple assistants (chat agents) are specialized to the task and use different generative language models to respond to queries.

## Project status
WIP. See issues list.


### Key Modules
- **`app.py`**: Handles the main chat assistance flow, including API calls and tool routing.
- **`modules/settings_panel.py`**: TODO.
- **`modules/multi_assistants_tool.py`**: TODO.


## Requirements
- Python 3.10+
- An Anthropic API key
- An Open AI API key

### Python Dependencies
```
eel==0.16.0
anthropic==0.42.0
python-dotenv==1.0.0
openai==1.51.0
```

## Setup
1. **Create and activate a virtual environment**  
  While not strictly necessary, it is highly recommended to use a virtual environment to isolate dependencies and avoid conflicts with other Python projects. To create and activate a virtual environment, run the following commands:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create a `.env` file in the project root and put the API keys as follows:
   ```
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   TOGETHER_API_KEY=your_key_here
   ```


## Chat with Zero
To interact with `Zero`, execute the following command in your terminal:

```bash
python app.py
```
