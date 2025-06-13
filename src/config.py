import os

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(BASE_DIR, "sessions.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "history_output.txt")
LOG_FILE = os.path.join(BASE_DIR, "chattree.log")

# Ollama API
OLLAMA_API = "http://localhost:11434/api/chat"

# Default sessions
DEFAULT_SESSIONS = {
    "Session 1": {"model": "llama3", "history": []},
    "Session 2": {"model": "mistral", "history": []},
}

# Keybindings
KEYBINDINGS = {
    "quit": "c-q",
    "move_down": "c-j",
    "move_up": "c-k",
    "send_message": "enter",
    "create_session": "c-c",
    "delete_session": "c-d",
    "rename_session": "c-r",
    "save_history": "c-y",
    "toggle_focus": "c-t",
}
