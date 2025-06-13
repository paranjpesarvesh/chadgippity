# ui.py
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, VSplit, HSplit, Window
from prompt_toolkit.widgets import Frame
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
import logging
import time

logger = logging.getLogger(__name__)

class ChatUI:
    def __init__(self, session_manager, keybindings, api_client):
        self.session_manager = session_manager
        self.keybindings = keybindings
        self.api_client = api_client
        self.input_buffer = Buffer()
        self.session_buffer = Buffer(multiline=True, read_only=False)
        self.chat_content = ""
        self.app = None
        self.session_window = None
        self.input_window = None
        self.start_time = time.time()
        self._last_update = 0
        self.update_session_display()

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
            logger.error(f"Error creating layout: {str(e)}")
            raise

    def update_session_display(self):
        """Update the session sidebar display."""
        try:
            current_time = time.time()
            if current_time - self._last_update < 0.1:
                return
            logger.debug(f"Updating session display with {len(self.session_manager.session_names)} sessions")
            lines = []
            for i, name in enumerate(self.session_manager.session_names):
                prefix = "> " if i == self.session_manager.current_session_idx else "  "
                lines.append(f"{prefix}{name}")
            if not lines:
                lines.append("No sessions available")
            self.session_buffer.text = "\n".join(lines)
            self.update_chat_display()
            self._last_update = current_time
        except Exception as e:
            logger.error(f"Error updating session display: {str(e)}")
            self.session_buffer.text = f"Error: Failed to update sessions: {str(e)}"

    def update_chat_display(self):
        """Update the chat area with the current session's history."""
        try:
            if not self.session_manager.session_names:
                self.chat_content = "No sessions available."
                return
            session_name = self.session_manager.session_names[self.session_manager.current_session_idx]
            history = self.session_manager.sessions[session_name]["history"]
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
            logger.error(f"Error updating chat display: {str(e)}")
            self.chat_content = f"Error: Failed to update chat: {str(e)}"
            if self.app:
                self.app.invalidate()

    def focus_input(self):
        """Set focus to the input window."""
        try:
            if self.app and self.input_window:
                self.app.layout.focus(self.input_window)
                logger.debug("Focused input window")
                # Force redraw to ensure focus is applied
                if self.app:
                    self.app.invalidate()
        except Exception as e:
            logger.error(f"Error focusing input: {str(e)}")

    def focus_sessions(self):
        """Set focus to the session window."""
        try:
            if self.app and self.session_window:
                self.app.layout.focus(self.session_window)
                logger.debug("Focused session window")
                if self.app:
                    self.app.invalidate()
        except Exception as e:
            logger.error(f"Error focusing sessions: {str(e)}")

    def run(self):
        """Run the application."""
        try:
            self.app = Application(
                layout=self.create_layout(),
                key_bindings=self.keybindings.get_key_bindings(self),
                full_screen=True
            )
            self.focus_input()
            logger.debug("Starting application")
            self.app.run()
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
