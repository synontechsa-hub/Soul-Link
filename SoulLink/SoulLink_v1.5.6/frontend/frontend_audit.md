# Frontend Code Audit — SoulLink / Legion Engine
**Version:** v1.5.6 Normandy SR-2  
**Stack:** Flutter / Dart, Provider, Supabase Auth, WebSocket  
**Date:** 2026-03-13  
**Files Reviewed:** 34 Dart files + pubspec, analysis output, flutter error logs

---

## Summary

| Severity | Count |
|---|---|
| 🔴 Critical (crash / data leak) | 4 |
| 🟠 Serious (logic bugs / broken features) | 6 |
| 🟡 Performance / UX issues | 5 |
| 🔵 Dead code / lint violations | 6 |

---

## 🔴 Critical Issues

### 1. `.env` File Bundled as a Flutter Asset — Secrets Shipped in the APK/IPA

**File:** `pubspec.yaml`, `lib/main.dart`

```yaml
flutter:
  assets:
    - .env  # Dev only — swap for --dart-define in production builds
```

The comment says "Dev only — swap for --dart-define in production builds" but this **has not been done**. The `.env` file (containing `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and potentially `API_BASE_URL`) is baked directly into every release build. Anyone who unpacks the APK or IPA with standard tools can read all of these values.

**Fix:** Remove `.env` from `pubspec.yaml` assets before any release build. Use `--dart-define` at build time instead:

```bash
flutter build apk \
  --dart-define=SUPABASE_URL=https://xyz.supabase.co \
  --dart-define=SUPABASE_ANON_KEY=your_key \
  --dart-define=API_BASE_URL=https://api.yourdomain.com
```

Then update `AppConfig` to read from compile-time constants:
```dart
static const String supabaseUrl = String.fromEnvironment('SUPABASE_URL');
```

---

### 2. `unused_local_variable 'soulId'` Warning in `chat_screen.dart` — Silent Data Loss

**File:** `lib/screens/chat_screen.dart:60`  
**Lint:** `warning - unused_local_variable`

The flutter analyzer flagged this as a **warning** (not just info), which means a variable is declared and assigned but its value is never used. This is a signal that something that *should* be happening (e.g. filtering WebSocket messages by soul ID, or including soulId in an API call) simply isn't. The WebSocket subscription in `_subscribeToWebSocket()` is also entirely commented out — so real-time chat responses are completely disabled. Messages only arrive via HTTP polling.

**Fix:** Either restore the WebSocket real-time message path properly (being careful to deduplicate with the HTTP response), or remove the dead variable and the commented block entirely if HTTP-only is the intent.

---

### 3. `BuildContext` Used Across Async Gaps Without Proper Guard — `apartment_screen.dart`

**File:** `lib/screens/apartment_screen.dart:164, 176, 337`  
**Lint:** `use_build_context_synchronously`

Three locations use `context` (for `ScaffoldMessenger`, `Navigator`, etc.) after `await` calls without being properly guarded by `if (!mounted) return`. Flutter's linter flags these as `info` warnings but they can cause crashes in practice — if the widget is unmounted while an async call is in-flight, accessing `context` will throw.

The existing `if (!mounted) return` guards in this file are present in some places but missing in others. Similarly flagged in `map_screen.dart:99`.

**Fix:** Add `if (!mounted) return;` immediately after every `await` before any `context` usage:
```dart
await provider.apiService.advanceTimeSlot();
if (!mounted) return;  // ← add this
ScaffoldMessenger.of(context).showSnackBar(...);
```

---

### 4. `getAllTimeSlots()` Makes Unauthenticated Request — No Auth Headers

**File:** `lib/services/api_service.dart`

```dart
Future<List<dynamic>> getAllTimeSlots() async {
  final response = await http.get(Uri.parse("$baseUrl/time/slots"));
  // ↑ No headers passed — completely unauthenticated
```

Every other `http.get` call in `ApiService` passes `headers: _headers` which injects the Bearer token. This one doesn't. If the backend endpoint requires auth (which it likely does now), this will silently return a 401 and throw an unhandled exception. If it doesn't require auth, it's inconsistent and leaks endpoint information.

**Fix:**
```dart
final response = await http.get(
  Uri.parse("$baseUrl/time/slots"),
  headers: _headers,  // ← add this
);
```

---

## 🟠 Serious Issues

### 5. Unused Import in `explore_screen.dart` — Dead Dependency on `flutter_dotenv`

**File:** `lib/screens/explore_screen.dart:6`  
**Lint:** `warning - unused_import`

```dart
import 'package:flutter_dotenv/flutter_dotenv.dart';  // ← never used
```

`ExploreScreen` doesn't use `dotenv` at all. This was almost certainly a copy-paste artifact. It's a warning (not just info), indicating the analyzer treated it with higher priority. Safe to delete immediately.

---

### 6. `isConnected` Check Is Wrong in `WebSocketService` — Reports `true` While Disconnected

**File:** `lib/services/websocket_service.dart`

```dart
bool get isConnected => _channel != null;
```

`_channel` is set to the `WebSocketChannel` immediately on connection attempt, *before* the handshake completes and *before* any confirmation from the server. This means `isConnected` reports `true` the instant `connect()` is called, even if the server rejects the connection or the handshake fails.

This causes `WebSocketProvider` to tell `main.dart` the connection is live when it may not be, suppressing the reconnect UI and any error state.

**Fix:** Add an explicit `_isConnected` boolean that is only set to `true` on successful handshake acknowledgement from the server (i.e. when the server sends back a `connected` or `handshake_ok` event):
```dart
bool _isConnected = false;
bool get isConnected => _isConnected;

// In _handleMessage:
if (data['type'] == 'connected') {
  _isConnected = true;
  onConnectionStateChanged?.call();
}
```

---

### 7. `portrait_url` Snake_case Field in a Dart Model

**File:** `lib/models/relationship.dart:17, 32`  
**Lint:** `non_constant_identifier_names` (flagged twice)

```dart
final String portrait_url;  // ← violates Dart naming conventions
```

Dart convention (and the `non_constant_identifier_names` lint rule) requires `portraitUrl`. While this is cosmetic, it's flagged because it can cause issues with code generation tools and reflects a lack of consistency — every other field in the model uses camelCase. It's also referenced as `soulsHere[i].portrait_url` in `map_screen.dart` which propagates the naming violation.

**Fix:** Rename to `portraitUrl` throughout.

---

### 8. `RegistrationScreen` Uses Anonymous Sign-In Instead of Actual Registration

**File:** `lib/screens/registration_screen.dart`

The registration flow calls `authService.signInAnonymously()` and then updates the profile. This means "registering" creates a guest account and slaps a username on it — not a real email-backed account. There's no email/password collection in the registration form at all.

This is probably intentional during development, but it means a "registered" user's account can't be recovered if they clear app data — it's functionally identical to guest login.

**Fix:** Either rename this screen to `GuestSetupScreen` to reflect what it actually does, or add the email/password fields and route through `authService.signUpWithEmail()`. The `AuthService` already has `signUpWithEmail` implemented and waiting.

---

### 9. `_openChat()` in `ExploreScreen` — Infinite Recursion Risk

**File:** `lib/screens/explore_screen.dart`

```dart
void _openChat(Map<String, dynamic> soulData) {
  // ...
  provider.syncDashboard().then((_) => _openChat(soulData));  // ← recursive call
}
```

If the dashboard syncs successfully but the soul *still* isn't in `activeSouls` (e.g. because the link API call failed silently, or the dashboard response format changed), this calls `_openChat()` again, which syncs the dashboard again, which calls `_openChat()` again. There's no recursion limit or guard, so it will loop until the user navigates away or the app runs out of memory.

**Fix:** Add a retry guard:
```dart
void _openChat(Map<String, dynamic> soulData, {bool isRetry = false}) {
  // ...
  if (relationship == null) {
    if (isRetry) {
      // Show snackbar: "Failed to open channel"
      return;
    }
    provider.syncDashboard().then((_) => _openChat(soulData, isRetry: true));
  }
}
```

---

### 10. `DashboardProvider.syncDashboard()` Calls `refreshUser()` Twice

**File:** `lib/providers/dashboard_provider.dart`

```dart
Future<void> syncDashboard() async {
  await Future.wait([
    refreshUser(),                              // ← GET /users/me
    apiService.getDashboard().then(...)
  ]);
}
```

`initAfterAuth()` calls `refreshUser()` first, then `syncDashboard()` — which calls `refreshUser()` again. So on every app start there are two consecutive `GET /users/me` requests. Additionally, the dashboard endpoint likely returns user data too (it returns `user_id`, `username`, `display_name`), making one of these `refreshUser()` calls redundant.

**Fix:** Remove the standalone `refreshUser()` call from `initAfterAuth()` since `syncDashboard()` already calls it, or restructure so `syncDashboard()` only calls `refreshUser()` when explicitly needed.

---

## 🟡 Performance & UX Issues

### 11. Memory Wall Uses `FutureBuilder` Inside a `ListView` — N Simultaneous API Calls

**File:** `lib/screens/apartment_screen.dart` — `_showMemoryWallDialog()`

```dart
ListView.builder(
  itemCount: souls.length,
  itemBuilder: (context, idx) {
    return FutureBuilder<Map<String, dynamic>>(
      future: api.getSoulMemories(soul.soulId),  // ← N calls, one per soul
```

When the Memory Wall opens, it immediately fires one `GET /souls/{id}/memories` request for *every linked soul*, all in parallel. For a user with 10+ linked souls, this floods the backend and creates visible jank. `FutureBuilder` inside a `ListView.builder` also re-fires the future every time the item scrolls off and back into view.

**Fix:** Load all memories upfront in a single `initState`-style call before showing the bottom sheet, or batch the requests. At minimum, store the future in a variable outside the builder so it doesn't re-execute on scroll.

---

### 12. `withOpacity()` Deprecated — Used 3 Times in `apartment_screen.dart`

**File:** `lib/screens/apartment_screen.dart:60, 67, 74`  
**Lint:** `deprecated_member_use`

```dart
Colors.red.withOpacity(0.1)  // ← deprecated in Flutter 3.x
```

**Fix:**
```dart
Colors.red.withValues(alpha: 0.1)  // ← correct modern API
```

Also present in `map_screen.dart` (`Colors.cyanAccent.withOpacity(0.2)`). Do a project-wide find-replace on `.withOpacity(` → `.withValues(alpha: `.

---

### 13. `print()` Used Throughout in Production Code — 15+ Violations

**Files:** `lib/main.dart`, `lib/providers/websocket_provider.dart`, `lib/services/websocket_service.dart`, `lib/services/ad_service.dart`  
**Lint:** `avoid_print`

`print()` is not controllable by log level and will appear in production console output. Specific instances:
- `main.dart:31, 33` — startup status
- `websocket_provider.dart:47, 73` — WebSocket event logging
- `websocket_service.dart` — multiple connection/message logs
- `ad_service.dart` — ad lifecycle logs

**Fix:** Replace all `print()` calls with `debugPrint()` (which is automatically a no-op in release builds) or use a proper logging package like `logger`.

---

### 14. `ApiService` Has No Timeout Configuration

**File:** `lib/services/api_service.dart`

Every `http.get` and `http.post` call uses the default `http` package timeout, which is essentially unlimited. If the backend is slow or unreachable, these calls will hang indefinitely — blocking `isLoading` spinners and the dashboard init forever.

**Fix:** Add a timeout to all requests:
```dart
final response = await http.get(
  Uri.parse("$baseUrl/sync/dashboard"),
  headers: _headers,
).timeout(const Duration(seconds: 15));
```

---

### 15. `didChangeDependencies` in `MapScreen` Has Empty Body

**File:** `lib/screens/map_screen.dart`

```dart
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  final provider = Provider.of<DashboardProvider>(context);
  final user = provider.currentUser;
  if (user != null && !_isLoadingLocs) {
    // Check if we need to refresh (implement more precise checking if needed)
    // For now, if the user state changed, we might want to refresh
  }
}
```

This override exists, calls `Provider.of` (causing this widget to rebuild on *every* `DashboardProvider` notification), and then does nothing. The empty `if` block and the comment indicate it was planned but abandoned. Since it listens to `DashboardProvider` without listening = false, it forces a full rebuild of `MapScreen` on every provider update for no reason.

**Fix:** Remove this `didChangeDependencies` override entirely until the refresh logic is implemented. If the rebuild is needed, use `context.select()` to be specific about what triggers it.

---

## 🔵 Dead Code & Lint Violations

### 16. Entire WebSocket Message Handler Is Commented Out in `ChatScreen`

**File:** `lib/screens/chat_screen.dart`

```dart
wsProvider.onChatMessage = (data) {
  // DISABLED: Prevent duplicate messages
  // Only process messages for this soul
  // if (soulId == widget.relationship.soulId && mounted) {
  //   setState(() { ... });
  //   _scrollToBottom();
  // }
};
```

The entire handler body is commented out, leaving an empty lambda. Real-time chat via WebSocket is completely non-functional — all messages arrive via HTTP only. The soul ID variable extracted just above this block (`final soulId = data['soul_id']`) is the `unused_local_variable` warning from the analyzer. This is fine if intentional, but the dead code should be cleaned up.

---

### 17. `Soul` Model Is Defined But Never Used

**File:** `lib/models/soul.dart`

The `Soul` class exists with a `fromJson` factory, but nothing in the frontend imports or uses it. The explore/chat flows use raw `Map<String, dynamic>` throughout. This is the frontend mirror of the backend's dead model problem.

**Fix:** Either start using it properly in `ExploreScreen` (which currently passes raw maps to `ExploreSoulCard`) or delete it.

---

### 18. `RegistrationScreen` Is Imported in `login_screen.dart` But Never Used

**File:** `lib/screens/login_screen.dart`

There is no navigation from `LoginScreen` to `RegistrationScreen` — the "Register" button is listed as a placeholder or was removed. The screen exists but is unreachable from the app's navigation flow.

---

### 19. `prefer_const_constructors` — Multiple Violations

**Files:** `lib/screens/dashboard_screen.dart:45, 46`, `lib/screens/login_screen.dart:149`  
**Lint:** `prefer_const_constructors`, `prefer_const_literals_to_create_immutables`

Widgets that could be `const` are not marked as such, preventing Flutter from skipping unnecessary rebuilds. Minor, but easy to fix with `dart fix --apply`.

---

### 20. `AppConfig` Version Comment Is Stale

**File:** `lib/core/config.dart:3`

```dart
// Environment configuration for SoulLink v1.5.5
```

The app is on v1.5.6. Minor, but if version comments are being maintained they should be accurate.

---

### 21. `curly_braces_in_flow_control_structures` — Multiple Violations

**Files:** `lib/screens/apartment_screen.dart:578, 581, 584`, `lib/screens/chat_screen.dart:384, 386`, `lib/screens/map_screen.dart:81`

```dart
if (time.contains("MORNING"))
  description = "...";  // ← no curly braces
```

All `if` statements without braces. Not a crash risk but a maintenance hazard — easy to accidentally add a second line and have it not be part of the `if`. Run `dart fix --apply` to auto-fix.

---

## Files Safe to Delete / Clean Up

| File | Reason |
|---|---|
| `lib/models/soul.dart` | `Soul` model never imported or used anywhere |
| `analysis_output.txt` | UTF-16 encoded duplicate of `analysis_output_utf8.txt` |
| `analysis_output_plain.txt` | Another duplicate of the analysis output |
| `flutter_errors.txt` | UTF-16 encoded duplicate of `flutter_errors_utf8.txt` |
| `trace.txt` | PowerShell error trace from a dev run — not source code |
| `env_dump.txt` | Windows environment variable dump from a dev run — **contains system paths, should not be in the repo** |

---

## Recommended Fix Priority

1. **Remove `.env` from pubspec assets** — this is a security issue that affects every release build
2. **Fix `getAllTimeSlots()` missing auth headers** — silent 401 failures
3. **Fix `BuildContext` async gaps** — potential crashes in apartment and map screens
4. **Fix `isConnected` WebSocket race condition** — false positive connection state
5. **Add HTTP timeouts to `ApiService`** — prevents infinite loading states
6. **Fix recursive `_openChat()` in ExploreScreen** — potential infinite loop
7. **Remove double `refreshUser()` in `initAfterAuth()`** — unnecessary double API call
8. **Fix Memory Wall `FutureBuilder` in ListView** — N simultaneous API calls on open
9. **Replace all `withOpacity()` with `withValues(alpha:)`** — deprecated API
10. **Replace all `print()` with `debugPrint()`** — production noise and lint warnings
11. **Rename `portrait_url` → `portraitUrl`** — Dart naming convention
12. **Delete dead log/env dump files from repo** — especially `env_dump.txt`
