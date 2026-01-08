import 'package:flutter/material.dart';
import '../state/app_session.dart';
import '../screens/home/home_screen.dart';
import '../screens/browse/browse_screen.dart';
import '../screens/chats/chat_history_screen.dart';
import '../screens/profile/profile_screen.dart';

class MainScaffold extends StatefulWidget {
  final AppSession session;

  const MainScaffold({
    super.key,
    required this.session,
  });

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int _currentIndex = 0;

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();

    _screens = [
      const HomeScreen(),
      const BrowseScreen(),
      const SizedBox(), // spacer for future Create Bot
      ChatHistoryScreen(session: widget.session),
      const ProfileScreen(),
    ];
  }

  void _onTabTapped(int index) {
    if (index == 2) return; // ignore center for now
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: ""),
          BottomNavigationBarItem(icon: Icon(Icons.explore), label: ""),
          BottomNavigationBarItem(icon: SizedBox(width: 24), label: ""),
          BottomNavigationBarItem(icon: Icon(Icons.chat_bubble), label: ""),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: ""),
        ],
      ),
    );
  }
}
