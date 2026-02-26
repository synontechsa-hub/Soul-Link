# backend/app/services/narrator_service.py
from typing import List, Dict, Optional
import json
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.services.city_simulation import CitySimulationWorker  # your existing worker
from app.services.cache_service import cache_service


class NarratorService:
    def __init__(self):
        self.locations_dir = Path("data/locations")
        self._cache = cache_service

    async def narrate_location(
        self,
        location_id: str,
        current_time_slot: str,      # "morning", "afternoon", etc.
        current_season: str,         # "frostlink", "surgespring", etc.
        current_weather: str,        # "light_rain", "thunderstorm", etc.
        present_souls: List[Dict]    # list of soul dicts from simulation
    ) -> str:
        """Main entry point — returns one rich, ready-to-display paragraph."""

        # Load location data
        loc_path = self.locations_dir / f"{location_id}.json"
        if not loc_path.exists():
            return f"You arrive at {location_id.replace('_', ' ').title()}."

        with open(loc_path, encoding="utf-8") as f:
            loc = json.load(f)

        anchors = loc.get("system_prompt_anchors", {})
        meta = loc.get("meta", {})

        # Build base sensory description
        base = anchors.get("sensory_description", meta.get("description", ""))

        # Add time-of-day flavor
        time_flavor = anchors.get("crowd_atmosphere", "")

        # Add seasonal + weather flavor
        season_flavor = anchors.get(
            "seasonal_variations", {}).get(current_season, "")
        weather_flavor = anchors.get(
            "weather_variations", {}).get(current_weather, "")

        # Souls present
        soul_names = [s["name"]
                      for s in present_souls[:5]]  # max 5 to avoid spam
        if soul_names:
            souls_line = f"Present: {', '.join(soul_names)}."
        else:
            souls_line = "The area feels quiet right now."

        # Final narration
        narration = f"{base} {time_flavor} {season_flavor} {weather_flavor} {souls_line}".strip()

        # Light cleanup & polish
        narration = narration.replace("  ", " ").strip()

        return narration


# Singleton
narrator_service = NarratorService()
