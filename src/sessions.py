# sessions.py
import json
import os
import logging
import time
from config import SESSION_FILE, DEFAULT_SESSIONS, OUTPUT_FILE

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.sessions = self.load_sessions()
        self.session_names = list(self.sessions.keys())
        self.current_session_idx = 0
        self._last_saved = 0

    def load_sessions(self):
        """Load sessions from JSON file."""
        if not os.path.exists(SESSION_FILE):
            logger.info(f"{SESSION_FILE} not found, using default sessions.")
            return DEFAULT_SESSIONS
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"{SESSION_FILE} is empty, using default sessions.")
                    return DEFAULT_SESSIONS
                sessions = json.loads(content)
                for name, data in sessions.items():
                    if not isinstance(data, dict) or "model" not in data or "history" not in data:
                        logger.error(f"Invalid session data for {name}")
                        return DEFAULT_SESSIONS
                return sessions
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {SESSION_FILE}: {str(e)}")
            return DEFAULT_SESSIONS
        except Exception as e:
            logger.error(f"Error reading {SESSION_FILE}: {str(e)}")
            return DEFAULT_SESSIONS

    def save_sessions(self, force=False):
        """Save sessions to JSON file, debounced."""
        current_time = time.time()
        if not force and current_time - self._last_saved < 5:
            return
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2)
            self._last_saved = current_time
        except Exception as e:
            logger.error(f"Error saving {SESSION_FILE}: {str(e)}")

    def save_history_to_file(self):
        """Save current session's history to file."""
        if not self.session_names:
            logger.debug("No sessions available to save history")
            return False, "No sessions available"
        session_name = self.session_names[self.current_session_idx]
        history = self.sessions[session_name]["history"]
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for msg in history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    f.write(f"{role}: {msg['content']}\n")
            return True, f"Saved history to {OUTPUT_FILE}"
        except Exception as e:
            logger.error(f"Error saving {OUTPUT_FILE}: {str(e)}")
            return False, f"Error saving history: {str(e)}"

    def create_session(self):
        """Create a new session."""
        try:
            new_session = f"Session {len(self.sessions) + 1}"
            self.sessions[new_session] = {"model": "llama3", "history": []}
            self.session_names.append(new_session)
            self.save_sessions()
            return True
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return False

    def delete_session(self):
        """Delete the current session."""
        try:
            if len(self.session_names) <= 1:
                return False
            session_name = self.session_names.pop(self.current_session_idx)
            del self.sessions[session_name]
            if self.current_session_idx >= len(self.session_names):
                self.current_session_idx = len(self.session_names) - 1
            self.save_sessions()
            return True
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return False

    def rename_session(self, new_name):
        """Rename the current session."""
        try:
            if not self.session_names or not new_name or new_name in self.session_names:
                return False
            old_name = self.session_names[self.current_session_idx]
            self.sessions[new_name] = self.sessions.pop(old_name)
            self.session_names[self.current_session_idx] = new_name
            self.save_sessions()
            return True
        except Exception as e:
            logger.error(f"Error renaming session: {str(e)}")
            return False

    def add_message(self, message, response):
        """Add user message and assistant response to current session."""
        try:
            session_name = self.session_names[self.current_session_idx]
            self.sessions[session_name]["history"].append({"role": "user", "content": message})
            self.sessions[session_name]["history"].append({"role": "assistant", "content": response})
            self.save_sessions()
            return True
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return False
