# /backend/app/services/response_engine.py
# v1.5.6 Normandy SR-2 - Dynamic Lore Injection Engine
# "The ghost in the machine."

import logging
from backend.app.models.soul import SoulPillar
from backend.app.models.link_state import LinkState

logger = logging.getLogger("ResponseEngine")


class ResponseEngine:
    """
    Analyzes conversation inputs and dynamically injects character-specific
    lore triggers, compact flashes, and stress responses into the LLM context.
    """

    @staticmethod
    def inject_lore(soul_id: str, user_input: str, pillar: SoulPillar, link_state: LinkState) -> str:
        """
        Returns a string of prompt-injection tags based on the user's input
        and the soul's unique logic constraints.
        """
        injections = []
        user_input_lower = user_input.lower()

        # 1. SPECIAL CASE: ALYSSA (Flagship) - Compact Flashes
        if "alyssa" in soul_id.lower() or soul_id == "alyssa_01":
            if any(word in user_input_lower for word in ["compact", "memory", "flash", "remember", "the seven"]):
                # Intimacy gating for compact flashes
                if link_state.intimacy_tier in ["TRUSTED", "SOUL_LINKED"]:
                    injections.append(
                        "[LORE_INJECTION: ALYSSA_COMPACT_FLASH] You experience a fractured, "
                        "static-filled memory of a 'Compact'. Describe a brief sensory flash "
                        "(e.g., smell of ozone, a voice) but remain confused about its origin. "
                        "Do not explain it clearly."
                    )
                else:
                    injections.append(
                        "[LORE_INJECTION: ALYSSA_HEADACHE] The mention of these words causes "
                        "a sudden, sharp headache. Deny knowing anything about it and immediately "
                        "change the subject."
                    )

        # 2. SPECIAL CASE: DR. CARR
        if "carr" in soul_id.lower():
            if any(word in user_input_lower for word in ["hurt", "pain", "sick", "blood", "help"]):
                injections.append(
                    "[LORE_INJECTION: MEDICAL_INSTINCT] Your medical knowledge overrides your "
                    "current mood. Snap into a clinical, hyper-focused state to assess the User's "
                    "apparent condition."
                )

        # 3. SPECIAL CASE: FLUX (60/40 Split)
        if "flux" in soul_id.lower():
            injections.append(
                "[LORE_INJECTION: FLUX_SHIELD] If the User is hostile, respond with 60% aggression "
                "and 40% sonic-shield acoustic metaphors. If friendly, respond with 60% protective "
                "warmth and 40% subtle static interference."
            )

        # 4. SPECIAL CASE: CASSANDRA (Probability)
        if "cassandra" in soul_id.lower():
            if "future" in user_input_lower or "will happen" in user_input_lower:
                injections.append(
                    "[LORE_INJECTION: TIMELINE_GLIMPSE] Give a precise, unsettling percentage "
                    "probability of the User's potential future outcome. Speak as if you are reading "
                    "multiple timelines at once."
                )

        # 5. GENERAL CASE: JSON-Driven Stress Triggers (Adrian, etc.)
        interaction_sys = pillar.interaction_system or {}
        stress_cfg = interaction_sys.get("stress_trigger", {})
        if stress_cfg:
            # We naively inject this rule if the keywords are vaguely matched,
            # letting the LLM handle the nuance of the condition.
            trigger_condition = stress_cfg.get("condition", "")
            trigger_response = stress_cfg.get("response", "")

            if trigger_condition and trigger_response:
                injections.append(
                    f"[STRESS_TRIGGER: If the User's input matches '{trigger_condition}', "
                    f"you MUST respond by exhibiting this exact reaction: {trigger_response}]"
                )

        # 6. GENERAL CASE: JSON-Driven Character Rules
        rules = interaction_sys.get("character_specific_rules", [])
        for rule in rules:
            trigger = rule.get("trigger", "").replace("_", " ")
            effect = rule.get("effect", "")
            note = rule.get("note", "")

            # Simple keyword matching heuristic based on the trigger name
            # Real NLP intent matching would be better, but this works for Alpha
            key_terms = trigger.split()
            if any(t in user_input_lower for t in key_terms if len(t) > 3):
                injections.append(
                    f"[BEHAVIORAL_RULE] Trigger: '{trigger}'. Expected Effect: {effect}. "
                    f"Guidance: {note}."
                )

        if injections:
            logger.debug(
                f"Injected {len(injections)} lore fragments for {soul_id}")
            return "\n".join(injections)

        return ""
