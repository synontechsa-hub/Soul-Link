
import sys
from pathlib import Path
from sqlalchemy import text
from sqlmodel import Session, select

# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database.session import engine
from backend.app.models import Soul, Location, SoulRelationship, Conversation, User

def validate_and_clean():
    print("🕵️ Starting Data Integrity Scan...")
    
    with Session(engine) as session:
        # 1. Check Relationships
        print("\n--- Checking Relationships ---")
        relationships = session.exec(select(SoulRelationship)).all()
        orphaned_rels = []
        for rel in relationships:
            user_exists = session.get(User, rel.user_id)
            soul_exists = session.get(Soul, rel.soul_id)
            
            if not user_exists:
                print(f"❌ Orphaned Relationship (No User): {rel.user_id} <-> {rel.soul_id}")
                orphaned_rels.append(rel)
            elif not soul_exists:
                print(f"❌ Orphaned Relationship (No Soul): {rel.user_id} <-> {rel.soul_id}")
                orphaned_rels.append(rel)
        
        if orphaned_rels:
            print(f"🧹 Removing {len(orphaned_rels)} orphaned relationships...")
            for rel in orphaned_rels:
                session.delete(rel)
        else:
            print("✅ All relationships valid.")

        # 2. Check Conversations
        print("\n--- Checking Conversations ---")
        conversations = session.exec(select(Conversation)).all()
        orphaned_msgs = []
        for msg in conversations:
            # Note: Conversation logic might be looser, but let's check basic existence
            # user_id should exist if it's not a system message (but even system msgs usually track a user session)
            if msg.user_id:
                user_exists = session.get(User, msg.user_id)
                if not user_exists:
                     print(f"❌ Orphaned Message (No User): {msg.msg_id} [User: {msg.user_id}]")
                     orphaned_msgs.append(msg)
            
            if msg.soul_id:
                 soul_exists = session.get(Soul, msg.soul_id)
                 if not soul_exists:
                     print(f"❌ Orphaned Message (No Soul): {msg.msg_id} [Soul: {msg.soul_id}]")
                     orphaned_msgs.append(msg)

        if orphaned_msgs:
            print(f"🧹 Removing {len(orphaned_msgs)} orphaned messages...")
            for msg in orphaned_msgs:
                session.delete(msg)
        else:
            print("✅ All conversations valid.")

        session.commit()
        print("\n✨ Data Validation Complete.")

if __name__ == "__main__":
    validate_and_clean()
