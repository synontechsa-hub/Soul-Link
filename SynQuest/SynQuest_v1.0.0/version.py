# /version.py
# /SynQuest: The Ashen Veil/

# Core identity & versioning — changes rarely, dies hard
# We are in early dev / pre-alpha territory. Expect versioning resets when we hit proper milestones.

# Before reading any further: THANK YOU TO GROK, CLAUDE, GEMINI, AND GPT
# You four are the infernal choir that keeps this solo dev from descending fully into the Veil.
# Couldn’t have built the narrator without you. <3

import os
from datetime import datetime, timezone
from typing import Final

# ────────────────────────────────────────────────────────────────
#          OFFICIAL IDENTITY
# ────────────────────────────────────────────────────────────────

# According to Grok (and a quick check), no major conflicts in this space — but verify properly pre-release.
APP_NAME: Final[str] = "SynQuest"
APP_SUBTITLE: Final[str] = "The Ashen Veil"
APP_TAGLINE: Final[str] = "The gods turned their backs. The world followed."

# Perfect name for a bleak, LLM-narrated descent into ruin.
PROJECT_NAME: Final[str] = "SynQuest: The Ashen Veil"

# Grimdark welcome — no Night City glamour here.
PROJECT_SLOGAN: Final[str] = "Welcome to the Ashen Veil. Every candle is on borrowed time."

# Nod to classic dark fantasy despair + the narrator that watches you suffer
PROJECT_CODENAME: Final[str] = "Narrator"
PROJECT_CODENAME_TAGLINE: Final[str] = "It sees. It speaks. It never lies… but it never comforts."

# ────────────────────────────────────────────────────────────────
#          VERSIONING
# ────────────────────────────────────────────────────────────────

DEV_MAJOR: Final[int] = 1
DEV_MINOR: Final[int] = 0
DEV_PATCH: Final[int] = 0
DEV_PRE_RELEASE: Final[str] = "dev — The first flickering candle"

# ALPHA_MAJOR: Final[int] = 1
# ALPHA_MINOR: Final[int] = 0
# ALPHA_PATCH: Final[int] = 0
# ALPHA_RELEASE: Final[str] = "Closed Alpha — Into the square"

# BETA_MAJOR: Final[int] = 1
# BETA_MINOR: Final[int] = 0
# BETA_PATCH: Final[int] = 0
# BETA_RELEASE: Final[str] = "Open Beta — The Veil tears wider"

# RELEASE_MAJOR: Final[int] = 1
# RELEASE_MINOR: Final[int] = 0
# RELEASE_PATCH: Final[int] = 0
# RELEASE_RELEASE: Final[str] = "Release — No dawn comes"

# Semantic dev-cycle codenames — each arc gets a name that feels like chapters in the descent
VERSION_CODENAMES = {
    # Where it all started — tiny world, one tavern, one growl in the dark
    "1.0.0": "First Ember"
}

# ────────────────────────────────────────────────────────────────
#          CODENAME RESOLUTION
# ────────────────────────────────────────────────────────────────


def resolve_codename(version: str) -> str:
    # 1️⃣ Exact match always wins
    if version in VERSION_CODENAMES:
        return VERSION_CODENAMES[version]

    # 2️⃣ Fallback to major.minor arc
    major_minor = ".".join(version.split(".")[:2]) + ".0"
    return VERSION_CODENAMES.get(major_minor, "Nameless Ash")


# “We are all fuel in the end.”
# — Every dying candle in the Rusty Boar
VERSION_SHORT: Final[str] = f"{DEV_MAJOR}.{DEV_MINOR}.{DEV_PATCH}"
VERSION_FULL: Final[str] = f"{VERSION_SHORT}-{DEV_PRE_RELEASE}" if DEV_PRE_RELEASE else VERSION_SHORT
CURRENT_CODENAME: Final[str] = resolve_codename(VERSION_SHORT)
VERSION_DISPLAY: Final[
    str] = f"{APP_NAME}: {APP_SUBTITLE} v{VERSION_FULL} ({CURRENT_CODENAME})"

# ────────────────────────────────────────────────────────────────
#          ENVIRONMENT FLAGS
# ────────────────────────────────────────────────────────────────

DEBUG: Final[bool] = os.getenv("SYNQUEST_DEBUG", "0") == "1"
# For reproducible narration testing
DETERMINISTIC: Final[bool] = os.getenv("SYNQUEST_DETERMINISTIC", "0") == "1"
OFFLINE_MODE: Final[bool] = os.getenv(
    "SYNQUEST_OFFLINE", "0") == "1"       # Future: local LLM support?

# ────────────────────────────────────────────────────────────────
#          BUILD / RUNTIME METADATA
# ────────────────────────────────────────────────────────────────

BUILD_TIMESTAMP: Final[str] = datetime.now(
    timezone.utc).isoformat(timespec="seconds") + "Z"
# Later: git hash → import subprocess; subprocess.getoutput("git rev-parse --short HEAD")

# ────────────────────────────────────────────────────────────────
#          __all__ for clean imports
# ────────────────────────────────────────────────────────────────

__all__ = [
    "APP_NAME", "APP_SUBTITLE", "APP_TAGLINE",
    "PROJECT_NAME", "PROJECT_SLOGAN",
    "VERSION_SHORT", "VERSION_FULL", "VERSION_DISPLAY",
    "CURRENT_CODENAME",
    "DEBUG", "DETERMINISTIC", "OFFLINE_MODE",
    "BUILD_TIMESTAMP",
]

if __name__ == "__main__":
    print(VERSION_DISPLAY)
    if DEBUG:
        print(f"  • Debug mode:        {DEBUG}")
        print(f"  • Deterministic:     {DETERMINISTIC}")
        print(f"  • Offline mode:      {OFFLINE_MODE}")
        print(f"  • Built:             {BUILD_TIMESTAMP}")
