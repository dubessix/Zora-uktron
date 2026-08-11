"""
Ultron Core Confidence Engine
Evaluates user prompts to score execution confidence. Prevents vague/gibberish executions.
"""

class ConfidenceEngine:
    def __init__(self) -> None:
        pass

    def calculate_confidence(self, user_prompt: str, intent: str) -> float:
        """
        Calculates a confidence score between 0.0 and 1.0.
        Scores are influenced by prompt length, structure, and intent clarity.
        """
        clean_prompt = user_prompt.strip()
        length = len(clean_prompt)

        # Edge case: Empty or extremely short inputs
        if length == 0:
            return 0.0
        if length < 3:
            return 0.30

        # Heuristic 1: Deduct score if inputs are just numbers or special symbols (High Priority)
        if clean_prompt.isdigit() or not any(c.isalnum() for c in clean_prompt):
            return 0.20

        base_score = 1.0

        # Heuristic 2: Deduct score for very short conversational phrases
        if intent == "CONVERSATION" and length < 10:
            base_score = 0.95

        # Heuristic 3: Deduct score for vague technical commands (e.g. just typing "webpack")
        elif intent == "DEVELOPER_HELP" and length < 15:
            base_score = 0.55

        # Clamp score between 0.0 and 1.0
        return max(0.0, min(1.0, base_score))
