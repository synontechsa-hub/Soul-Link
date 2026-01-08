import 'package:flutter/material.dart';

import 'navigation/main_scaffold.dart';
import 'screens/login_screen.dart';

class SoulLinkApp extends StatelessWidget {
  const SoulLinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "SoulLink",
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0E0E11),
        primaryColor: const Color(0xFFE53935),
      ),
      home: const LoginScreen(),
      // later this becomes MainScaffold() after login
    );
  }
}
