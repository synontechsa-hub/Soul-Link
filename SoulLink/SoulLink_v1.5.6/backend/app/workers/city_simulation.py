# /backend/app/workers/city_simulation.py
# v1.5.6 Normandy SR-2 - The City Lives
# "The world breathes, even when you aren't looking."

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import text
from backend.app.database.session import async_session_maker
from backend.app.logic.time_manager import TimeManager

logger = logging.getLogger("CitySimulation")


class CitySimulationWorker:
    """
    Background worker that simulates the passage of time across Link City.
    It advances time slots for all active users, triggering routines and
    environmental shifts.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        # In a real production environment, this would be cron-based or longer.
        # For the Closed Alpha, we'll tick time forward every 60 minutes.
        self.scheduler.add_job(self.tick_city_forward, 'interval', minutes=60)

    def start(self):
        """Starts the background scheduler."""
        logger.info("Starting CitySimulation background worker...")
        self.scheduler.start()

    def shutdown(self):
        """Stops the background scheduler."""
        logger.info("Shutting down CitySimulation worker...")
        self.scheduler.shutdown()

    async def tick_city_forward(self):
        """
        The core loop: Advances time for all users and resolves world state.
        """
        logger.info("⏳ Ticking City Forward...")
        try:
            async with async_session_maker() as session:
                # Get all unique users
                result = await session.execute(text("SELECT user_id FROM users"))
                users = result.fetchall()

                tm = TimeManager(session)

                tasks = []
                for row in users:
                    user_id = row[0]
                    # Advance time for this user
                    # This automatically handles WebSocket notifications and cache invalidations
                    tasks.append(tm.advance_time_slot(user_id=user_id))

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                logger.info(
                    f"✅ Advanced time for {len(tasks)} users in Link City.")

        except Exception as e:
            logger.error(f"❌ City Simulation Tick Failed: {e}", exc_info=True)


# Singleton instance
city_simulation = CitySimulationWorker()
