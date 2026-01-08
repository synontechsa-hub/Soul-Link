import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app.dart';
import 'state/app_session.dart';
import 'dev/seed_data.dart';

// ─────────────────────────────────────────────
// 🏗️ APPLICATION ENTRY POINT
// ─────────────────────────────────────────────

void main() async {
  // 1. Ensure Flutter bindings are initialized for async asset loading
  WidgetsFlutterBinding.ensureInitialized();

  // 2. Initialize the Core Session
  final session = AppSession();

  // 3. Load the Soul Roster (The 30+ bots)
  // We call this before runApp so the data is ready the moment the screen draws
  await seedAppSession(session);

  runApp(
    // 4. Wrap the app in ChangeNotifierProvider
    // This allows Echo, Nova, and Evangeline to be "found" by any widget
    ChangeNotifierProvider<AppSession>.value(
      value: session,
      child: const SoulLinkApp(),
    ),
  );
}