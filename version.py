# version.py
import os

SOUL_LINK_VERSION = "1.4.0"

# Deterministic debug mode (used for testing)
DEBUG_DETERMINISTIC = os.getenv("SOULLINK_DEBUG", "0") == "1"
