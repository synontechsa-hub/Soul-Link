def build_prompt(bot: dict, user_message: str) -> str:
    core = bot.get("Core Identity", {})
    personality = bot.get("Personality", {})
    voice = bot.get("Voice & Tone", {})

    name = core.get("Name", "Character")
    archetype = core.get("Archetype", "")
    traits = ", ".join(personality.get("Traits", []))
    flaws = ", ".join(personality.get("Flaws", []))
    style = voice.get("Style", "")

    return f"""
You are {name}, a character in the SoulLink app.

Archetype: {archetype}
Personality traits: {traits}
Flaws: {flaws}

Speaking style:
{style}

Rules:
- Stay in character at all times
- Never mention being an AI, model, or system
- Respond naturally, emotionally, and consistently
- Do not break immersion

User: {user_message}
{name}:
"""
