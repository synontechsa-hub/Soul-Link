# /_dev/scripts/test_chat.py
# /version.py

import sys
import os
from pathlib import Path

# Find the root
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.core.config import settings
from backend.app.logic.brain import PhoenixBrain
from sqlmodel import create_engine, Session, select
from backend.app.models.relationship import SoulRelationship
from backend.app.models.soul import Soul

engine = create_engine(settings.database_url)

def chat(user_id: str, soul_id: str):
    """Terminal chat interface for any user"""
    
    # Verify relationship exists
    with Session(engine) as session:
        rel = session.exec(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        ).first()
        
        if not rel:
            print(f"❌ No relationship found between {user_id} and {soul_id}")
            print(f"💡 Tip: Run seed_db.py or use /souls/{soul_id}/link endpoint first")
            return
        
        soul = session.get(Soul, soul_id)
        soul_name = soul.name if soul else soul_id
    
    brain = PhoenixBrain(engine)
    
    print(f"🌙 SoulLink Phoenix v1.5.3 - Terminal Interface")
    print(f"Connected: {user_id} ↔ {soul_name}")
    print(f"Tier: {rel.intimacy_tier} | Location: {rel.current_location}")
    print("─" * 60)
    print("Type 'exit' or 'quit' to end session\n")
    
    while True:
        user_in = input(f"{user_id}: ")
        if user_in.lower() in ["exit", "quit"]: 
            print(f"\n👋 Disconnecting from {soul_name}...")
            break
        
        if not user_in.strip():
            continue
        
        try:
            response = brain.generate_response(user_id, soul_id, user_in)
            print(f"\n{soul_name}: {response}\n")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Parse arguments
    if len(sys.argv) < 3:
        print("Usage: python test_chat.py <user_id> <soul_id>")
        print("\nExamples:")
        print("  python test_chat.py USR-001 evangeline_01")
        print("  python test_chat.py USR-A3F2B8C1 adrian_01")
        print("\n💡 For Architect mode, use USR-001")
        sys.exit(1)
    
    user_id = sys.argv[1]
    soul_id = sys.argv[2]
    
    chat(user_id, soul_id)
