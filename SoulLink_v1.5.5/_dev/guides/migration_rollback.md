# 🛡️ SoulLink Data Safety Protocols: Migration & Rollback

> "Time is a flat circle, but sometimes we need to rewind the tape." - True Detective / The Architect

This guide details how to safely manage database schema changes and recover from catastrophic data loss during the Closed Alpha.

---

## 1. Automated Safeguards

The **Legion Engine** (Backend) automatically performs the following:

- **Daily Backups**: A full JSON export of all core tables runs every 24 hours.
- **Startup Backups**: A backup is triggered every time the backend restarts (`Lifespan` event).

Backups are stored in: `_dev/data_backups/`

---

## 2. Managing Schema Migrations (Alembic)

We use **Alembic** to version-control our database schema.

### Creating a Migration

When you modify a generic `SQLModel` (e.g., adding a field to `Soul`):

```bash
# 1. Generate the migration script
alembic revision --autogenerate -m "Add coherence_score to Soul"

# 2. Review the generated file in /migrations/versions/
# ensure it looks correct!

# 3. Apply the migration
alembic upgrade head
```

### Rolling Back a Migration (Schema Only)

If a migration breaks the application logic (but didn't delete data):

```bash
# Undo the last migration
alembic downgrade -1
```

---

## 3. Disaster Recovery (Data Restoration)

If a migration accidentally deletes data (e.g., dropping a column or table), or if the database becomes corrupted, use the **Restore Script**.

### Prerequisites

- Ensure the server is **STOPPED** (to avoid locking issues).
- Identify the target timestamp from `_dev/data_backups/`.
  - Example: `users_20260209_120000.json` → Timestamp is `20260209_120000`.

### Running the Restore

This script will **WIPE** the current database and reload data from the backup JSONs.

```bash
# Restore from the LATEST backup (default)
python _dev/scripts/restore_db.py

# Restore from a SPECIFIC point in time
python _dev/scripts/restore_db.py --timestamp 20260209_120000
```

### Verification

After restoring, verify integrity:

1. Start the server.
2. Check `/api/v1/health` (should be healthy).
3. Check `/api/v1/map/world-state` (should show souls).

---

## 4. Manual Backup (Emergency)

To manually trigger a backup before a risky operation:

```bash
python _dev/scripts/backup_db.py
```

*(Note: Requires the server to be stopped if using SQLite in strict mode, though the script attempts to share access).*
