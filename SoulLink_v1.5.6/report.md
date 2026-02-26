# Senior Dev Team Report: SoulLink v1.5.6 (Normandy SR-2)

**Date:** 22 February 2026  
**Auditor:** Antigravity (Acting Senior Dev Team)  

## System Architecture & State of the Build

The core foundational elements of **SoulLink v1.5.6** are spectacular.

- **The Data Layer (`_dev/data`)** represents a massive leap forward. The deeply textured JSON schemas for souls (e.g., `adrian_01.json`) and locations (e.g., `circuit_diner.json`) are world-class. The mechanics embedded directly into character behaviors (`intimacy_tiers`, `consent`, `stress_trigger`) create an immersive, dynamic simulation.
- **The UI/Frontend** is highly polished and conceptually sound.

**However, the Backend Orchestrator (Python/FastAPI) is operating as technical debt.**
Currently, there is a severe disconnect between the robust JSON definitions in `_dev/data` and what the backend is actually executing. The backend still retains deprecated legacy models, blocking synchronous calls, and security flaws that will not survive a production alpha launch.

We act as the translator bringing the backend up to par with the data layer.

## The Core Issues

### 1. The Boot & Model Clash (System DevOps)

The server struggles to even boot properly or maintain schema integrity.

- **Imports:** Vital routers (`websocket`, `time`, `health`, etc.) are completely missing from the module initializations. The server throws `ModuleNotFoundError` on `version.py`.
- **Database Clashes:** `SoulRelationship` and `UserSoulState` are competing with the new `LinkState` table. If these execute in production, the database schema will conflict and corrupt user data.

### 2. Security Vulnerabilities (Systems Security)

- **Token Exposure:** The WebSocket connection accepts JWT tokens in the URL query parameters (`?token=...`). This prints plain text auth tokens into server access logs, giving attackers direct access.
- **Ad Reward Bypasses:** The AppLovin SSV (Server-Side Verification) endpoint expects a user token (`Bearer`) which AppLovin servers do not possess. Simultaneously, there is a bypass hardcoded in that grants rewards as long as the secret is "mock_secret"—giving users unlimited free stability.
- **Hardcoded Secrets:** `ARCHITECT_UUID` is hardcoded as a literal string in over 7 files instead of respecting environment variables.

### 3. Stability & Concurrency (Systems Architecture)

- **The Event Loop Block:** The LLM integration (`Groq`) is making synchronous calls. Every time the AI answers a message, the *entire server freezes* for all users until the response generates.
- **Desynced Time States:** The backend frequently alerts the frontend via WebSocket that an event (e.g., time progression) has occurred *before* the database actually commits it. If the DB fails, the user is looking at a phantom reality.

### 4. Code & Data Sync

- The Python codebase is currently trying to parse `TXT` files and older implementations instead of strictly running off the highly detailed `_dev/data` JSONs.
- This results in missing fields, such as `unlocked_nsfw` being called `nsfw_enabled` by the frontend, meaning data is discarded.

## How We Move Forward (The Plan)

We have formalized a 4-phase **Implementation Plan** (see artifacts). We will execute these changes sequentially:

**Phase 0: Unblock the Core**
We will rip out the deprecated models, fix the critical imports, and get the server to a guaranteed secure boot state.

**Phase 1: Hardening the Gates**
The WebSocket handshake and the ad reward verification will be hardened. The system will rely purely on valid server-side signatures for ads and message-based tokens for sockets.

**Phase 2: Freeing the Event Loop**
We will wrap the Groq logic in asynchronous executors so The Brain can think without freezing Link City. Cache states and transaction orders will be structurally enforced.

**Phase 3: Building The Bridge (Data Integration)**
We will build the parsers specifically targeted at the beautiful `_dev/data/**/*.json` schemas so that characters like Adrian operate off their actual intimacy rules rather than static blocking calls.

---
**Conclusion:**
You built a masterpiece of a world. Now, my job as the Senior Dev is to wire the engine so it actually drives instead of just looking pristine in the garage.

Let me know if we are clear to advance to Phase 0.
