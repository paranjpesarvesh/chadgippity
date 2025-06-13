ChatTree: Terminal-Based Multi-Chat Interface for Ollama
Overview
ChatTree is a terminal-based UI for managing multiple chat sessions with local LLMs using Ollama, inspired by nvim-tree. It features a sidebar for navigating chat sessions and a main area for conversations, with Vim-like keybindings.
Prerequisites

Ollama: Install from ollama.ai and pull models (e.g., ollama pull llama3, ollama pull mistral).
Python 3.8+: Ensure installed (python3 --version).
Dependencies: Install prompt_toolkit and requests:pip install prompt_toolkit requests


Hardware: 16GB+ RAM, 10-20GB storage, GPU optional.

Setup

Create a directory: mkdir chattree && cd chattree.
Save chattree.py and README.md in the directory.
Ensure Ollama is running: ollama serve (in a separate terminal).
Run the app:python chattree.py



Usage

Interface:
Left: Sidebar with chat sessions (e.g., "> Session 1" indicates the active session).
Right: Conversation history for the selected session.
Bottom: Input field for messages or commands.


Keybindings:
j/k: Navigate sessions in the sidebar.
Enter: Send a message or confirm a rename.
c: Create a new session.
d: Delete the current session (if >1 session exists).
r: Rename the current session (type new name in input field).
q: Quit.


Example:
Start the app, select "Session 1" (uses Llama3).
Type "What is AI?" and press Enter.
Press j to move to "Session 2" (uses Mistral), type a new message.
Press c to create a new session, r to rename, or d to delete.



Files

chattree.py: Main application script.
sessions.json: Auto-generated file storing session data (model, history).
README.md: This file.

Customization

Add Models: Edit load_sessions in chattree.py to include models like gemma2.
Keybindings: Modify bindings in chattree.py for custom keys.
UI: Adjust create_layout for different sidebar/chat area sizes.

Troubleshooting

Ollama Errors: Ensure ollama serve is running and models are pulled (ollama ls).
Performance: Use smaller models (e.g., mistral:7b) for low-end hardware.
Terminal: Use a modern terminal (e.g., Alacritty, iTerm2) for proper rendering.

Next Steps

Add session folders in the sidebar.
Integrate with Neovim as a plugin.
Add a command palette for quick actions.


