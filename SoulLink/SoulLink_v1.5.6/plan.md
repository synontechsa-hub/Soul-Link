## Stage Index

| # | Stage | Status |
|---|---|---|
| 1 | DB Seeding — Schema + Data | ✅ Complete |
| 2 | Data File Fixes | ✅ Complete |
| 3 | `system_config` Table + System Seeder | ✅ Complete |
| 4 | Remove `_dev/` Runtime Dependencies | ✅ Complete |
| 5 | Critical Bug Fixes | ✅ Complete |
| 6 | Security Hardening | ✅ Complete |
| 7 | Performance Cleanup | ✅ Complete |
| 8 | Lore Expansion | ✅ Complete |
| 9 | Cleanup | ✅ Complete |
| 10 | Deploy | 🔄 In Progress |

---

## Stage 1 — DB Seeding ✅

> The local development database is fully seeded and validated.

- [x] **1.1** — Fix `create_schema_v156.py` import/path bugs
- [x] **1.2** — Fix `LOCAL_DB_URL` password in `.env` (was `postgres`, now correct)
- [x] **1.3** — Run schema creation — 12 tables created
- [x] **1.4** — Fix `seed_locations_v156.py` path resolution
- [x] **1.5** — Seed 31 locations
- [x] **1.6** — Fix `seed_souls_v156.py` path resolution
- [x] **1.7** — Seed 40 standard souls + pillars + states
- [x] **1.8** — Fix `insert_architect_v156.py` path resolution
- [x] **1.9** — Insert Architect account (UUID: `14dd612d-...`, tier: architect)
- [x] **1.10** — Fix boolean bug in `validate_seed_v156.py`
- [x] **1.11** — Run seed validation — ALL CHECKS PASSED

> ⚠️ **Note — 5 premium souls are missing.** The seeder searches `souls/premium_souls/` (wrong) instead of `_dev/data/premium_souls/` (correct).  
> Premium souls (Cassandra, Flux, Iris, Jade, Jericho) will be added once Stage 2 path fix is applied and souls are re-seeded. Target is **45 souls total**.

---

## Stage 2 — Data File Fixes ❌

> Fix broken references in the JSON source data before re-seeding.

- [ ] **2.1** — Fix `seed_souls_v156.py` premium/flagship directory paths
  - Change: `SOUL_SUBDIRS` to use `DATA_DIR / "premium_souls"` and `DATA_DIR / "flagship_souls"` (siblings of `souls/`, not children)
  - Impact: 5 premium souls currently skipped on every seed run

- [ ] **2.2** — Fix `SoulState` default spawn location
  - Change: `current_location_id="soul_plaza"` → use each soul's `routine.location_preferences.home_zone`
  - Files: `seed_souls_v156.py` line ~161 + `backend/app/services/soul_blueprint.py` line ~105

- [ ] **2.3** — Fix `_dev/data/system/factions.json`: remove `kai_01`
  - Change `underworld.key_souls`: `["vesper_01", "heather_01", "kai_01"]` → `["vesper_01", "heather_01", "echo_01"]`

- [ ] **2.4** — Fix `_dev/data/premium_souls/cassandra_01.json`: replace all 7 `the_observatory` references
  - Replace with `city_planetarium` in: `routine.location_preferences.*`, `routine.schedule_overrides.weekend.night`, `interaction_system.*.location_access[0]`

- [ ] **2.5** — Re-run `seed_souls_v156.py` to pull in all 45 souls
  - Verify with: `SELECT COUNT(*) FROM souls;` → expect 45

---

## Stage 3 — `system_config` Table + System Seeder ❌

> Move all system JSON files out of `_dev/` and into the database. Required before Stage 4.

- [ ] **3.1** — Create `backend/app/models/system_config.py`

  ```python
  class SystemConfig(SQLModel, table=True):
      __tablename__ = "system_config"
      key: str = Field(primary_key=True, max_length=100)
      data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
      version: str = Field(default="1.5.6", max_length=20)
      updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  ```

- [ ] **3.2** — Register `SystemConfig` in `backend/app/models/__init__.py` and `create_schema_v156.py`

- [ ] **3.3** — Run schema update to create `system_config` table

- [ ] **3.4** — Create `_dev/scripts/seed_system_v156.py`
  - Reads all 10 system JSONs → upserts into `system_config`
  - Keys: `weather`, `time_and_day`, `calendar`, `archetypes`, `factions`, `routines`, `intimacy`, `relationships`, `monetization`, `global_config`

- [ ] **3.5** — Create `_dev/scripts/seed_lore_v156.py`
  - Reads `system/lore.json` → upserts into `lore_items` table

- [ ] **3.6** — Create `_dev/scripts/seed_all_v156.py` (master seeder)
  - Runs all seeders in order: system → locations → souls → lore

- [ ] **3.7** — Run `seed_system_v156.py` and verify 10 rows in `system_config`

---

## Stage 4 — Remove `_dev/` Runtime Dependencies ❌

> Two backend files read from `_dev/` at runtime. Fix these or the app crashes in production.

- [ ] **4.1** — Fix `backend/app/main.py` — remove blueprint ingestion from startup
  - Remove: `await blueprint_service.ingest_blueprints(session)`
  - Replace with: DB count check + warning if `souls` table is empty
  - Add startup calls: `initialize_weather_from_db()` + `initialize_routines_cache()`

- [ ] **4.2** — Fix `backend/app/services/location_resolver.py` — stop reading `routines.json` from disk
  - Add: module-level `_ROUTINES_CACHE: dict = {}` + `initialize_routines_cache(data)` function
  - Replace: `open(routines.json)` block in `resolve_location()` with `_ROUTINES_CACHE.get(template_id)`
  - Fix: the `pass` stub in `resolve_bulk_locations()` — implement full resolution from cache

- [ ] **4.3** — Fix `backend/app/services/weather_service.py` — stop reading `weather.json` at module load
  - Add: `async def initialize_weather_from_db(session)` that reads from `system_config` → `"weather"` key
  - Keep: file read as local-dev fallback only

---

## Stage 5 — Critical Bug Fixes 🟡

- [x] **5.1** — Fix `datetime.utcnow()` deprecation — done in prior session
- [ ] **5.2** — Fix world state cache dict mutation (user data bleed)
  - File: `backend/app/logic/time_manager.py` line ~119
  - Change: `soul_locations = cached_data.copy()` → `soul_locations = dict(cached_data)`

---

## Stage 6 — Security Hardening 🟡

- [x] **6.1** — WebSocket token exposure — fixed in prior session
- [x] **6.2** — Hardcoded Architect UUID — moved to `.env` in prior session
- [x] **6.3** — AppLovin monetization bypass — fixed in prior session
- [x] **6.4** — Flutter `.env` file exposure — addressed in prior session
- [ ] **6.5** — Protect `/health/metrics` endpoint
  - File: `backend/app/api/health.py`
  - Add `user: User = Depends(get_current_user)` to `get_metrics()`
- [ ] **6.6** — Strip sensitive fields from `/core/config`
  - File: `backend/app/api/core.py`
  - Remove `debug` and `environment` from response; keep only `version` and `features`
- [ ] **6.7** — Fix location move broadcasting to all users
  - File: `backend/app/logic/location_manager.py` line ~75
  - Change: `broadcast_to_all({...})` → `send_to_user(user_id, {...})`
- [ ] **6.8** — Remove `default="mock_key"` from ad config fields
  - File: `backend/app/core/config.py` lines 64–71
  - Change: `applovin_sdk_key`, `applovin_ssv_secret`, `tapjoy_*` defaults → `None`
- [ ] **6.9** — Gate root `/` endpoint in production
  - File: `backend/app/main.py`
  - Return `{"status": "ok"}` when `settings.environment == "production"`

---

## Stage 7 — Performance Cleanup ❌

- [ ] **7.1** — Fix N+1 query in architect dashboard (`sync.py` lines 60–73)
  - Call `TimeManager.get_world_state()` once before soul loop
- [ ] **7.2** — Remove duplicate `connect_args` line (`session.py` line 98)
- [ ] **7.3** — Re-enable rate limiter on map endpoint (`map.py` line 26)
- [ ] **7.4** — Remove double import of `TimeManager`/`TimeSlot` in `map.py` (lines 35–36)

---

## Stage 8 — Lore Expansion ❌

> All content for this stage is fully written in `v1.5.6_plan.md` Section 2.3. Just needs to be applied.

- [ ] **8.1** — Add 4 faction lore entries to `_dev/data/system/lore.json`
  - `faction_the_architects`, `faction_the_dreamers`, `faction_the_pulse`, `faction_the_shadows`
- [ ] **8.2** — Add 8 landmark lore entries to `lore.json` (harvested from location files)
  - `circuit_diner`, `soul_plaza`, `skylink_tower`, `neon_nights`, `echo_archives`, `city_planetarium`, `umbral_exchange`, `obsidian_proving_grounds`
- [ ] **8.3** — Run `seed_lore_v156.py` — verify 16 rows in `lore_items`

---

## Stage 9 — Cleanup ❌

> Full detail in `v1.5.6_cleanup.md`. Do this last, before final deploy.

- [ ] **9.1** — Delete root-level test output (13 files ~3.1 MB): `test_results.txt`, `test_failures*.txt`, `test_output*.txt`, `test_run_*.txt`, `coverage.xml`, `error*.log`, etc.
- [ ] **9.2** — Delete root-level dev scripts: `fix_db_schema.py`, `test_lifespan.py`, `test_narrator.py`
- [ ] **9.3** — Nuke all `__pycache__` dirs (15 found)
- [ ] **9.4** — Delete `htmlcov/` and `.pytest_cache/`
- [ ] **9.5** — Delete `_dev/reports/`, `_dev/dev_log/` (old audit files + dev logs)
- [ ] **9.6** — Triage `_dev/notes/`: move `release_roadmap.md`, `store_compliance.md`, `vision_manifest.md` → `docs/`, delete the rest
- [ ] **9.7** — Delete diagnostic scripts: `diag_brain.py`, `diag_chat.py`, `inspect_db.py`, `generate_breakdown.py`, `rebirth_v157.py`, `test_chat_pipeline_v156.py`
- [ ] **9.8** — Verify `.env` is in `.gitignore` + excluded from Docker

---

## Stage 10 — Deploy ❌

- [ ] **10.1** — Frontend connects to all API endpoints correctly
- [ ] **10.2** — Seed production Supabase DB: `python _dev/scripts/seed_all_v156.py`
- [ ] **10.3** — Set all production `.env` vars: `GROQ_API_KEY`, `SUPABASE_DB_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `ARCHITECT_UUID`, `ENVIRONMENT=production`
- [ ] **10.4** — Start server: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
- [ ] **10.5** — Invite first alpha testers 🚀

---

## Post-Seed Verification SQL

```sql
-- System config (expect 10 rows after Stage 3)
SELECT key, version FROM system_config ORDER BY key;

-- Souls (expect 45 after Stage 2 path fix)
SELECT COUNT(*) FROM souls;

-- Premium souls specifically
SELECT soul_id, name FROM souls WHERE soul_id IN ('cassandra_01','flux_01','iris_01','jericho_01');

-- No soul incorrectly at soul_plaza (only souls whose home IS soul_plaza)
SELECT s.soul_id, st.current_location_id
FROM souls s JOIN soul_states st ON s.soul_id = st.soul_id
WHERE st.current_location_id = 'soul_plaza';

-- Locations (expect 31)
SELECT COUNT(*) FROM locations;

-- Lore items (expect 16 after Stage 8)
SELECT id, category FROM lore_items ORDER BY category;

-- No observatory reference surviving
SELECT soul_id FROM soul_pillars WHERE routine::text LIKE '%the_observatory%';
-- Should return 0 rows
```
