import 'package:flutter/material.dart';
import '../state/app_session.dart';
import '../screens/home/home_screen.dart';
import '../screens/browse/browse_screen.dart';
import '../screens/chats/chat_history_screen.dart';
import '../screens/profile/profile_screen.dart';

// ─────────────────────────────────────────────
// 🏗️ MAIN NAVIGATION SCAFFOLD
// ─────────────────────────────────────────────

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

  // 🧠 NAVIGATION LOGIC
  // We remove 'late final' and use a getter or rebuild logic 
  // to ensure ChatHistoryScreen always has the freshest session data.
  List<Widget> _buildScreens() {
    return [
      const HomeScreen(),
      const BrowseScreen(),
      const SizedBox(), // 🧪 Placeholder for "Create Bot" FAB
      ChatHistoryScreen(session: widget.session),
      const ProfileScreen(),
    ];
  }

  void _onTabTapped(int index) {
    // 🧠 NAVIGATION GUARD: Prevent switching to the empty spacer
    if (index == 2) return; 
    
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final screens = _buildScreens();

    return Scaffold(
      // 🧠 STATE PRESERVATION: IndexedStack keeps the scroll 
      // position of your chat history alive even when you switch tabs.
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      
      // ─────────────────────────────────────────────
      // 🔹 FLOATING ACTION BUTTON (CENTRAL HUB)
      // ─────────────────────────────────────────────
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Future: Logic to create a new bot/conversation
          print("Create Bot Tapped");
        },
        child: const Icon(Icons.add),
      ),

      // ─────────────────────────────────────────────
      // ⚓ BOTTOM NAVIGATION BAR
      // ─────────────────────────────────────────────
      bottomNavigationBar: BottomAppBar(
        shape: const CircularNotchedRectangle(),
        notchMargin: 8.0,
        child: BottomNavigationBar(
          elevation: 0, // Remove shadow as BottomAppBar handles it
          backgroundColor: Colors.transparent, 
          currentIndex: _currentIndex,
          onTap: _onTabTapped,
          type: BottomNavigationBarType.fixed,
          showSelectedLabels: false,
          showUnselectedLabels: false,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: "Home"),
            BottomNavigationBarItem(icon: Icon(Icons.explore_rounded), label: "Browse"),
            BottomNavigationBarItem(icon: Icon(null), label: ""), // Space for FAB
            BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_rounded), label: "Chats"),
            BottomNavigationBarItem(icon: Icon(Icons.person_rounded), label: "Profile"),
          ],
        ),
      ),
    );
  }
}