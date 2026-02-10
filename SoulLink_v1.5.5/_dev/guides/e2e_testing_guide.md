# 🧪 End-to-End Testing Guide (Task 23)

## Prerequisites ✅

- [x] Backend server running on `http://127.0.0.1:8000`
- [ ] Flutter app ready to run
- [ ] Supabase credentials in `.env`

---

## Test Suite

### Test 1: WebSocket Connection 🔌

**Objective**: Verify WebSocket auto-connects on login

**Steps**:

1. Run the Flutter app: `flutter run` (in `frontend/` directory)
2. Log in with your Supabase credentials
3. **Check console output** for:

   ```
   🔌 WebSocket: Connecting to ws://127.0.0.1:8000/api/v1/ws
   ✅ WebSocket: Connected
   ```

**Expected Result**:

- ✅ Console shows successful connection
- ✅ No error messages

**If it fails**:

- Check backend logs for WebSocket connection attempts
- Verify JWT token is being sent (check `🔑 API Call with Token:` in console)

---

### Test 2: Real-Time Chat Messages 💬

**Objective**: Verify messages arrive via WebSocket (not HTTP polling)

**Steps**:

1. Navigate to the **Dashboard** (LINKS tab)
2. Tap on any linked soul to open chat
3. Send a message: "Hello, testing WebSocket!"
4. **Watch the console** for:

   ```
   📨 WebSocket Message: chat_message
   ```

**Expected Result**:

- ✅ Soul's response appears **instantly** (no delay)
- ✅ Console shows `📨 WebSocket Message: chat_message`
- ✅ Intimacy score updates in real-time (progress bar animates)
- ✅ Location updates if soul mentions moving

**If it fails**:

- Check if WebSocket is still connected
- Look for `❌ WebSocket Error:` in console
- Verify backend sent the message (check backend logs)

---

### Test 3: WebSocket Reconnection 🔄

**Objective**: Verify auto-reconnect works

**Steps**:

1. While in a chat, **restart the backend server**:
   - Stop: `Ctrl+C` in backend terminal
   - Start: `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`
2. **Watch the console** for:

   ```
   🔌 WebSocket: Disconnected
   🔄 WebSocket: Reconnecting in 2s (attempt 1)
   ✅ WebSocket: Connected
   ```

3. Send another message

**Expected Result**:

- ✅ App reconnects automatically within 2-10 seconds
- ✅ Messages work after reconnection
- ✅ No manual refresh needed

---

### Test 4: Error Handling UI 🚨

**Objective**: Verify user-friendly error messages

**Steps**:

1. **Test 401 (Session Expired)**:
   - Manually sign out from Supabase (or wait for token to expire)
   - Try to send a message
   - **Expected**: Red toast: "🔐 Session expired. Please log in again."

2. **Test 429 (Rate Limit)**:
   - Send 10+ messages rapidly
   - **Expected**: Orange toast: "⏳ Too many requests. Please slow down."

3. **Test Network Error**:
   - Turn off Wi-Fi or disconnect network
   - Try to send a message
   - **Expected**: Red toast: "📡 Connection lost. Check your internet."

**Expected Result**:

- ✅ All errors show user-friendly messages (not raw HTTP codes)
- ✅ Toasts appear at bottom of screen
- ✅ Can dismiss with "DISMISS" button

---

### Test 5: Heartbeat (Connection Keep-Alive) 💓

**Objective**: Verify connection stays alive during idle time

**Steps**:

1. Open a chat screen
2. **Wait 2 minutes** without sending any messages
3. After 2 minutes, send a message

**Expected Result**:

- ✅ Message sends successfully (no reconnection needed)
- ✅ Console shows periodic heartbeat (every 30s):

   ```
   (No visible output, but connection stays alive)
   ```

**If it fails**:

- Connection might have timed out
- Check for `🔌 WebSocket: Disconnected` in console

---

### Test 6: Multiple Souls (Isolation) 👥

**Objective**: Verify WebSocket messages are routed correctly

**Steps**:

1. Link with at least 2 souls (use Explore screen)
2. Open chat with **Soul A**
3. Send a message
4. Navigate back and open chat with **Soul B**
5. Send a message

**Expected Result**:

- ✅ Each chat only shows messages for that specific soul
- ✅ No message leakage between chats
- ✅ Console shows correct `soul_id` in WebSocket messages

---

## Quick Verification Checklist

Run through this quickly to verify everything works:

- [ ] Login → WebSocket connects automatically
- [ ] Send message → Response arrives via WebSocket
- [ ] Restart backend → App reconnects automatically
- [ ] Send invalid request → User-friendly error toast
- [ ] Wait 2 minutes idle → Connection stays alive
- [ ] Switch between souls → Messages isolated correctly

---

## Console Output Reference

### ✅ Good Signs

```
🔌 WebSocket: Connecting to ws://127.0.0.1:8000/api/v1/ws
✅ WebSocket: Connected
📨 WebSocket Message: chat_message
🔑 API Call with Token: eyJhbGciOi...
```

### ❌ Bad Signs

```
❌ WebSocket Connection Error: [Errno 111] Connection refused
❌ WebSocket: Max reconnect attempts reached
❌ WebSocket Parse Error: ...
```

---

## Backend Logs to Monitor

While testing, keep an eye on the backend terminal for:

```
INFO: WebSocket connection accepted
INFO: WebSocket message received: {'type': 'ping'}
INFO: WebSocket message sent: {'type': 'pong'}
INFO: WebSocket connection closed
```

---

## Next Steps After Testing

Once all tests pass:

- [ ] Mark Task 23 as complete in `task.md`
- [ ] Update `walkthrough.md` with test results
- [ ] Proceed to Task 24: Security Audit

---

## Troubleshooting

### WebSocket won't connect

1. Check backend is running: `curl http://127.0.0.1:8000/api/v1/health`
2. Verify JWT token is valid (check Supabase dashboard)
3. Check firewall isn't blocking WebSocket connections

### Messages not arriving in real-time

1. Check WebSocket is connected (look for `✅ WebSocket: Connected`)
2. Verify backend is sending WebSocket messages (check backend logs)
3. Try restarting the app

### Error toasts not showing

1. Check `error_toast.dart` is imported in the screen
2. Verify `ErrorToast.show()` is being called in catch blocks
3. Check console for any Flutter rendering errors
