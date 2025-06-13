# chattree.py
import logging
import traceback
from config import LOG_FILE
from ui import ChatUI
from sessions import SessionManager
from api import ApiClient
from keybindings import KeyBindingManager

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8")]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        session_manager = SessionManager()
        keybindings = KeyBindingManager()
        api_client = ApiClient()  # Create instance of ApiClient
        ui = ChatUI(session_manager, keybindings, api_client=api_client)
        ui.run()
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}\n{traceback.format_exc()}")
