# keybindings.py
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application.current import get_app
from config import OUTPUT_FILE
import logging
import time

logger = logging.getLogger(__name__)

class KeyBindingManager:
    def __init__(self):
        self.start_time = time.time()

    def get_key_bindings(self, ui):
        """Define keybindings for the UI."""
        bindings = KeyBindings()

        @bindings.add('c-q')
        def _(event):
            logger.debug("Keypress: Ctrl+q")
            event.app.exit()

        @bindings.add('c-j')
        def _(event):
            logger.debug("Keypress: Ctrl+j")
            if ui.session_manager.current_session_idx < len(ui.session_manager.session_names) - 1:
                ui.session_manager.current_session_idx += 1
                ui.update_session_display()

        @bindings.add('c-k')
        def _(event):
            logger.debug("Keypress: Ctrl+k")
            if ui.session_manager.current_session_idx > 0:
                ui.session_manager.current_session_idx -= 1
                ui.update_session_display()

        @bindings.add('enter')
        def _(event):
            logger.debug("Keypress: Enter")
            if get_app().layout.has_focus(ui.session_window):
                ui.focus_input()
            elif ui.input_buffer.text.strip().startswith("Enter new session name:"):
                new_name = ui.input_buffer.text.replace("Enter new session name:", "").strip()
                if ui.session_manager.rename_session(new_name):
                    ui.update_session_display()
                ui.input_buffer.text = ""
            else:
                message = ui.input_buffer.text.strip()
                if not message:
                    return
                if len(message.encode()) > 1000 or any(ord(c) > 127 for c in message):
                    logger.warning(f"Invalid input detected: {message}")
                    ui.input_buffer.text = "Invalid input, please use ASCII characters"
                    return
                if message == f"Saved history to {OUTPUT_FILE}" or message.startswith("Error saving history:"):
                    logger.debug(f"Ignoring feedback message: {message}")
                    ui.input_buffer.text = ""
                    return
                session_name = ui.session_manager.session_names[ui.session_manager.current_session_idx]
                model = ui.session_manager.sessions[session_name]["model"]
                history = ui.session_manager.sessions[session_name]["history"]
                response = ui.api_client.send_to_ollama(model, history)
                ui.session_manager.add_message(message, response)
                ui.input_buffer.text = ""
                ui.update_chat_display()

        @bindings.add('c-c')
        def _(event):
            logger.debug("Keypress: Ctrl+c")
            if ui.session_manager.create_session():
                ui.update_session_display()

        @bindings.add('c-d')
        def _(event):
            logger.debug("Keypress: Ctrl+d")
            if ui.session_manager.delete_session():
                ui.update_session_display()

        @bindings.add('c-r')
        def _(event):
            logger.debug("Keypress: Ctrl+r")
            if not ui.session_manager.session_names:
                return
            ui.input_buffer.text = "Enter new session name: "
            ui.focus_input()
            if ui.app:
                ui.app.invalidate()

        @bindings.add('c-y')
        def _(event):
            logger.debug("Keypress: Ctrl+y")
            if time.time() - ui.start_time < 1:
                logger.debug("Ignoring Ctrl+y keypress during startup")
                return
            success, feedback = ui.session_manager.save_history_to_file()
            ui.input_buffer.text = feedback
            if ui.app:
                ui.app.invalidate()
            def clear_input():
                if ui.input_buffer.text == feedback:
                    time.sleep(1)
                    ui.input_buffer.text = ""
                    if ui.app:
                        ui.app.invalidate()
            ui.app.create_background_task(clear_input())

        @bindings.add('c-t')
        def _(event):
            logger.debug("Keypress: Ctrl+t")
            if get_app().layout.has_focus(ui.input_window):
                ui.focus_sessions()
            else:
                ui.focus_input()

        return bindings
