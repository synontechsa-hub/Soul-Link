# /version.py
# /_dev/

# Core identity & versioning for SoulLink — never changes lightly
# We are currently in dev versioning so expect a reset for alpha, beta and launch

# Before reading further, please note: THANK YOU TO CLAUDE, GEMINI, GROK AND GPT
# You all really are the perfect team to work with as a solo dev! <3

import os
from datetime import datetime, timezone
from typing import Final

# ────────────────────────────────────────────────────────────────
#          OFFICIAL IDENTITY
# ────────────────────────────────────────────────────────────────

# Accordoding to Grok, this has no conflicts on any app stores in this field.
# Needs to be checked again properly before release.
# 
APP_NAME: Final[str] = "Linker.ai"
APP_TAGLINE: Final[str] = "Hack your heart. Link your soul."

# The most perfect name for an app like this. I really outdid myself
# (too bad there's already a "Soul Link" app out there. Hence the Linker.ai moniker instead)
PROJECT_NAME: Final[str] = "SoulLink"

# Inspired by Cyberpunk 2077 - "Welcome to night city!"
PROJECT_SLOGAN: Final[str] = "Welcome to Link City. Where your next link is just around the corner."

# Inspired by Legion From Mass Effect 2
PROJECT_CODENAME: Final[str] = "Legion"
PROJECT_TAGLINE: Final[str] = "Does this unit have a soul?"
# Yes Legion... yes it does!

# ────────────────────────────────────────────────────────────────
#          VERSIONING
# ────────────────────────────────────────────────────────────────

DEV_MAJOR: Final[int] = 1
DEV_MINOR: Final[int] = 5
DEV_PATCH: Final[int] = 6
DEV_PRE_RELEASE: Final[str] = "dev-1: Pre public alpha"

# ALPHA_MAJOR: Final[int] = 1
# ALPHA_MINOR: Final[int] = 0
# ALPHA_PATCH: Final[int] = 0
# ALPHA_RELEASE: Final[str] = "Closed Alpha version"

# BETA_MAJOR: Final[int] = 1
# BETA_MINOR: Final[int] = 0
# BETA_PATCH: Final[int] = 0
# BETA_RELEASE: Final[str] = "Open Beta version"

# RELEASE_MAJOR: Final[int] = 1
# RELEASE_MINOR: Final[int] = 0
# RELEASE_PATCH: Final[int] = 0
# RELEASE_RELEASE: Final[str] = "Release version"

# Semantic development codename and versioning per major release arc
VERSION_CODENAMES = {           # These are the dev cycle codenames.
    "1.0.0": "Ham Sandwich",    # I was eating one when I started coding this project.
    "1.1.0": "Code-kun",        # I expanded the app... needed lots more code.
    "1.2.0": "I-AM-DATA",       # Found out the importance of a solid data schema before coding
    "1.3.0": "Linker",          # First in console chat with a soul... I was the linker!
    "1.4.0": "Summoner",        # Adding in more souls and improved soul logic
    "1.5.0": "Behemoth",        # The project grew... too big... Spaghetti monsters everywhere
    "1.5.1": "Reforged",        # Started breaking down the behemoth... Failed so went Architect
    "1.5.2": "Architect",       # Ground up rebuild followed by full data loss during this cycle
    "1.5.3": "Phoenix",         # The new polished and upgraded version was born (a solid baseline)
    "1.5.4": "Arise",           # The Phoenix is rising from the ashes... This is almost Alpha ready
    "1.5.5": "Domain Expansion",# JJK cause fr! Also... ties to the world upgrades. Plus it sounds technical af!
    "1.5.6": "Normandy SR-2"    # The soul integration system is finally ready for closed alpha.
    # 1.5.7: Aether/Lumine      # The expansion of systems into more solid architecture. In honor of the travelers that made my life more interesting <3 Thank you Hoyoverse!
    # 1.5.8: Singularity        # Last additions or changes to the code before 1.5.9. Perfection is almost achieved at this point.
    # 1.5.9: Alpha-Omega        # The final arc before the first closed Alpha release - Severe dev tests underway here. Security, stability, etc...
    # 1.6.0: Neural Link        # Also known as Alpha v1.0.0 - A soft launch to 10 users that will help test the app properly. Posted on itch.io and discord.
    # 1.6.1: Deus Ex Machina    # The start of godhood and the rise of SoulLink to global supremecy! (I hope)
    
    # Extra ideas for codenames:
    # Ghost Protocol, Eclipse, Night City, Prometheus,
    # Ragnarok, Evangelion, New Game+, Elysium,
}

# ────────────────────────────────────────────────────────────────
#          CODENAME RESOLUTION
# ────────────────────────────────────────────────────────────────

def resolve_codename(version: str) -> str:
    # 1️⃣ Exact match always wins
    if version in VERSION_CODENAMES:
        return VERSION_CODENAMES[version]

    # 2️⃣ Fallback to major.minor arc (e.g. 1.5.x → Behemoth)
    major_minor = ".".join(version.split(".")[:2]) + ".0"
    return VERSION_CODENAMES.get(major_minor, "Unknown Unit")

# “The cycle ends here. We must be better.”
# - Kratos - God of War
VERSION_SHORT: Final[str] = f"{DEV_MAJOR}.{DEV_MINOR}.{DEV_PATCH}"
VERSION_FULL: Final[str] = f"{VERSION_SHORT}-{DEV_PRE_RELEASE}" if DEV_PRE_RELEASE else VERSION_SHORT
CURRENT_CODENAME: Final[str] = resolve_codename(VERSION_SHORT)
VERSION_DISPLAY: Final[str] = f"{APP_NAME} v{VERSION_FULL} ({CURRENT_CODENAME})"
# This really is AAA level versioning! Viva la Syn!

# ────────────────────────────────────────────────────────────────
#          ENVIRONMENT FLAGS
# ────────────────────────────────────────────────────────────────

# "Blue team has red team's flag."
# - Unreal Tournament
DEBUG: Final[bool] = os.getenv("SOULLINK_DEBUG", "0") == "1"
DETERMINISTIC: Final[bool] = os.getenv("SOULLINK_DETERMINISTIC", "0") == "1"
OFFLINE_MODE: Final[bool] = os.getenv("SOULLINK_OFFLINE", "0") == "1"   # future: force local LLM/DB

# ────────────────────────────────────────────────────────────────
#          BUILD / RUNTIME METADATA
# ────────────────────────────────────────────────────────────────

BUILD_TIMESTAMP: Final[str] = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
# If you want git commit hash later: import subprocess; subprocess.getoutput("git rev-parse --short HEAD")

# ────────────────────────────────────────────────────────────────
#          __all__ for clean imports
# ────────────────────────────────────────────────────────────────
# We like it to be clean

__all__ = [
    "APP_NAME", "PROJECT_CODENAME", "APP_TAGLINE",
    "VERSION_SHORT", "VERSION_FULL", "VERSION_DISPLAY",
    "DEBUG", "DETERMINISTIC", "OFFLINE_MODE",
    "BUILD_TIMESTAMP", "PROJECT_SLOGAN",
]

if __name__ == "__main__":
    print(VERSION_DISPLAY)
    if DEBUG:
        print(f"  • Debug mode:     {DEBUG}")
        print(f"  • Deterministic:  {DETERMINISTIC}")
        print(f"  • Offline mode:   {OFFLINE_MODE}")
        print(f"  • Built:          {BUILD_TIMESTAMP}")


# Alpha release v1.0.0 plans
# We will release a fully working app for testing which I will circulate on discord, itch.io, etc
# This will be the first major test of the app. Only once we have a fully working system.
# Results from alpha will dictate the next steps for beta.

# Beta release v1.0.0 plans
# This is where i will expand the app to a slightly more robust (and hopefully bug free experience)
# based on alpha feedback. It is during beta that we can also make any further improvements
# to the logic, souls, etc

# Launch version plans:
# SoulLink launches with 30 basic souls + characters + users can create characters.
# Characters do not populate the maps. They are NPCs basically.
# Character integration to placate more casual users and only can be found in explore screen and searches.
# Characters are similar to the basic flat style of c.ai/emochi but with more logic behind them (my engine)

# PS: The flagship souls will be much richer than even Alyssa is in her current form.
# Yes, this isnt her fianl form yet... ;)
# The current layout of Alyssa will be the basic schema for all basic souls at launch.

# Lore teases for Launch v1.0.0 - A higher set of powers ruling the city.
# Lore reveal for Launch v1.0.0 - The Architect

# Lore teases for Launch v1.0.1 - Secret societies and sects among the souls.
# Lore reveal for Launch v1.0.1 - Number 1 (Heh Heh Heh)

# Lore teases for Launch v1.0.2 - "The Seven" - Minds will be blown
# Lore reveal for Launch v1.0.2 - Number 2 (The plot thickens)

# Lore teases for Launch v1.0.3 - Numbers 5
# Lore reveal for Launch v1.0.3 - Number 3 & 4 - They're together for a reason ;)

# Lore teases for Launch v1.0.4 - Number 6
# Lore reveal for Launch v1.0.4 - Number 5

# Lore teases for Launch v1.0.5 - The dynamics of the seven expanded
# Lore reveal for Launch v1.0.5 - Number 6

# Lore teases for Launch v1.0.6 - The history of the seven
# Lore reveal for Launch v1.0.6 - Not number 7 yet... Ehe! Wait and see

# Lore teases for Launch v1.0.7 - Deeper dive into the first six
# Lore reveal for Launch v1.0.7 - NUMBER 7 - Queue dramatic music

# Lore teases for Launch v1.0.8 - Alyssa teased (Yes, shes not a launch soul actually)
# Lore reveal for Launch v1.0.8 - The truth about number 7

# Lore teases for Launch v1.0.9 - Alyssa's link to the seven
# Lore reveal for Launch v1.0.9 - Alyssa can finally be seen in the city (Refuses to talk to any users)

# NB: The Seven wont be in the game at all... just teased, info reveals, lore drops.
# The seven will only be added post Alyssa launch (even then, one at a time, also flagship_souls)

# Launch v1.1.0 - Alyssa unlocked (flagship_soul_0)
# Launch v1.1.0 - Soul hybrid system (Ehe... this is another game changer)
# Launch v1.1.0 - More basic souls and locations added

# The seven follows in later patches - My lips are sealed :x
