# /backend/app/services/narrator.py
# v1.5.6 Narrative Engine - The Voice of the World
# UPDATED: Now uses Groq (llama-3.1-8b-instant) for dynamic Chronicle Breaks.

from datetime import datetime, timezone
import random
import logging
from backend.app.core.config import settings

logger = logging.getLogger("Narrator")

class NarratorService:
    """
    Handles 'Fade-to-Black' logic, time jumps, and world continuity.
    In v1.5.6, the Narrator is a distinct System Voice that bridges gaps between sessions.
    """
    
    CHRONICLE_THRESHOLD_HOURS = 4  # Minimum gap to trigger a Chronicle Break
    
    @property
    def client(self):
        """Lazy-loaded Groq client."""
        if not hasattr(self, "_client") or self._client is None:
            from groq import Groq
            self._client = Groq(api_key=settings.groq_api_key)
        return self._client
    
    @staticmethod
    def check_time_jump(last_interaction: datetime) -> bool:
        """
        Determines if enough time has passed to warrant a narrator interjection.
        """
        if not last_interaction:
            return False
            
        # Normandy-SR2 Fix: Ensure conscious comparison between naive datetimes
        if last_interaction.tzinfo is not None:
            last_interaction = last_interaction.replace(tzinfo=None)
            
        delta = datetime.utcnow() - last_interaction
        return delta.total_seconds() > (NarratorService.CHRONICLE_THRESHOLD_HOURS * 3600)

    @staticmethod
    async def generate_chronicle(last_interaction: datetime, current_location: str, weather: str) -> str:
        """
        Generates the 'Chronicle Break' text based on time passed and world state.
        Uses Groq (llama-3.1-8b-instant) for snappy, immersive narration.
        """
        # Normandy-SR2 Fix: Consistency in time comparison
        if last_interaction.tzinfo is not None:
            last_interaction = last_interaction.replace(tzinfo=None)
        delta = datetime.utcnow() - last_interaction
        hours_passed = int(delta.total_seconds() / 3600)
        
        prompt = (
            f"You are the Narrator of SoulLink. Write a short 'Fade-to-Black' event summary.\n"
            f"Context: {hours_passed} hours have passed since the user last interacted.\n"
            f"Current Location: {current_location}\n"
            f"Current Weather: {weather}\n\n"
            f"Requirement: Write exactly ONE cinematic sentence (max 80 tokens). "
            f"Focus on the passage of time and the atmosphere. Do not use character names."
        )

        try:
            # Normandy-SR2 Fix: Use self.client (lazy) instead of global
            # Note: Since this is currently a staticmethod, we need to instantiate or change access.
            # Refactoring to instance method for cleaner lazy access.
            srv = NarratorService()
            chat_completion = srv.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=80
            )
            chronicle_text = chat_completion.choices[0].message.content.strip()
            # Clean up quotes if the LLM adds them
            if chronicle_text.startswith('"') and chronicle_text.endswith('"'):
                chronicle_text = chronicle_text[1:-1]
            return chronicle_text

        except Exception as e:
            logger.error(f"Narrator LLM Failure: {e}")
            
            # Fallback Template System
            templates = [
                f"It has been {hours_passed} hours. The city hums with {weather} energy.",
                f"Time skips forward ({hours_passed}h). You are now at {current_location}.",
                f"The scene fades. {hours_passed} hours later, the lights of {current_location} flicker back to life."
            ]
            return random.choice(templates)

    @staticmethod
    def get_system_prompt_injection(weather: str, time_of_day: str) -> str:
        """
        Injects the current world state into the System Prompt.
        """
        return f"[WORLD STATE: Time={time_of_day}, Weather={weather}. The Narrator is active.]"
