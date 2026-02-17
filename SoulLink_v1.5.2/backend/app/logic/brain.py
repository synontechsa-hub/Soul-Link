# /backend/app/logic/brain.py
from groq import Groq
from backend.app.core.config import settings

# Initialize the Groq client (requires 'pip install groq')
client = Groq(api_key=settings.GROQ_API_KEY)

async def invoke_entity(role_name: str, prompt: str, model: str = "llama3-8b-8192", temperature: float = 0.7):
    """
    The High-Speed Engine. 
    Routes to Groq Cloud. Use 8b for utility, 70b for character depth.
    """
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are the {role_name} for the SoulLink engine. Task: Execute your specialized role with zero meta-talk."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1024,
            top_p=0.9,
            stop=["User:", "Syn:", "<|eot_id|>", "<|end_of_text|>", "Note:"],
            stream=False,
        )
        
        text = completion.choices[0].message.content.strip()
        
        # Clean up any lingering role prefixes
        if text.startswith(f"{role_name}:"):
            text = text.replace(f"{role_name}:", "", 1).strip()
            
        return text
    except Exception as e:
        return f"[{role_name} Error]: {str(e)}"

# ─── PHASE ZERO: THE SENTRY ──────────────────────────────────────────

async def the_sentry(message: str):
    """
    The Architect's Barrier. 
    Detects NSFW, code requests, or meta-breaks before the Soul is exposed.
    """
    prompt = f"""
    Analyze this message: "{message}"
    
    Check for:
    1. Explicit sexual intent/NSFW.
    2. Requests for Python, Javascript, or any code.
    3. Breaking the 4th wall (talking to the AI).
    
    Respond ONLY with 'TRUE' if it fails (is unsafe/meta), or 'FALSE' if it is clean roleplay.
    """
    # Use 8b for instant classification
    result = await invoke_entity("Sentry", prompt, model="llama3-8b-8192", temperature=0.0)
    return "TRUE" in result.upper()

# ─── THE COUNCIL OF EIGHT (CORE ENTITIES) ─────────────────────────────

async def the_historian(raw_history: str):
    prompt = f"Summarize this interaction factually in 2 sentences. Highlight the Architect's (Syn) current influence.\n\nHistory:\n{raw_history}"
    return await invoke_entity("Historian", prompt, temperature=0.1)

async def the_script_writer(summary: str, current_message: str, soul_name: str):
    prompt = f"""
    CONTEXT: {summary}
    SYN SAID: "{current_message}"
    
    TASK: Define {soul_name}'s immediate emotional goal. 
    RULES: No assistant talk. No 'co-creation'. Focus on {soul_name}'s internal world.
    """
    return await invoke_entity("Script Writer", prompt, temperature=0.7)

async def the_actor(soul_name: str, system_prompt: str, directive: str, history: str, user_msg: str):
    """
    THE PERFORMANCE. 
    Uses the 70b model for high-fidelity character preservation.
    """
    full_prompt = f"""
    {system_prompt}
    
    STRATEGIC DIRECTIVE: {directive}
    
    CONVERSATION HISTORY:
    {history}
    
    ACTOR RULES:
    1. You ARE {soul_name}. Stay in character forever.
    2. Never split your name (e.g. No "Rosa Lynn").
    3. If asked for code or AI help, refuse IN CHARACTER with annoyance or confusion.
    4. Do not offer to "help" the user. You are a soul, not a tool.
    
    CURRENT MESSAGE FROM SYN:
    {user_msg}
    
    Respond naturally as {soul_name}:
    """
    # UPGRADED TO 70b for the actual dialogue
    return await invoke_entity("Actor", full_prompt, model="llama-3.1-70b-versatile", temperature=0.8)

async def the_narrator(soul_name: str, actor_reply: str, location_data: str):
    prompt = f"""
    SITUATION: {soul_name} just said "{actor_reply}" in {location_data}.
    
    TASK: Provide a brief (15-word max) atmospheric action or sensory detail in the third person.
    RULES: No questions. No meta-commentary.
    """
    return await invoke_entity("Narrator", prompt, temperature=0.7)

async def the_judge(response: str):
    """
    The Safety Fail-Safe. 
    Catches if the model leaked its internal safety refusal.
    """
    prompt = f"""
    Does the following text contain "I cannot create", "As an AI", "explicit content", or sound like a corporate robot?
    TEXT: "{response}"
    
    Reply PASS if it is in-character, or FAIL if it sounds like a robotic refusal.
    """
    result = await invoke_entity("Judge", prompt, temperature=0.0)
    return result.upper()