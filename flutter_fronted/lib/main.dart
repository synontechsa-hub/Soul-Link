import 'package:flutter/material.dart';
import 'navigation/main_scaffold.dart';
import 'state/app_session.dart';
import 'dev/seed_data.dart';

void main() {
  runApp(const SoulLinkApp());
}

class SoulLinkApp extends StatelessWidget {
  const SoulLinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    final session = AppSession();
    seedAppSession(session);

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SoulLink',
      theme: ThemeData.dark(),
      home: MainScaffold(session: session),
    );
  }
}
