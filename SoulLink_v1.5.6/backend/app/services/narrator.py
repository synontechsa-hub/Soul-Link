# /backend/app/services/narrator.py
# v1.5.6 Narrative Engine - The Voice of the World

from datetime import datetime, timedelta
import random

class NarratorService:
    """
    Handles 'Fade-to-Black' logic, time jumps, and world continuity.
    In v1.5.6, the Narrator is a distinct System Voice that bridges gaps between sessions.
    """
    
    CHRONICLE_THRESHOLD_HOURS = 4  # Minimum gap to trigger a Chronicle Break
    
    @staticmethod
    def check_time_jump(last_interaction: datetime) -> bool:
        """
        Determines if enough time has passed to warrant a narrator interjection.
        """
        if not last_interaction:
            return False
            
        delta = datetime.utcnow() - last_interaction
        return delta.total_seconds() > (NarratorService.CHRONICLE_THRESHOLD_HOURS * 3600)

    @staticmethod
    def generate_chronicle(last_interaction: datetime, current_location: str, weather: str) -> str:
        """
        Generates the 'Chronicle Break' text based on time passed and world state.
        TODO: Connect this to LLM for dynamic generation. For now, use templates.
        """
        delta = datetime.utcnow() - last_interaction
        hours_passed = int(delta.total_seconds() / 3600)
        
        # Simple Template System (Placeholder for LLM)
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
