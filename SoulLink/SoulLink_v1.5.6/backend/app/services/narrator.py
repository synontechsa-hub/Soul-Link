# /backend/app/services/narrator.py
# v1.5.6 Narrative Engine - The Voice of the World
# UPDATED: Now uses Groq (llama-3.1-8b-instant) for dynamic Chronicle Breaks.

from datetime import datetime, timezone
from backend.app.core.utils import utcnow
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
    def check_time_jump(last_seen_at: datetime) -> bool:
        """Check if enough time has passed to trigger a Chronicle Break."""
        if not last_seen_at:
            return False
        delta = utcnow() - last_seen_at
        return (delta.total_seconds() / 3600) >= NarratorService.CHRONICLE_THRESHOLD_HOURS

    async def generate_chronicle(
        self,
        last_seen_at: datetime,
        current_location: str,
        weather: str
    ) -> str:
        """Generates a cinematic one-liner about the passage of time."""
        delta = utcnow() - last_seen_at
        hours_passed = round(delta.total_seconds() / 3600, 1)

        prompt = (
            f"Context: It has been {hours_passed} hours since the user last interacted. "
            f"Location: {current_location}. "
            f"Current Weather: {weather}\n\n"
            f"Requirement: Write exactly ONE cinematic sentence (max 80 tokens). "
            f"Focus on the passage of time and the atmosphere. Do not use character names."
        )

        try:
            import asyncio
            loop = asyncio.get_running_loop()

            def _call_narrator_groq():
                return self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                    max_tokens=80
                )

            chat_completion = await loop.run_in_executor(None, _call_narrator_groq)
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

    @staticmethod
    async def narrate_location(
        session,
        location_id: str,
        current_time_slot: str,
        present_souls_data: list,
        user=None
    ) -> dict:
        """
        Fast, database-driven location narration returning structured data for Flutter widgets.
        No LLM generation involved.
        Uses WeatherService to resolve real per-user season and weather.
        """
        from backend.app.models.location import Location
        from backend.app.services.weather_service import WeatherService

        loc = await session.get(Location, location_id)

        # Resolve per-user weather context (falls back to defaults if user is None)
        if user:
            weather_ctx = WeatherService.get_weather_for_user(
                calendar_day=user.calendar_day,
                calendar_month=user.calendar_month,
                calendar_year=user.calendar_year,
                current_season=user.current_season,
                current_weather=user.current_weather,
            )
        else:
            weather_ctx = WeatherService.get_weather_for_user(
                calendar_day=1, calendar_month=1, calendar_year=1
            )

        current_season = weather_ctx["season"]
        current_weather = weather_ctx["weather_id"]

        if not loc:
            base_desc = f"You arrive at {location_id.replace('_', ' ').title()}."
            music = "ambient_city_loop.mp3"
        else:
            anchors = loc.system_prompt_anchors or {}
            base_desc = anchors.get(
                "sensory_description", loc.description or "A quiet place in the city.")
            music = loc.music_track

            # Optionally add time flavor from DB if it exists
            time_flavor = anchors.get("crowd_atmosphere", "")
            base_desc = f"{base_desc} {time_flavor}".strip()

        return {
            "location_id": location_id,
            "base_description": base_desc,
            "music_track": music,
            "environmental_factors": {
                "time_slot": current_time_slot,
                "season": current_season,
                "weather": current_weather,
                "weather_display": weather_ctx["display_name"],
                "weather_llm_context": weather_ctx["llm_context"],
            },
            "present_souls": present_souls_data
        }


# Singleton instance
narrator_service = NarratorService()
