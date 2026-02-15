# /backend/app/models/time_slot.py
# /version.py v1.5.4 Arise
# /_dev/

# "Time is an illusion. Lunchtime doubly so."
# - Douglas Adams, The Hitchhiker's Guide to the Galaxy

from enum import Enum
from typing import Final

class TimeSlot(str, Enum):
    """
    The Five Time Slots of Link City
    Each slot represents a distinct phase of the day with unique soul routines.
    """
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    HOME_TIME = "home_time"

# Time slot progression order
TIME_SLOT_ORDER: Final[list[TimeSlot]] = [
    TimeSlot.MORNING,
    TimeSlot.AFTERNOON,
    TimeSlot.EVENING,
    TimeSlot.NIGHT,
    TimeSlot.HOME_TIME,
]

def get_next_time_slot(current: TimeSlot) -> TimeSlot:
    """
    Get the next time slot in the progression cycle.
    HOME_TIME wraps back to MORNING.
    """
    try:
        current_index = TIME_SLOT_ORDER.index(current)
        next_index = (current_index + 1) % len(TIME_SLOT_ORDER)
        return TIME_SLOT_ORDER[next_index]
    except ValueError:
        # Fallback to morning if invalid slot
        return TimeSlot.MORNING

def get_time_slot_display_name(slot: TimeSlot) -> str:
    """Get human-readable display name for time slot."""
    display_names = {
        TimeSlot.MORNING: "Morning",
        TimeSlot.AFTERNOON: "Afternoon",
        TimeSlot.EVENING: "Evening",
        TimeSlot.NIGHT: "Night",
        TimeSlot.HOME_TIME: "Home Time",
    }
    return display_names.get(slot, "Unknown")

def get_time_slot_description(slot: TimeSlot) -> str:
    """Get atmospheric description for each time slot."""
    descriptions = {
        TimeSlot.MORNING: "The city awakens. Fresh synth-coffee and new beginnings.",
        TimeSlot.AFTERNOON: "Link City pulses with activity. The streets are alive.",
        TimeSlot.EVENING: "Neon lights flicker on. The night shift begins.",
        TimeSlot.NIGHT: "The city never sleeps. Shadows dance in alleyways.",
        TimeSlot.HOME_TIME: "The quiet hours. Most souls retreat to their sanctuaries.",
    }
    return descriptions.get(slot, "Time flows through Link City.")
