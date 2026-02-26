# /backend/scripts/ingestion.py
# v1.5.6 Data Ingestion System
# Parses all _dev/data JSONs and writes to the Linker.ai Database

import os
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import database session logic
from backend.app.database.session import get_session, engine
from backend.app.models.soul import Soul, SoulPillar, SoulState
from backend.app.models.location import Location

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestionSystem")

DEV_DATA_DIR = Path(__file__).parent.parent.parent / "_dev" / "data"


def init_db(session: Session):
    """Ensure tables exist (SQLModel.metadata.create_all handles this in main, but let's be safe)"""
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)


def ingest_locations(session: Session):
    logger.info("--- Ingesting Locations ---")
    loc_dir = DEV_DATA_DIR / "locations"

    if not loc_dir.exists():
        logger.warning(f"Location directory not found at {loc_dir}")
        return

    count = 0
    for file_path in loc_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            loc_id = data.get("location_id")
            if not loc_id:
                logger.warning(f"Missing location_id in {file_path.name}")
                continue

            meta = data.get("meta", {})
            location = session.get(Location, loc_id)
            if not location:
                location = Location(location_id=loc_id)

            location.display_name = meta.get("display_name", loc_id)
            location.category = meta.get("category")
            location.description = meta.get("description")
            location.music_track = meta.get(
                "music_track", "ambient_city_loop.mp3")
            location.image_url = meta.get("image_url")

            location.system_prompt_anchors = data.get(
                "system_prompt_anchors", {})
            location.game_logic = data.get("game_logic", {})
            location.lore = data.get("lore", {})
            location.source_metadata = data.get("metadata", {})
            location.system_modifiers = data.get("system_modifiers", {})

            # For backward compatibility
            entry_rules = location.game_logic.get("entry_rules", {})
            location.min_intimacy = entry_rules.get("min_intimacy", 0)

            session.add(location)
            count += 1
            logger.info(f"Ingested Location: {loc_id}")

    session.commit()
    logger.info(f"Total Locations Ingested: {count}")


def ingest_souls(session: Session, subdir: str = "souls"):
    logger.info(f"--- Ingesting Souls from {subdir} ---")
    souls_dir = DEV_DATA_DIR / subdir

    if not souls_dir.exists():
        logger.warning(f"Souls directory not found at {souls_dir}")
        return

    count = 0
    for file_path in souls_dir.glob("*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON {file_path.name}: {e}")
                continue

            soul_id = data.get("soul_id")
            if not soul_id:
                logger.warning(f"Missing soul_id in {file_path.name}")
                continue

            # 1. Identity Extraction
            identity = data.get("identity", {})
            aesthetic = data.get("aesthetic", {})

            soul = session.get(Soul, soul_id)
            if not soul:
                soul = Soul(soul_id=soul_id)

            soul.name = identity.get("name", soul_id)
            soul.summary = identity.get("summary", "A mysterious soul...")
            soul.portrait_url = aesthetic.get(
                "portrait_path", f"/assets/images/souls/{soul_id}.png")
            soul.archetype = identity.get("archetype_id")
            soul.version = data.get("version", "1.5.6")

            session.add(soul)

            # 2. Pillar Extraction
            pillar = session.get(SoulPillar, soul_id)
            if not pillar:
                pillar = SoulPillar(soul_id=soul_id)

            pillar.identity = data.get("identity", {})
            pillar.aesthetic = data.get("aesthetic", {})
            pillar.systems_config = data.get("systems_config", {})
            pillar.routine = data.get("routine", {})
            pillar.inventory = data.get("inventory", {})
            pillar.relationships = data.get("relationships", {})
            pillar.lore_associations = data.get("lore_associations", {})
            pillar.interaction_system = data.get("interaction_system", {})
            pillar.prompts = data.get("prompts", {})
            pillar.meta_data = data.get("meta_data", {})

            session.add(pillar)

            # 3. State Initialization (if it doesn't exist)
            state = session.get(SoulState, soul_id)
            if not state:
                state = SoulState(soul_id=soul_id)
                session.add(state)

            count += 1
            logger.info(f"Ingested Soul: {soul_id}")

    session.commit()
    logger.info(f"Total Souls Ingested ({subdir}): {count}")


def run_ingestion():
    logger.info("=== STARTING SOULLINK INGESTION ===")

    # We use a session from the main engine
    session_generator = get_session()
    session = next(session_generator)

    try:
        init_db(session)
        ingest_locations(session)

        # Ingest standard souls
        ingest_souls(session, "souls")

        # Ingest premium souls (if any)
        ingest_souls(session, "premium_souls")

        # Ingest flagship souls (if any)
        ingest_souls(session, "flagship_souls")

        logger.info("=== INGESTION COMPLETE ===")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    run_ingestion()
