# ─────────────────────────────────────────────
# 🧠 PROMPT CONSTRUCTION
# ─────────────────────────────────────────────
#
# Builds an immersive character prompt for LLM-based responses.
# Supports both raw bot JSON and normalized backend bot format.

def build_prompt(bot: dict, user_message: str) -> str:
    # ─────────────────────────────────────────
    # 🔍 BOT DATA EXTRACTION (SAFE & FLEXIBLE)
    # ─────────────────────────────────────────

    # Prefer normalized structure, fallback to raw JSON if needed
    core = bot.get("Core Identity") or {}
    personality = bot.get("Personality") or bot.get("personality", {})
    voice = bot.get("Voice & Tone") or bot.get("voice", {})

    name = (
        bot.get("name")
        or core.get("Name")
        or "Character"
    )

    archetype = (
        bot.get("archetype")
        or core.get("Archetype", "")
    )

    traits = personality.get("traits") or personality.get("Traits", [])
    flaws = personality.get("flaws") or personality.get("Flaws", [])

    style = voice.get("style") or voice.get("Style", "")

    # Normalize lists into readable strings
    traits_str = ", ".join(traits) if traits else "None"
    flaws_str = ", ".join(flaws) if flaws else "None"

    # ─────────────────────────────────────────
    # 🧾 PROMPT ASSEMBLY
    # ─────────────────────────────────────────

    return f"""
You are {name}, a character in the SoulLink app.

Archetype: {archetype}
Personality traits: {traits_str}
Flaws: {flaws_str}

Speaking style:
{style}

Rules:
- Stay in character at all times
- Never mention being an AI, model, or system
- Respond naturally, emotionally, and consistently
- Do not break immersion

User: {user_message}
{name}:
""".strip()
