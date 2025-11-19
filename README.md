ChatTree: Terminal-Based Multi-Chat Interface for Ollama

# Overview
ChatTree is a terminal-based UI for managing multiple chat sessions with local LLMs using Ollama, inspired by nvim-tree. It features a sidebar for navigating chat sessions and a main area for conversations, with Vim-like keybindings.

---

# Prerequisites

- Ollama: Install from ollama.ai and pull models (e.g., ollama pull llama3, ollama pull mistral).
- Python 3.8+: Ensure installed (python3 --version).
- Dependencies: Install prompt_toolkit and requests:pip install prompt_toolkit requests


- Hardware: 16GB+ RAM, 10-20GB storage, GPU optional.


# Setup
- Create a directory: mkdir chattree && cd chattree.
- Clone the Repository.
- Ensure Ollama is running: ollama serve (in a separate terminal).
- Run the app:python chattree.py


# Interface:
- Left: Sidebar with chat sessions (e.g., "> Session 1" indicates the active session).
- Right: Conversation history for the selected session.
- Bottom: Input field for messages or commands.


# Keybindings:
- Quit: Ctrl+q (was q)
- Move down: Ctrl+j (was j)
- Move up: Ctrl+k (was k)
- Send message: Enter (unchanged)
- Create session: Ctrl+c (was c)
- Delete session: Ctrl+d (was d)
- Rename session: Ctrl+r (was r)
- Save history: Ctrl+y (was y)
- Toggle focus: Ctrl+t (was tab)


# Customization
- Add Models: Edit load_sessions in chattree.py to include models like gemma2.
- Keybindings: Modify bindings in chattree.py for custom keys.
- UI: Adjust create_layout for different sidebar/chat area sizes.


# Troubleshooting
- Ollama Errors: Ensure ollama serve is running and models are pulled (ollama ls).
- Performance: Use smaller models (e.g., mistral:7b) for low-end hardware.
- Terminal: Use a modern terminal (e.g., Alacritty, iTerm2) for proper rendering.

