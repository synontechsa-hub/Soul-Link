import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'state/app_session.dart';
import 'navigation/main_scaffold.dart';
import 'screens/login_screen.dart';

// ─────────────────────────────────────────────
// 🏗️ MAIN APPLICATION BOILERPLATE
// ─────────────────────────────────────────────

class SoulLinkApp extends StatelessWidget {
  const SoulLinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    // We access the session via Provider so all 30 bots are available everywhere
    final session = Provider.of<AppSession>(context);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "SoulLink",
      
      // 🎨 SOUL LINK DARK THEME
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0A0A0C), // Deep space black
        primaryColor: Colors.blueAccent,
        hintColor: Colors.blueAccent,
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0A0A0C),
          elevation: 0,
        ),
      ),

      // 🚦 NAVIGATION LOGIC
      // If user is null, show Login. If logged in, show the Scaffold with the bots.
      home: session.currentUser == null 
        ? const LoginScreen() 
        : MainScaffold(session: session),
    );
  }
}