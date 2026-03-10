# /backend/app/services/soul_blueprint.py
# v1.5.6 Normandy SR-2 - Blueprints Loader
import os
import json
import logging
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.app.models.soul import Soul, SoulPillar, SoulState

logger = logging.getLogger("SoulBlueprint")


class SoulBlueprintService:
    """
    Service responsible for loading Soul blueprints from JSON files
    into the database and parsing their templates for the Engine.
    """

    def __init__(self):
        # Determine paths logically from this file
        # This file is in backend/app/services/, so _dev is ../../../_dev/
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))))
        self.data_dir = os.path.join(base_dir, "_dev", "data")
        self.soul_dirs = [
            os.path.join(self.data_dir, "souls"),
            os.path.join(self.data_dir, "premium_souls"),
            os.path.join(self.data_dir, "flagship_souls")
        ]

    def _get_all_json_files(self) -> List[str]:
        files = []
        for d in self.soul_dirs:
            if not os.path.exists(d):
                continue
            for f in os.listdir(d):
                if f.endswith(".json") and not f.endswith("template.json"):
                    files.append(os.path.join(d, f))
        return files

    async def ingest_blueprints(self, session: AsyncSession) -> dict:
        """
        Reads all JSON blueprints and upserts them into the database.
        Returns a summary of operations.
        """
        files = self._get_all_json_files()
        stats = {"added": 0, "updated": 0, "failed": 0}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                soul_id = data.get("soul_id")
                if not soul_id:
                    continue

                # Prepare Data
                version = data.get("version", "1.0.0")
                identity = data.get("identity", {})
                name = identity.get("name", "Unknown")
                summary = identity.get("summary", "")
                archetype = identity.get("archetype_id", "")

                aesthetic = data.get("aesthetic", {})
                portrait_url = aesthetic.get(
                    "portrait_path", f"/assets/images/souls/{soul_id}.png")

                # Check if Soul exists
                existing_soul = await session.get(Soul, soul_id)
                if not existing_soul:
                    # Create Soul
                    new_soul = Soul(
                        soul_id=soul_id,
                        name=name,
                        summary=summary,
                        portrait_url=portrait_url,
                        archetype=archetype,
                        version=version
                    )
                    session.add(new_soul)

                    # Create Pillar
                    new_pillar = SoulPillar(
                        soul_id=soul_id,
                        identity=identity,
                        aesthetic=aesthetic,
                        systems_config=data.get("systems_config", {}),
                        routine=data.get("routine", {}),
                        inventory=data.get("inventory", {}),
                        relationships=data.get("relationships", {}),
                        lore_associations=data.get("lore_associations", {}),
                        interaction_system=data.get("interaction_system", {}),
                        prompts=data.get("prompts", {}),
                        meta_data=data.get("meta_data", {})
                    )
                    session.add(new_pillar)

                    # Create default State if missing
                    existing_state = await session.get(SoulState, soul_id)
                    if not existing_state:
                        new_state = SoulState(
                            soul_id=soul_id,
                            current_location_id="soul_plaza",
                            energy=100,
                            mood="neutral"
                        )
                        session.add(new_state)

                    stats["added"] += 1
                else:
                    # Update Pillar if version changed or just force update
                    # For v1.5.6 we force sync the logic pillars to ensure JSON is reflected.
                    existing_pillar = await session.get(SoulPillar, soul_id)
                    if existing_pillar:
                        existing_pillar.identity = identity
                        existing_pillar.aesthetic = aesthetic
                        existing_pillar.systems_config = data.get(
                            "systems_config", {})
                        existing_pillar.routine = data.get("routine", {})
                        existing_pillar.inventory = data.get("inventory", {})
                        existing_pillar.relationships = data.get(
                            "relationships", {})
                        existing_pillar.lore_associations = data.get(
                            "lore_associations", {})
                        existing_pillar.interaction_system = data.get(
                            "interaction_system", {})
                        existing_pillar.prompts = data.get("prompts", {})
                        existing_pillar.meta_data = data.get("meta_data", {})
                        session.add(existing_pillar)

                        existing_soul.name = name
                        existing_soul.summary = summary
                        existing_soul.portrait_url = portrait_url
                        existing_soul.archetype = archetype
                        existing_soul.version = version
                        session.add(existing_soul)

                        stats["updated"] += 1
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
                stats["failed"] += 1

        try:
            await session.commit()
            logger.info(f"Ingestion complete: {stats}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to commit blueprints: {e}")
            stats["failed"] += stats["added"] + stats["updated"]
            stats["added"] = 0
            stats["updated"] = 0

        return stats


blueprint_service = SoulBlueprintService()
