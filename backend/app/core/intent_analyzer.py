"""
Ultron Core Intent Analyzer
Parses and classifies user queries into structured behavioral intents.
Runs entirely locally with 0MB RAM footprint.
"""

import re
from typing import Dict, Any

class IntentAnalyzer:
    def __init__(self) -> None:
        # Predefined regex patterns for high-speed, local intent matching
        self._patterns = {
            "PLANNING": re.compile(r"\b(plan|schedule|todo|task|calendar|sprint|reminder)\b", re.IGNORECASE),
            "DEVELOPER_HELP": re.compile(r"\b(debug|error|compile|build|npm|pip|git|git status|webpack|vite|cors|middleware|bug|traceback|line)\b", re.IGNORECASE),
            "EMOTIONAL": re.compile(r"\b(sad|stressed|overwhelmed|tired|stupid|impossible|give up|hate|upset|angry|sigh)\b", re.IGNORECASE),
            "RESEARCH": re.compile(r"\b(research|compare|difference between|versus|vs|how does|why is)\b", re.IGNORECASE),
            "CONVERSATION": re.compile(r"\b(hi|hello|hey|good morning|how are you|good night|thanks|thank you|welcome)\b", re.IGNORECASE),
        }

    def analyze(self, user_prompt: str) -> str:
        """
        Analyzes the prompt and returns a standardized intent category string.
        Defaults to 'EXPLANATION' if no specific category matches.
        """
        prompt_clean = user_prompt.strip()
        if not prompt_clean:
            return "CONVERSATION"

        # Check regex matches in priority order
        for intent, pattern in self._patterns.items():
            if pattern.search(prompt_clean):
                return intent
                
        return "EXPLANATION"
