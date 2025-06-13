# api.py
import requests
import logging
from config import OLLAMA_API

logger = logging.getLogger(__name__)

class ApiClient:
    def send_to_ollama(self, model, messages):
        """Send messages to Ollama API."""
        payload = {"model": model, "messages": messages, "stream": False}
        try:
            response = requests.post(OLLAMA_API, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.RequestException as e:
            logger.error(f"Ollama API error: {str(e)}")
            return f"Error: {e}"
