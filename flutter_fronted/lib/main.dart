import 'package:flutter/material.dart';
import 'app.dart';
import 'state/app_session.dart';
import 'main_scaffold.dart';

void main() {
  runApp(const SoulLinkApp());
}

class SoulLinkApp extends StatelessWidget {
  const SoulLinkApp({super.key});

  @override
  Widget build(BuildContext context) {
    final session = AppSession();

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SoulLink',
      theme: ThemeData.dark(),
      home: MainScaffold(session: session),
    );
  }
}
