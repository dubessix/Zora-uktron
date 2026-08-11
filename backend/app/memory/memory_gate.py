"""
Ultron Core Memory Gate
Analyzes prompt complexity and skips semantic vector indexing for low-density requests (Greetings/Thanks).
Loads list triggers dynamically from config.yaml.
"""

import re
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.yaml"

class MemoryGate:
    def __init__(self) -> None:
        self._greetings = self._load_regex_from_config()

    def _load_regex_from_config(self) -> re.Pattern:
        """Loads greeting list dynamically from config.yaml and compiles standard pattern."""
        default_words = ["hi", "hello", "hey", "thanks", "thank you", "welcome", "test"]
        
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    default_words = config.get("memory", {}).get("low_density_keywords", default_words)
            except Exception:
                pass

        # Escape keywords to build secure regex
        escaped_words = [re.escape(word) for word in default_words]
        pattern_str = r"^\b(" + "|".join(escaped_words) + r")\b[!?.]*$"
        return re.compile(pattern_str, re.IGNORECASE)

    def is_semantically_dense(self, user_prompt: str) -> bool:
        """
        Analyzes prompt contents. Returns False if query is a simple greeting/phrase,
        bypassing costly Cloud Embedding API execution.
        """
        clean = user_prompt.strip()
        if not clean:
            return False
            
        # If matches simple greeting pattern and has less than 4 words, mark as low density
        word_count = len(clean.split())
        if self._greetings.search(clean) and word_count < 4:
            return False
            
        return True
