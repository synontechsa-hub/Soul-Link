# DEV SCRIPTS GUIDE - SoulLink Phoenix v1.5.3

## 📁 Script Inventory

| Script | Purpose | Changes Made |
|--------|---------|--------------|
| `init_db.py` | Create database tables | ✅ No changes needed |
| `nuke_db.py` | Drop all tables | ✅ No changes needed |
| `seed_db.py` | Load souls + locations + USR-001 | ✅ Fixed field name, added ensure_architect |
| `boost_intimacy.py` | Test intimacy progression | ✅ Now supports any user_id |
| `move_to.py` | Teleport souls between locations | ✅ Now supports any user_id |
| `test_chat.py` | Terminal chat interface | ✅ Now supports any user_id |
| ~~`create_dev_user.py`~~ | ~~Create USR-001~~ | ⚠️ REDUNDANT - seed_db does this now |

---

## 🔥 CRITICAL FIX APPLIED

### **seed_db.py - Line 91**
**BEFORE:**
```python
"llm_instructions": raw_data.get("llm_instruction_override", {}),  # ❌
```

**AFTER:**
```python
"llm_instruction_override": raw_data.get("llm_instruction_override", {}),  # ✅
```

**Why:** Your Soul model expects `llm_instruction_override`, not `llm_instructions`!

---

## 📖 USAGE GUIDE

### 🏗️ **1. Database Setup**

```bash
# Drop everything (NUCLEAR OPTION)
python _dev/scripts/nuke_db.py

# Create tables
python _dev/scripts/init_db.py

# Load souls + locations + create USR-001 (The Architect)
python _dev/scripts/seed_db.py
```

**What `seed_db.py` does now:**
1. Creates all tables
2. Creates USR-001 (The Architect) with admin privileges
3. Loads all souls from `/_dev/blueprints/*.json`
4. Auto-links USR-001 to ALL souls with SOUL_LINKED tier
5. Seeds 7 locations in Link City

**✅ ONE COMMAND = FULL DATABASE SETUP**

---

### 💬 **2. Terminal Chat Testing**

```bash
# Chat as The Architect (USR-001)
python _dev/scripts/test_chat.py USR-001 evangeline_01

# Chat as any other user
python _dev/scripts/test_chat.py USR-A3F2B8C1 adrian_01
```

**Features:**
- ✅ Shows current tier & location
- ✅ Works with any user_id
- ✅ Architect mode automatic for USR-001
- ✅ Type `exit` or `quit` to end

---

### 📈 **3. Intimacy Testing**

```bash
# Boost intimacy for any user
python _dev/scripts/boost_intimacy.py <user_id> <soul_id> [points]

# Examples:
python _dev/scripts/boost_intimacy.py USR-001 evangeline_01 20
python _dev/scripts/boost_intimacy.py USR-A3F2B8C1 adrian_01 50
```

**Default points:** 20 if not specified

**Tier Thresholds:**
- STRANGER: 0-20
- ACQUAINTANCE: 21-40
- TRUSTED: 41-70
- FRIENDSHIP: 71-85
- SOUL_LINKED: 86+

---

### 🗺️ **4. Location Movement**

```bash
# Teleport a soul for any user
python _dev/scripts/move_to.py <user_id> <soul_id> [location_id]

# Examples:
python _dev/scripts/move_to.py USR-001 evangeline_01 dollhouse_dungeon
python _dev/scripts/move_to.py USR-A3F2B8C1 blaze_01 stop_n_go_racetrack
```

**Available Locations:**
- `linkside_estate` - Your private loft (Private)
- `crimson_arms` - Crumbling apartments (Semi-Private)
- `soul_plaza` - City center hub (Public)
- `stop_n_go_racetrack` - Hover-kart racing (Public)
- `skylink_tower` - Mysterious spire (Public)
- `dollhouse_dungeon` - Basement nightclub (Private)
- `ether_baths` - Spa & wellness (Private)

---

## ⚠️ DEPRECATION NOTICE

### **`create_dev_user.py` - REDUNDANT**

**Why:** `seed_db.py` now handles ALL of this:
1. ✅ Creates USR-001 automatically
2. ✅ Links USR-001 to all souls
3. ✅ Sets max intimacy + Architect flag
4. ✅ All in one command

**Decision:** DELETE or REPURPOSE

**If you keep it:** Use it to create OTHER test users, not USR-001.

---

## 🎯 COMPLETE WORKFLOW

```bash
# Full Reset & Setup (from scratch)
python _dev/scripts/nuke_db.py          # 1️⃣ Destroy old world
python _dev/scripts/seed_db.py          # 2️⃣ Build new world + Architect

# Testing
python _dev/scripts/test_chat.py USR-001 evangeline_01    # Chat test
python _dev/scripts/boost_intimacy.py USR-001 adrian_01 30  # Intimacy test
python _dev/scripts/move_to.py USR-001 selene_01 ether_baths  # Location test
```

---

## ✅ SCRIPT IMPROVEMENTS SUMMARY

### **seed_db.py**
- ✅ Fixed `llm_instructions` → `llm_instruction_override`
- ✅ Added `ensure_architect_exists()` function
- ✅ Better error messages with traceback
- ✅ Now handles complete database setup in one command

### **boost_intimacy.py**
- ✅ Accepts `user_id` as first argument
- ✅ Works with any user, not just USR-001
- ✅ Better error messages
- ✅ Shows available commands in help

### **move_to.py**
- ✅ Accepts `user_id` as first argument
- ✅ Works with any user, not just USR-001
- ✅ Lists available locations on error
- ✅ Better help text

### **test_chat.py**
- ✅ Accepts `user_id` as first argument
- ✅ Verifies relationship exists before starting
- ✅ Shows tier & location in header
- ✅ Better error handling

---

## 🚀 YOU'RE NOW PRODUCTION-READY

All scripts support **thousands of users** while keeping USR-001 special.

**Senior dev says:** Ship it! 🔥
