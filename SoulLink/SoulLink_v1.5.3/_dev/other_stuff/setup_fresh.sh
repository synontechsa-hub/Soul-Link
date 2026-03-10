# /_dev/scripts/setup_fresh.sh

#!/bin/bash
echo "🔥 Phoenix Setup - Fresh Install"
python _dev/scripts/nuke_db.py
python _dev/scripts/seed_db.py
echo "✅ Setup Complete! Try: python _dev/scripts/test_chat.py USR-001 evangeline_01"