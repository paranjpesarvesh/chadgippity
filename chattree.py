from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, VSplit, HSplit, Window
from prompt_toolkit.widgets import Frame
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.application.current import get_app
import requests
import json
import os
import logging
import traceback
import time

# Setup logging to file
log_file = "chattree.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(log_file, encoding="utf-8")]
)
logger = logging.getLogger(__name__)

# Ollama API
OLLAMA_API = "http://localhost:11434/api/chat"

# Session storage
SESSION_FILE = "sessions.json"
OUTPUT_FILE = "history_output.txt"

class ChatTree:
    def __init__(self):
        self.sessions = self.load_sessions()
        self.current_session_idx = 0
        self.session_names = list(self.sessions.keys())
        self.input_buffer = Buffer()
        self.chat_content = ""
        self.session_buffer = Buffer(multiline=True, read_only=False)
        self.app = None
        self.session_window = None
        self.input_window = None
        self.start_time = time.time()  # Track startup time
        try:
            logger.debug("Initializing session display")
            self.update_session_display()
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}\n{traceback.format_exc()}")
            self.session_buffer.text = f"Error: Failed to initialize sessions: {str(e)}"

    def load_sessions(self):
        """Load sessions from JSON file."""
        default_sessions = {
            "Session 1": {"model": "llama3", "history": []},
            "Session 2": {"model": "mistral", "history": []},
        }
        if not os.path.exists(SESSION_FILE):
            logger.info(f"{SESSION_FILE} not found, using default sessions.")
            return default_sessions
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"{SESSION_FILE} is empty, using default sessions.")
                    return default_sessions
                sessions = json.loads(content)
                for name, data in sessions.items():
                    if not isinstance(data, dict) or "model" not in data or "history" not in data:
                        logger.error(f"Invalid session data for {name}")
                        return default_sessions
                return sessions
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {SESSION_FILE}: {str(e)}\n{traceback.format_exc()}")
            return default_sessions
        except Exception as e:
            logger.error(f"Error reading {SESSION_FILE}: {str(e)}\n{traceback.format_exc()}")
            return default_sessions

    def save_sessions(self):
        """Save sessions to JSON file."""
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {SESSION_FILE}: {str(e)}\n{traceback.format_exc()}")

    def update_session_display(self):
        """Update the session sidebar display."""
        try:
            logger.debug(f"Updating session display with {len(self.session_names)} sessions")
            lines = []
            for i, name in enumerate(self.session_names):
                prefix = "> " if i == self.current_session_idx else "  "
                lines.append(f"{prefix}{name}")
            if not lines:
                lines.append("No sessions available")
            self.session_buffer.text = "\n".join(lines)
            self.update_chat_display()
        except Exception as e:
            logger.error(f"Error updating session display: {str(e)}\n{traceback.format_exc()}")
            self.session_buffer.text = f"Error: Failed to update sessions: {str(e)}"

    def update_chat_display(self):
        """Update the chat area with the current session's history."""
        try:
            logger.debug(f"Updating chat display for session index {self.current_session_idx}")
            if not self.session_names:
                self.chat_content = "No sessions available."
                return
            session_name = self.session_names[self.current_session_idx]
            history = self.sessions[session_name]["history"]
            lines = []
            for msg in history:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    logger.warning(f"Invalid message in session {session_name}: {msg}")
                    continue
                role = "User" if msg["role"] == "user" else "Assistant"
                lines.append(f"{role}: {msg['content']}")
            self.chat_content = "\n".join(lines) if lines else "No messages yet."
            if self.app:
                self.app.invalidate()
        except Exception as e:
            logger.error(f"Error updating chat display: {str(e)}\n{traceback.format_exc()}")
            self.chat_content = f"Error: Failed to update chat: {str(e)}"
            if self.app:
                self.app.invalidate()

    def send_to_ollama(self, model, messages):
        """Send messages to Ollama API."""
        payload = {"model": model, "messages": messages, "stream": False}
        try:
            response = requests.post(OLLAMA_API, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"Ollama API error: {str(e)}\n{traceback.format_exc()}")
            return f"Error: {e}"

    def save_history_to_file(self):
        """Save the current session's history to a file."""
        if not self.session_names:
            logger.debug("No sessions available to save history")
            return
        session_name = self.session_names[self.current_session_idx]
        history = self.sessions[session_name]["history"]
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for msg in history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    f.write(f"{role}: {msg['content']}\n")
            # Display feedback in input buffer temporarily
            self.input_buffer.text = f"Saved history to {OUTPUT_FILE}"
            if self.app:
                self.app.invalidate()
            # Clear input buffer after short delay to prevent sending as message
            def clear_input():
                if self.input_buffer.text == f"Saved history to {OUTPUT_FILE}":
                    self.input_buffer.text = ""
                    if self.app:
                        self.app.invalidate()
            self.app.create_background_task(clear_input())
        except Exception as e:
            logger.error(f"Error saving {OUTPUT_FILE}: {str(e)}\n{traceback.format_exc()}")
            self.input_buffer.text = f"Error saving history: {e}"

    def create_layout(self):
        """Create the terminal UI layout."""
        try:
            self.session_window = Window(BufferControl(self.session_buffer), width=20)
            session_frame = Frame(self.session_window, title="Chat Sessions")
            chat_window = Frame(Window(FormattedTextControl(lambda: self.chat_content)), title="Conversation")
            self.input_window = Window(BufferControl(self.input_buffer), height=3)
            input_frame = Frame(self.input_window, title="Input")
            return Layout(
                HSplit([
                    VSplit([session_frame, chat_window]),
                    input_frame
                ])
            )
        except Exception as e:
            logger.error(f"Error creating layout: {str(e)}\n{traceback.format_exc()}")
            raise

    def focus_input(self):
        """Set focus to the input window."""
        try:
            if self.app and self.input_window:
                self.app.layout.focus(self.input_window)
                logger.debug("Focused input window")
            else:
                logger.warning("Cannot focus input: app or input_window not initialized")
        except Exception as e:
            logger.error(f"Error focusing input: {str(e)}\n{traceback.format_exc()}")

    def focus_sessions(self):
        """Set focus to the session window."""
        try:
            if self.app and self.session_window:
                self.app.layout.focus(self.session_window)
                logger.debug("Focused session window")
            else:
                logger.warning("Cannot focus sessions: app or session_window not initialized")
        except Exception as e:
            logger.error(f"Error focusing sessions: {str(e)}\n{traceback.format_exc()}")

    def get_key_bindings(self):
        """Define keybindings bound to this ChatTree instance."""
        bindings = KeyBindings()

        @bindings.add('q')
        def _(event):
            try:
                logger.debug("Keypress: q")
                event.app.exit()
            except Exception as e:
                logger.error(f"Error in quit keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('j')
        def _(event):
            try:
                logger.debug("Keypress: j")
                self.move_down()
            except Exception as e:
                logger.error(f"Error in j keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('k')
        def _(event):
            try:
                logger.debug("Keypress: k")
                self.move_up()
            except Exception as e:
                logger.error(f"Error in k keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('enter')
        def _(event):
            try:
                logger.debug("Keypress: enter")
                if get_app().layout.has_focus(self.session_window):
                    self.focus_input()
                elif self.input_buffer.text.strip().startswith("Enter new session name:"):
                    self.handle_rename()
                else:
                    self.send_message()
            except Exception as e:
                logger.error(f"Error in enter keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('c')
        def _(event):
            try:
                logger.debug("Keypress: c")
                self.create_session()
            except Exception as e:
                logger.error(f"Error in c keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('d')
        def _(event):
            try:
                logger.debug("Keypress: d")
                self.delete_session()
            except Exception as e:
                logger.error(f"Error in d keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('r')
        def _(event):
            try:
                logger.debug("Keypress: r")
                self.rename_session()
            except Exception as e:
                logger.error(f"Error in r keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('y')
        def _(event):
            try:
                logger.debug("Keypress: y")
                # Ignore if within 1 second of startup
                if time.time() - self.start_time < 1:
                    logger.debug("Ignoring y keypress during startup")
                    return
                self.save_history_to_file()
            except Exception as e:
                logger.error(f"Error in y keybinding: {str(e)}\n{traceback.format_exc()}")

        @bindings.add('tab')
        def _(event):
            try:
                logger.debug("Keypress: tab")
                if get_app().layout.has_focus(self.input_window):
                    self.focus_sessions()
                else:
                    self.focus_input()
            except Exception as e:
                logger.error(f"Error in tab keybinding: {str(e)}\n{traceback.format_exc()}")

        return bindings

    def run(self):
        """Run the application."""
        try:
            self.app = Application(
                layout=self.create_layout(),
                key_bindings=self.get_key_bindings(),
                full_screen=True
            )
            self.focus_input()
            logger.debug("Starting application")
            self.app.run()
        except Exception as e:
            logger.error(f"Application error: {str(e)}\n{traceback.format_exc()}")

    def move_down(self):
        """Move session selection down."""
        try:
            if self.current_session_idx < len(self.session_names) - 1:
                self.current_session_idx += 1
                self.update_session_display()
        except Exception as e:
            logger.error(f"Error in move_down: {str(e)}\n{traceback.format_exc()}")

    def move_up(self):
        """Move session selection up."""
        try:
            if self.current_session_idx > 0:
                self.current_session_idx -= 1
                self.update_session_display()
        except Exception as e:
            logger.error(f"Error in move_up: {str(e)}\n{traceback.format_exc()}")

    def send_message(self):
        """Send message to the current session."""
        try:
            if not self.session_names:
                logger.debug("No sessions available to send message")
                return
            message = self.input_buffer.text.strip()
            if not message:
                return
            # Validate input
            if len(message.encode()) > 1000 or any(ord(c) > 127 for c in message):
                logger.warning(f"Invalid input detected: {message}")
                self.input_buffer.text = "Invalid input, please use ASCII characters"
                return
            # Prevent feedback messages from being sent
            if message in [f"Saved history to {OUTPUT_FILE}", f"Error saving history: {str(e)}" for e in [Exception()]]:
                logger.debug(f"Ignoring feedback message: {message}")
                self.input_buffer.text = ""
                return
            session_name = self.session_names[self.current_session_idx]
            self.sessions[session_name]["history"].append({"role": "user", "content": message})
            response = self.send_to_ollama(
                self.sessions[session_name]["model"],
                self.sessions[session_name]["history"]
            )
            self.sessions[session_name]["history"].append({"role": "assistant", "content": response})
            self.input_buffer.text = ""
            self.update_chat_display()
            self.save_sessions()
        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}\n{traceback.format_exc()}")
            self.input_buffer.text = f"Error sending message: {e}"

    def create_session(self):
        """Create a new session."""
        try:
            new_session = f"Session {len(self.sessions) + 1}"
            self.sessions[new_session] = {"model": "llama3", "history": []}
            self.session_names.append(new_session)
            self.save_sessions()
            self.update_session_display()
        except Exception as e:
            logger.error(f"Error in create_session: {str(e)}\n{traceback.format_exc()}")

    def delete_session(self):
        """Delete the current session."""
        try:
            if len(self.session_names) <= 1:
                return
            session_name = self.session_names.pop(self.current_session_idx)
            del self.sessions[session_name]
            if self.current_session_idx >= len(self.session_names):
                self.current_session_idx = len(self.session_names) - 1
            self.save_sessions()
            self.update_session_display()
        except Exception as e:
            logger.error(f"Error in delete_session: {str(e)}\n{traceback.format_exc()}")

    def rename_session(self):
        """Rename the current session."""
        try:
            if not self.session_names:
                return
            self.input_buffer.text = "Enter new session name: "
            self.focus_input()
            self.app.invalidate()
        except Exception as e:
            logger.error(f"Error in rename_session: {str(e)}\n{traceback.format_exc()}")

    def handle_rename(self):
        """Process session rename from input buffer."""
        try:
            if not self.input_buffer.text.strip().startswith("Enter new session name:"):
                return
            new_name = self.input_buffer.text.replace("Enter new session name:", "").strip()
            if new_name and new_name not in self.session_names:
                old_name = self.session_names[self.current_session_idx]
                self.sessions[new_name] = self.sessions.pop(old_name)
                self.session_names[self.current_session_idx] = new_name
                self.save_sessions()
                self.update_session_display()
            self.input_buffer.text = ""
        except Exception as e:
            logger.error(f"Error in handle_rename: {str(e)}\n{traceback.format_exc()}")
            self.input_buffer.text = f"Error renaming session: {e}"

if __name__ == "__main__":
    try:
        chat_tree = ChatTree()
        chat_tree.run()
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}\n{traceback.format_exc()}")
