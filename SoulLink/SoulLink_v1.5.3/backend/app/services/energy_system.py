# /backend/app/services/energy_system.py
from datetime import datetime, timedelta
from backend.app.models.user import User
from sqlmodel import Session

# "Power overwhelming." - Archon, StarCraft
class EnergySystem:
    MAX_ENERGY = 100
    REFILL_RATE_MINUTES = 5
    REFILL_AMOUNT = 1

    @staticmethod
    def check_and_deduct_energy(user: User, session: Session) -> bool:
        """
        Manages the Energy Economy.
        Returns True if user is in FAST MODE (Energy Used).
        Returns False if user is in SLOW MODE (Energy Depleted).
        """
        # 0. God Mode Bypass
        if user.account_tier in ["admin", "architect", "vip"]:
            return True

        # 1. Regenerate Energy First
        now = datetime.utcnow()
        last_refill = user.last_energy_refill or user.created_at
        
        delta = now - last_refill
        minutes_passed = delta.total_seconds() / 60
        
        if minutes_passed >= EnergySystem.REFILL_RATE_MINUTES:
            # Calculate how many chunks of 5 mins passed
            refill_cycles = int(minutes_passed // EnergySystem.REFILL_RATE_MINUTES)
            energy_gain = refill_cycles * EnergySystem.REFILL_AMOUNT
            
            # Update Energy (Cap at 100)
            if user.energy < EnergySystem.MAX_ENERGY:
                user.energy = min(EnergySystem.MAX_ENERGY, user.energy + energy_gain)
            
            # Reset the clock (keep the remainder to avoid losing seconds)
            # Actually, simplest approach is just reset to now for MVP stability
            user.last_energy_refill = now
            session.add(user)
            # We commit later or let the caller handle it (Caller handles commit usually)

        # 2. Check Deductions
        if user.energy > 0:
            user.energy -= 1
            user.lifetime_tokens_used += 1 # Tracking for analytics
            session.add(user)
            return True # FAST MODE
        else:
            return False # SLOW MODE
