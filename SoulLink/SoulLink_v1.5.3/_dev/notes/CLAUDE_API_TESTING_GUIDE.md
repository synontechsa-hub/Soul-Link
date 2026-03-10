# API Testing Guide - SoulLink Phoenix v1.5.3

## 🔥 Updated Endpoints (No More Hardcoded USR-001!)

All endpoints now use **header-based authentication**:
```
X-User-Id: <your_user_id>
```

---

## 1️⃣ USER REGISTRATION

### Register New User
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "JohnDoe",
    "display_name": "John"
  }'
```

**Response:**
```json
{
  "status": "registered",
  "user_id": "USR-A3F2B8C1",
  "username": "JohnDoe",
  "message": "Welcome to Link City! Save your user_id for future logins."
}
```

**💡 SAVE YOUR user_id! You'll need it for all future requests.**

---

### Get Your Profile
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "X-User-Id: USR-A3F2B8C1"
```

---

## 2️⃣ SOUL DISCOVERY

### Browse All Souls (No Auth Required)
```bash
curl http://localhost:8000/api/v1/souls/explore
```

### Get Soul Details
```bash
curl http://localhost:8000/api/v1/souls/evangeline_01
```

---

## 3️⃣ LINKING WITH SOULS

### Link with a Soul (Required Before Chat)
```bash
curl -X POST http://localhost:8000/api/v1/souls/evangeline_01/link \
  -H "X-User-Id: USR-A3F2B8C1"
```

**Response:**
```json
{
  "status": "linked",
  "soul_id": "evangeline_01",
  "soul_name": "Evangeline",
  "message": "You've established a link with Evangeline. Your journey begins..."
}
```

### Check Relationship Status
```bash
curl http://localhost:8000/api/v1/souls/evangeline_01/relationship \
  -H "X-User-Id: USR-A3F2B8C1"
```

---

## 4️⃣ CHATTING

### Send Message
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-Id: USR-A3F2B8C1" \
  -d '{
    "soul_id": "evangeline_01",
    "message": "Hello, Eva!"
  }'
```

### Get Chat History
```bash
curl "http://localhost:8000/api/v1/chat/history?soul_id=evangeline_01&limit=20" \
  -H "X-User-Id: USR-A3F2B8C1"
```

---

## 5️⃣ LOCATION MOVEMENT

### Move Soul to New Location
```bash
curl -X POST "http://localhost:8000/api/v1/map/move?soul_id=evangeline_01&location_id=stop_n_go_racetrack" \
  -H "X-User-Id: USR-A3F2B8C1"
```

---

## 🔧 DEV USER (Architect Mode)

If you're the developer (USR-001), you can still use your special ID:

```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -H "X-User-Id: USR-001" \
  -d '{
    "soul_id": "evangeline_01",
    "message": "Hey Eva, I am your creator!"
  }'
```

**Eva will recognize you as The Architect** and respond differently!

---

## 📱 FRONTEND INTEGRATION

Your frontend should:
1. **Register user** → Store `user_id` locally
2. **Include header** in all API calls: `X-User-Id: <stored_user_id>`
3. **Link with souls** before attempting to chat

Example JavaScript:
```javascript
// Store user_id after registration
localStorage.setItem('user_id', 'USR-A3F2B8C1');

// Use in all API calls
const response = await fetch('http://localhost:8000/api/v1/chat/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-User-Id': localStorage.getItem('user_id')
  },
  body: JSON.stringify({
    soul_id: 'evangeline_01',
    message: 'Hello!'
  })
});
```

---

## ✅ NEW ENDPOINTS SUMMARY

| Endpoint | Method | Auth? | Purpose |
|----------|--------|-------|---------|
| `/users/register` | POST | ❌ | Create account |
| `/users/me` | GET | ✅ | Get profile |
| `/souls/explore` | GET | ❌ | Browse souls |
| `/souls/{id}` | GET | ❌ | Soul details |
| `/souls/{id}/link` | POST | ✅ | Initialize relationship |
| `/souls/{id}/relationship` | GET | ✅ | Check status |
| `/chat/send` | POST | ✅ | Send message |
| `/chat/history` | GET | ✅ | Get history |
| `/map/move` | POST | ✅ | Move location |

**Auth = ✅** means include `X-User-Id` header

---

## 🚀 READY TO SCALE TO THOUSANDS OF USERS!
