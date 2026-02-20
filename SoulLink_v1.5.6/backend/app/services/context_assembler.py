# /backend/app/services/context_assembler.py
# v1.5.6 Prompt Engineering - The Signal Hierarchy

from typing import List, Optional, Dict
from backend.app.models.soul import Soul, SoulPillar
from backend.app.models.user_persona import UserPersona
from backend.app.models.link_state import LinkState
from backend.app.models.location import Location
from backend.app.services.identity import IdentityService
from backend.app.services.rules import Gatekeeper

class ContextAssembler:
    """
    Constructs the System Prompt based on the 5-State Hierarchy.
    1. System Anchor (The Soul's Core)
    2. World Context (Time, Weather, Location)
    3. User Context (Persona, LinkState)
    4. Relational Context (Memory, Intimacy)
    5. Immediate Instruction (Protocols)
    """

    @staticmethod
    def build_system_prompt(
        soul: Soul,
        pillar: SoulPillar,
        persona: UserPersona,
        link_state: LinkState,
        location: Optional[Location],
        is_architect: bool,
        world_state: str = ""
    ) -> str:
        
        # 1. SYSTEM ANCHOR (The Core)
        # We replace {user_name} with the Persona's screen_name
        user_name = persona.screen_name
        prompts = pillar.prompts or {}
        base_anchor = prompts.get("system_anchor_override", "")
        system_anchor = base_anchor.replace("{user_name}", user_name)

        # 🧪 ARCHITECT OVERRIDE
        if is_architect:
            recognition_logic = IdentityService.get_recognition_instructions(pillar, user_name)
            system_anchor += recognition_logic

        # 2. CONTEXT TAGS
        context_tags = []

        # [WORLD STATE]
        if world_state:
            context_tags.append(world_state)

        # [AUTH & ROLE]
        if is_architect:
            context_tags.append(f"[AUTH: {IdentityService.get_architect_title(pillar)} | ROLE: CREATOR]")
        
        # [THE RESIDENT] (Replaces old User Profile)
        resident_info = [f"NAME: {user_name}"]
        if persona.gender: resident_info.append(f"GENDER: {persona.gender}")
        if persona.age: resident_info.append(f"AGE: {persona.age}")
        if persona.bio: resident_info.append(f"BIO: {persona.bio}")
        if persona.identity_anchor: resident_info.append(f"ANCHOR: {persona.identity_anchor}")
        
        context_tags.append(f"[THE RESIDENT: {' | '.join(resident_info)}]")

        # [AWARENESS PROTOCOL]
        # Injected from Soul Meta Data (v1.5.6)
        meta = pillar.meta_data or {}
        recognition = meta.get("recognition_protocol", {})
        if recognition:
            knowledge = []
            if recognition.get("alyssa_awareness"): knowledge.append("Alyssa is a known Anomaly")
            # if recognition.get("administrator_awareness"): knowledge.append("Admins exist") # Superseded by new schema? Or kept? 
            # User removed 'administrator_awareness' from the new list. I will map strict schema.
            if recognition.get("architect_awareness"): knowledge.append("The Architect is Creator")
            if recognition.get("linker_awareness"): knowledge.append("Linkers (Users) are known entities")
            if recognition.get("creator_awareness") and is_architect: knowledge.append("You perceive the User as a Creator-level entity")
            
            # Explicit denials for high-risk hallucinations
            if recognition.get("primordial_awareness") is False:
                knowledge.append("Primordials are UNKNOWN")
            # if recognition.get("flagship_awareness") is False: knowledge.append("Flagship Souls are UNKNOWN") # Removed from strict list

            if knowledge:
                context_tags.append(f"[KNOWLEDGE: {' | '.join(knowledge)}]")

        # [SENSORY ANCHOR] (Location)
        privacy_level = "Public"
        if location:
            mods = location.system_modifiers or {}
            privacy_level = mods.get("privacy_gate", "Public")
            moods = mods.get("mood_modifiers", {})
            top_mood = max(moods.items(), key=lambda x: float(x[1]))[0] if moods else "neutral"
            
            description_text = f"Setting: {location.description}. " if location.description else ""
            
            anchor_str = (
                f"[SENSORY_ANCHOR] You are at '{location.display_name}'. "
                f"{description_text}"
                f"Atmosphere: {top_mood}. Privacy: {privacy_level}. "
                "You cannot leave or be elsewhere during this turn."
            )
            context_tags.append(anchor_str)

        # 3. CONTENT CEILING (Privacy/NSFW)
        # SERVER-SIDE AGE GATE: If persona age is set and under 18, force SFW regardless of LinkState.
        # This cannot be bypassed by the client.
        nsfw_allowed = link_state.unlocked_nsfw
        if persona.age is not None and persona.age < 18:
            nsfw_allowed = False

        # Deep Scan Fix: Inject Consent Notes for behavioural grounding
        sys_cfg = pillar.systems_config or {}
        consent_notes = sys_cfg.get("consent", {}).get("notes", "")
        consent_instr = f" [CONSENT_GUIDELINE: {consent_notes}]" if consent_notes else ""

        if not nsfw_allowed:
             context_tags.append(f"[CONTENT: SFW_ONLY] Sexual content is strictly prohibited.{consent_instr}")
        elif privacy_level == "Private" and link_state.intimacy_tier in ["TRUSTED", "SOUL_LINKED"]:
             context_tags.append(f"[CONTENT: UNRESTRICTED] Adult themes allowed in private.{consent_instr}")
        else:
             context_tags.append(f"[CONTENT: SFW_ONLY]{consent_instr}")

        # 4. LORE & INTIMACY CONFIGURATION (v1.5.6)
        # Extract Interaction Data
        interaction_system = pillar.interaction_system or {}
        intimacy_tiers = interaction_system.get("intimacy_tiers", {})
        
        current_tier = link_state.intimacy_tier if link_state.intimacy_tier else "STRANGER"
        
        if intimacy_tiers:
            tier_data = intimacy_tiers.get(current_tier, {})
            
            # [A] BIAS INJECTION (Personality Modifier)
            tier_bias = tier_data.get("llm_bias", "")
            if tier_bias:
                 context_tags.append(f"[PERSONALITY_MODIFIER] {tier_bias}")
                 
            # [B] TOPIC GATING
            allowed = tier_data.get("allowed_topics", [])
            forbidden = tier_data.get("forbidden_topics", [])
            
            if allowed:
                 context_tags.append(f"[ALLOWED_TOPICS] {', '.join(allowed)}")
            if forbidden:
                 context_tags.append(f"[FORBIDDEN_TOPICS] {', '.join(forbidden)}")

        # [C] SECRET REVEALS (Lore Gating)
        lore_data = pillar.lore_associations or {}
        
        secrets = lore_data.get("secrets", [])
        if secrets and current_tier == "SOUL_LINKED":
             context_tags.append(f"[SECRETS_REVEALED] {'; '.join(secrets)}")

        # [D] SPEECH PROFILE (v1.5.6 Deep Scan Fix)
        aesthetic = pillar.aesthetic or {}
        speech = aesthetic.get("speech_profile", {})
        if speech:
            voice = speech.get("voice_style", "")
            emote = speech.get("signature_emote", "")
            forbid = speech.get("forbidden_behaviours", [])
            
            speech_tags = []
            if voice: speech_tags.append(f"VOICE: {voice}")
            if emote: speech_tags.append(f"EMOTE: {emote}")
            if forbid: speech_tags.append(f"FORBIDDEN: {', '.join(forbid)}")
            
            if speech_tags:
                context_tags.append(f"[SPEECH_PROFILE: {' | '.join(speech_tags)}]")

        # 5. PROTOCOLS
        protocols = (
            "\n\n[PROTOCOL]\n"
            "- Actions: *wrap in single asterisks*\n"
            "- Internal Monologue: Weave thoughts directly into actions.\n"
            "- Forbidden: parentheses (), character-breaking"
        )
        if is_architect:
            protocols += ", [meta-dialogue ok]"



        # 6. ASSEMBLY
        full_system_prompt = (
            f"{system_anchor}\n"
            f"{' '.join(context_tags)}\n"
            f"[TIER: {link_state.intimacy_tier}] [SCORE: {link_state.intimacy_score}]\n"
            f"[MOOD: {link_state.current_mood.upper()}]\n"
            f"{protocols}"
        )
        
        return full_system_prompt
