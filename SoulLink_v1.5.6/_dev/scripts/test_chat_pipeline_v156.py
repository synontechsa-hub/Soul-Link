"""
test_chat_pipeline_v156.py
--------------------------
Integration smoke test for the full SoulLink v1.5.6 chat pipeline.

Tests:
  1. [UNIT]   ContextAssembler builds a valid system prompt from mock data.
  2. [DB]     SoulPillar is correctly populated with v1.5.6 schema fields.
  3. [LIVE]   LegionBrain.generate_response() fires a real Groq request (optional).

Usage:
    python test_chat_pipeline_v156.py              # Unit + DB tests only
    python test_chat_pipeline_v156.py --live       # Include live Groq call
"""

import sys
import asyncio
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.models.soul import Soul, SoulPillar
from backend.app.models.link_state import LinkState
from backend.app.models.user_persona import UserPersona
from backend.app.models.location import Location
from backend.app.services.context_assembler import ContextAssembler
from backend.app.services.identity import IdentityService

LIVE_MODE = "--live" in sys.argv
SOUL_ID = "amber_01"
ARCHITECT_UUID = "14dd612d-744e-487d-b2d5-cc47732183d3"

PASS = "[PASS]"
FAIL = "[FAIL]"


# ── TEST 1: CONTEXT ASSEMBLER UNIT TEST ──────────────────────────────────────

def test_context_assembler():
    print("\n== TEST 1: Context Assembler (Offline) ==")
    
    soul = Soul(
        soul_id=SOUL_ID,
        name="Amber",
        summary="A warm, playful soul.",
        archetype="the_muse",
        version="1.5.6"
    )
    
    pillar = SoulPillar(
        soul_id=SOUL_ID,
        identity={"name": "Amber", "archetype_id": "the_muse"},
        aesthetic={"portrait_path": "/assets/amber.jpg", "tagline": "Sunshine and static."},
        systems_config={"capabilities": {"sexual_content": True, "violence": False}},
        routine={"template_id": "social_butterfly"},
        interaction_system={
            "intimacy_tiers": {
                "STRANGER": {
                    "llm_bias": "Maintain playful but distant energy.",
                    "allowed_topics": ["weather", "hobbies"],
                    "forbidden_topics": ["trauma", "secrets"]
                }
            }
        },
        prompts={
            "system_anchor_override": "You are Amber, a neon-lit spark in Link City. {user_name} feels like a warm breeze."
        },
        meta_data={
            "recognition_protocol": {
                "architect_awareness": True,
                "alyssa_awareness": True,
                "linker_awareness": True,
                "primordial_awareness": False,
                "creator_awareness": True
            },
            "dev_config": {
                "architect_ids": [ARCHITECT_UUID],
                "title": "The Architect"
            }
        },
        lore_associations={"secrets": ["She once met Alyssa face-to-face."]},
        routines={}
    )
    
    link = LinkState(
        user_id=ARCHITECT_UUID,
        soul_id=SOUL_ID,
        intimacy_tier="STRANGER",
        intimacy_score=0,
        signal_stability=100.0,
        current_mood="curious",
        is_architect=True,
        unlocked_nsfw=False,
        current_location="soul_plaza"
    )
    
    persona = UserPersona(
        user_id=ARCHITECT_UUID,
        screen_name="Garrett",
        bio="The one who built the city.",
        age=28,
        gender="Male",
        identity_anchor="Always has a faint smell of ozone"
    )
    
    location = Location(
        location_id="soul_plaza",
        display_name="Soul Plaza",
        description="The central hub, humming with synthetic energy.",
        system_modifiers={"privacy_gate": "Public", "mood_modifiers": {"energized": 0.9, "neutral": 0.1}}
    )
    
    try:
        prompt = ContextAssembler.build_system_prompt(
            soul=soul,
            pillar=pillar,
            persona=persona,
            link_state=link,
            location=location,
            is_architect=True,
            world_state="[WEATHER: Crimson Fog. Visibility: 40%]"
        )
        
        # Assertions
        errors = []
        if "Garrett" not in prompt: errors.append("screen_name not injected")
        if "CREATOR" not in prompt: errors.append("Architect AUTH not injected")
        if "STRANGER" not in prompt: errors.append("Intimacy tier missing")
        if "Alyssa is a known Anomaly" not in prompt: errors.append("Alyssa awareness missing")
        if "The Architect is Creator" not in prompt: errors.append("Architect awareness missing")
        if "Crimson Fog" not in prompt: errors.append("World state not injected")
        if "SFW_ONLY" not in prompt: errors.append("Content ceiling missing (NSFW false, should be SFW)")
        if "playful but distant" not in prompt: errors.append("Tier LLM bias not injected")
        if "DIVINE_RECOGNITION" not in prompt: errors.append("Creator awareness not injected for Architect")
        
        if errors:
            print(f"  {FAIL} Context assembler failed:")
            for e in errors: print(f"    - {e}")
            return False
        else:
            print(f"  {PASS} System prompt assembled correctly ({len(prompt)} chars).")
            print(f"\n  -- PROMPT PREVIEW --")
            print(f"  {prompt[:800]}...")
            return True
    except Exception as e:
        import traceback
        print(f"  {FAIL} Exception: {e}")
        print(traceback.format_exc())
        return False


# ── TEST 2: DATABASE PILLAR CHECK ──────────────────────────────────────────

def test_db_pillar():
    print("\n== TEST 2: Database Pillar Integrity (amber_01) ==")
    from backend.app.database.session import engine
    from sqlmodel import Session
    
    try:
        with Session(engine) as session:
            pillar = session.get(SoulPillar, SOUL_ID)
            
            if not pillar:
                print(f"  {FAIL} SoulPillar for '{SOUL_ID}' not found in DB.")
                return False
            
            checks = {
                "prompts": bool(pillar.prompts),
                "interaction_system": bool(pillar.interaction_system),
                "meta_data": bool(pillar.meta_data),
                "recognition_protocol": bool(pillar.meta_data.get("recognition_protocol")),
                "architect_awareness": pillar.meta_data.get("recognition_protocol", {}).get("architect_awareness", False),
                "architect_uuid_in_dev_config": ARCHITECT_UUID in pillar.meta_data.get("dev_config", {}).get("architect_ids", []),
                "systems_config": bool(pillar.systems_config),
                "identity": bool(pillar.identity),
                "aesthetic": bool(pillar.aesthetic),
            }
            
            all_pass = True
            for key, val in checks.items():
                status = PASS if val else FAIL
                print(f"  {status} {key}: {val}")
                if not val:
                    all_pass = False
            
            return all_pass
    except Exception as e:
        import traceback
        print(f"  {FAIL} DB error: {e}")
        print(traceback.format_exc())
        return False


# ── TEST 3: LIVE GROQ CALL ────────────────────────────────────────────────

async def test_live_chat():
    print("\n== TEST 3: Live Brain Call (Groq) ==")
    from backend.app.logic.brain import LegionBrain
    from backend.app.database.session import engine
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.core.config import settings
    
    # Derive async URL from sync URL
    async_url = str(engine.url).replace("postgresql://", "postgresql+asyncpg://")
    async_engine = create_async_engine(async_url, pool_pre_ping=True)
    async_session_factory = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    
    brain = LegionBrain(async_engine)
    
    try:
        async with async_session_factory() as session:
            # Fetch a real LinkState (the architect)
            from sqlmodel import select
            link_result = await session.execute(
                select(LinkState).where(
                    LinkState.user_id == ARCHITECT_UUID,
                    LinkState.soul_id == SOUL_ID
                )
            )
            link = link_result.scalars().first()
            
            if not link:
                # Create a temporary one
                link = LinkState(
                    user_id=ARCHITECT_UUID,
                    soul_id=SOUL_ID,
                    intimacy_tier="STRANGER",
                    intimacy_score=0,
                    signal_stability=100.0,
                    current_mood="curious",
                    is_architect=True,
                    unlocked_nsfw=False,
                    current_location="soul_plaza"
                )
            
            persona = UserPersona(
                user_id=ARCHITECT_UUID,
                screen_name="Garrett",
                is_active=True
            )
            
            response = await brain.generate_response(
                user_id=ARCHITECT_UUID,
                soul_id=SOUL_ID,
                user_input="Hey, how's Link City today?",
                session=session,
                link_state=link,
                persona=persona
            )
            
            print(f"  {PASS} Groq responded ({len(response)} chars):")
            print(f"  > {response}")
            return True
    except Exception as e:
        import traceback
        print(f"  {FAIL} Live test failed: {e}")
        print(traceback.format_exc())
        return False
    finally:
        await async_engine.dispose()


# ── RUNNER ────────────────────────────────────────────────────────────────

async def main():
    print("=" * 55)
    print("  SoulLink v1.5.6 -- Chat Pipeline Integration Test")
    print("=" * 55)
    
    results = []
    results.append(("Context Assembler", test_context_assembler()))
    results.append(("DB Pillar Integrity", test_db_pillar()))
    
    if LIVE_MODE:
        live_pass = await test_live_chat()
        results.append(("Live Groq Call", live_pass))
    else:
        print("\n  [SKIPPED] Live Groq test. Run with --live to enable.")
    
    print("\n" + "=" * 55)
    print("  RESULTS SUMMARY")
    print("=" * 55)
    all_pass = True
    for name, passed in results:
        status = PASS if passed else FAIL
        print(f"  {status}  {name}")
        if not passed:
            all_pass = False
    
    print()
    if all_pass:
        print("  ALL TESTS PASSED. Pipeline is NOMINAL.")
    else:
        print("  SOME TESTS FAILED. Review output above.")
    print("=" * 55)

if __name__ == "__main__":
    asyncio.run(main())
