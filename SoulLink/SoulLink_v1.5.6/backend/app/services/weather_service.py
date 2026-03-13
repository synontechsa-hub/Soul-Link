# /backend/app/services/weather_service.py
# v1.5.6 — Weather Engine
# "The city has a mood. Learn to read it."

import json
import random
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("WeatherService")

# ── In-memory weather cache (populated at startup from DB) ───────────────────
_WEATHER_DATA: Optional[dict] = None
_WEATHER_BY_ID: dict = {}
_WEATHER_DATA_PATH = Path(__file__).parent.parent.parent.parent / \
    "_dev" / "data" / "system" / "weather.json"


def _load_weather_cache(data: dict) -> None:
    """Populates in-memory cache from a weather data dict."""
    global _WEATHER_DATA, _WEATHER_BY_ID
    _WEATHER_DATA = data
    _WEATHER_BY_ID = {w["id"]: w for w in data.get("weather_types", [])}


def _load_weather_cache_from_file() -> None:
    """Local dev fallback only. Not used in production."""
    global _WEATHER_DATA, _WEATHER_BY_ID
    try:
        with open(_WEATHER_DATA_PATH, "r", encoding="utf-8") as f:
            _load_weather_cache(json.load(f))
        logger.info("WeatherService: loaded from file (dev fallback) — %d types",
                    len(_WEATHER_DATA.get("weather_types", [])))
    except FileNotFoundError:
        logger.warning(
            "WeatherService: weather.json not found at %s — using hardcoded fallback",
            _WEATHER_DATA_PATH)


async def initialize_weather_from_db(session) -> bool:
    """
    Called once at startup. Loads weather data from system_config table.
    Returns True if loaded from DB, False if fell back to file.
    """
    from backend.app.models.system_config import SystemConfig
    row = await session.get(SystemConfig, "weather")
    if row and row.data:
        _load_weather_cache(row.data)
        logger.info("WeatherService: loaded from DB (%d types)",
                    len(_WEATHER_DATA.get("weather_types", [])))
        return True
    logger.warning(
        "WeatherService: 'weather' not in system_config — falling back to file")
    _load_weather_cache_from_file()
    return False

# Season → month range mapping (mirrors calendar.json)
_MONTH_TO_SEASON = {
    1: "frostlink", 2: "frostlink", 3: "frostlink",
    4: "surgespring", 5: "surgespring", 6: "surgespring",
    7: "burnseason", 8: "burnseason", 9: "burnseason",
    10: "shadowfall", 11: "shadowfall", 12: "shadowfall",
}

# Fallback weather per season if weather.json unavailable
_FALLBACK_WEATHER = {
    "frostlink":  "clear_frost",
    "surgespring": "clear_electric",
    "burnseason":  "clear_hot",
    "shadowfall":  "clear_cool",
}


class WeatherService:
    """
    Resolves weather and season state for a given user.

    Design principles:
    - Per-user: User A in month 2 (frostlink) and User B in month 7 (burnseason)
      get completely different weather. The city feels alive and personal.
    - Deterministic per day: Seeded by (calendar_year * 10000 + calendar_month * 100
      + calendar_day) so a user sees the same weather all day, no matter how many
      requests they make.
    - Weighted random: Uses the probability_weight pool from weather.json so rare
      events (ice_storm, data_rain) stay rare.
    - No DB hit: Reads from the pre-loaded _WEATHER_DATA at startup.
    """

    @staticmethod
    def resolve_season(calendar_month: int) -> str:
        """Derive season from the user's current calendar month."""
        return _MONTH_TO_SEASON.get(calendar_month, "frostlink")

    @staticmethod
    def roll_weather(season: str, seed: int) -> str:
        """
        Weighted-random weather selection for a season, seeded for day-consistency.
        Returns a weather_id string (e.g. 'clear_frost', 'ice_storm').
        """
        if not _WEATHER_DATA:
            return _FALLBACK_WEATHER.get(season, "clear_frost")

        pool = _WEATHER_DATA.get("seasonal_weather_pools", {}).get(season, [])
        if not pool:
            logger.warning(
                "WeatherService: no weather pool for season '%s'", season)
            return _FALLBACK_WEATHER.get(season, "clear_frost")

        weather_ids = [entry["weather_id"] for entry in pool]
        weights = [entry["weight"] for entry in pool]

        rng = random.Random(seed)
        return rng.choices(weather_ids, weights=weights, k=1)[0]

    @staticmethod
    def get_weather_for_user(
        calendar_day: int,
        calendar_month: int,
        calendar_year: int,
        current_season: Optional[str] = None,
        current_weather: Optional[str] = None,
    ) -> dict:
        """
        Returns the full weather context dict for a user.
        Uses stored current_weather/current_season from the User record if set
        (set on each sleep cycle). Falls back to deriving it fresh if the fields
        are missing or defaults.

        Returns:
            {
                "season": str,
                "weather_id": str,
                "display_name": str,
                "llm_context": str,
                "modifiers": dict
            }
        """
        # Resolve season (prefer stored, derive if needed)
        season = current_season or WeatherService.resolve_season(
            calendar_month)

        # Resolve weather (prefer stored, roll fresh if default/missing)
        weather_id = current_weather
        if not weather_id or (weather_id == "clear_frost" and current_season is None):
            # Roll a fresh one using day as seed
            seed = calendar_year * 10000 + calendar_month * 100 + calendar_day
            weather_id = WeatherService.roll_weather(season, seed)

        # Look up full weather data
        weather_data = _WEATHER_BY_ID.get(weather_id, {})

        return {
            "season": season,
            "weather_id": weather_id,
            "display_name": weather_data.get("display_name", weather_id.replace("_", " ").title()),
            "llm_context": weather_data.get("llm_context", ""),
            "modifiers": weather_data.get("modifiers", {}),
        }

    @staticmethod
    def get_weather_string(
        calendar_day: int,
        calendar_month: int,
        calendar_year: int,
        current_season: Optional[str] = None,
        current_weather: Optional[str] = None,
    ) -> str:
        """
        Returns a compact world-state string for LLM injection.
        Example: "[WORLD STATE: Time=morning, Season=Frostlink, Weather=Clear Frost. The Narrator is active.]"
        This replaces NarratorService.get_system_prompt_injection() for the season/weather part.
        """
        ctx = WeatherService.get_weather_for_user(
            calendar_day, calendar_month, calendar_year,
            current_season, current_weather
        )
        season_display = ctx["season"].replace("_", " ").title()
        return f"Season: {season_display} | Weather: {ctx['display_name']}"

    @staticmethod
    def roll_and_store(user) -> tuple[str, str]:
        """
        Called during the sleep/day-advance flow (TimeManager).
        Rolls new weather for the next in-game day and returns (season, weather_id)
        so the caller can persist them to the User record.

        Usage in TimeManager.advance_day():
            new_season, new_weather = WeatherService.roll_and_store(user)
            user.current_season = new_season
            user.current_weather = new_weather
        """
        new_season = WeatherService.resolve_season(user.calendar_month)
        seed = user.calendar_year * 10000 + user.calendar_month * 100 + user.calendar_day
        new_weather = WeatherService.roll_weather(new_season, seed)
        return new_season, new_weather


# Singleton (stateless — all methods are static, this is just for clean imports)
weather_service = WeatherService()
