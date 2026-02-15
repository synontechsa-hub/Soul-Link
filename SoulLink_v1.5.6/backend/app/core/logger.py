# /backend/app/core/logger.py
# /version.py
# /_dev/

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LegionEngine")

class LegionLogger:
    @staticmethod
    def log_brain_thought(soul_id: str, prompt: str):
        print(f"\n🧠 [BRAIN THOUGHT - {soul_id}]")
        print("-" * 50)
        print(prompt)
        print("-" * 50 + "\n")

    @staticmethod
    def log_gatekeeper(action: str, allowed: bool):
        status = "✅ ALLOWED" if allowed else "🚫 BLOCKED"
        print(f"🛡️ [GATEKEEPER] {action}: {status}")