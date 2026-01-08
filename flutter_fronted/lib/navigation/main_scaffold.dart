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

  // ─────────────────────────────────────────────
  // 🧠 NAVIGATION LOGIC & STATE INJECTION
  // ─────────────────────────────────────────────
  
  List<Widget> _buildScreens() {
    return [
      HomeScreen(session: widget.session),      // 🟢 Fixed: Parameter 'session' provided
      BrowseScreen(session: widget.session),    // 🟢 Fixed: Parameter 'session' provided
      const SizedBox(),                         // 🧪 Placeholder for FAB logic
      ChatHistoryScreen(session: widget.session),
      ProfileScreen(session: widget.session),   // 🟢 Fixed: Parameter 'session' provided
    ];
  }

  void _onTabTapped(int index) {
    // 🧠 GUARD: Do not navigate to the index reserved for the FAB notch
    if (index == 2) return; 
    
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final screens = _buildScreens();

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0C),

      // ─────────────────────────────────────────────
      // 📺 VIEWPORT (STATE PRESERVATION)
      // ─────────────────────────────────────────────
      
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      
      // ─────────────────────────────────────────────
      // 🔹 FLOATING ACTION BUTTON (SOUL CREATOR)
      // ─────────────────────────────────────────────
      
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: FloatingActionButton(
        elevation: 8,
        backgroundColor: Colors.blueAccent,
        onPressed: () {
          // Future: Open Bot Creation Wizard
          print("Initialize Soul Sequence...");
        },
        child: const Icon(Icons.add, color: Colors.white, size: 28),
      ),

      // ─────────────────────────────────────────────
      // ⚓ BOTTOM NAVIGATION BAR (DOCK)
      // ─────────────────────────────────────────────
      
      bottomNavigationBar: BottomAppBar(
        padding: EdgeInsets.zero,
        color: const Color(0xFF16161A),
        shape: const CircularNotchedRectangle(),
        notchMargin: 10.0,
        child: BottomNavigationBar(
          elevation: 0,
          backgroundColor: Colors.transparent, 
          currentIndex: _currentIndex,
          onTap: _onTabTapped,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: Colors.blueAccent,
          unselectedItemColor: Colors.white24,
          showSelectedLabels: false,
          showUnselectedLabels: false,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded), 
              label: "Home"
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.explore_rounded), 
              label: "Browse"
            ),
            BottomNavigationBarItem(
              icon: Icon(null), 
              label: "" // Empty slot for FAB Notch
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.chat_bubble_rounded), 
              label: "Inbox"
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded), 
              label: "Profile"
            ),
          ],
        ),
      ),
    );
  }
}