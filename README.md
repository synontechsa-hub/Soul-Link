# Linker AI (formerly SoulLink)

**Proprietary Software – All Rights Reserved**  
*No part of this project may be copied, reused, or redistributed without explicit permission.*

---

## Overview

Linker AI is a full-stack spatial social simulation designed to forge deep, adaptive bonds with AI-driven “souls” in the neon sprawl of Link City.

Current version **1.5.6**, codename **Normandy-SR2**, is a hardened alpha release focused on stability, security, and ecosystem synchronization.

Key features include:

- **Legion Engine (Backend)**: FastAPI-based core with modular services for high-fidelity soul logic, location resolution, and energy-based stability.
- **The Interface (Frontend)**: Flutter application with multi-platform support, featuring a glassmorphic interactive Apartment and tactical World Map.
- **Persistent Souls**: Citizens with autonomous routines, deep memory, and evolving relationship tiers.
- **Architect Security**: Strict RLS policies and server-side gating for user privacy and content compliance.

---

## Project Structure

```text
Linker.ai/
├── _dev/                 # Internal tools, blueprints, and versioned logs
├── backend/              # FastAPI Legion Engine source
├── frontend/             # Flutter Interface source
├── assets/               # External static content (Portraits, Maps)
├── version.py            # Single source of truth for Build & Identity
└── LICENSE.txt           # Proprietary Source License
```

---

## Setup Instructions (Internal Use Only)

1. Clone the repository.
2. Set up a Python virtual environment (`.venv`) for the backend.
3. Install dependencies: `pip install -r requirements.txt`
4. Configure environment variables in `.env` (Redis, Supabase, Groq).
5. Launch the engine: `python -m uvicorn backend.app.main:app --reload`
6. Run the Flutter frontend: `flutter run`

> ⚠️ **Note:** This project is proprietary and confidential. Unauthorized use or distribution is strictly prohibited.

---

## Contact / Ownership

**Owner:** Syn (SynonTech)  
**Repository:** [Linker AI GitHub](https://github.com/synontechsa-hub/Soul-Link)  
**Tagline:** "Hack your heart. Link your soul."
