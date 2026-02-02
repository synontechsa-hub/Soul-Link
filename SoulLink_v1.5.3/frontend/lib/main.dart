// frontend/lib/main.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart'; // 1. Add this import
import 'providers/dashboard_provider.dart';
import 'services/api_service.dart';
import 'screens/dashboard_screen.dart';
import 'screens/explore_screen.dart';
import 'screens/map_screen.dart';

// 2. Change main to be async
void main() async {
  // 3. Essential magic line for async initialization
  WidgetsFlutterBinding.ensureInitialized();

  // 4. Load the environment file
  try {
    await dotenv.load(fileName: ".env");
    print("✅ Link City Environment Loaded");
  } catch (e) {
    print("❌ Critical Error: Could not load .env file. Check if it exists in frontend root!");
  }

  runApp(const LinkCityApp());
}

class LinkCityApp extends StatelessWidget {
  const LinkCityApp({super.key});

  @override
  Widget build(BuildContext context) {
    // API Service will now be able to read the URL from .env properly
    final apiService = ApiService(userId: "USR-001");

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => DashboardProvider(apiService)..syncDashboard(),
        ),
      ],
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark().copyWith(
          scaffoldBackgroundColor: const Color(0xFF0A0A0E),
          // Cleaned up the navigation bar colors while we're at it
          bottomNavigationBarTheme: const BottomNavigationBarThemeData(
            selectedItemColor: Colors.cyanAccent,
            unselectedItemColor: Colors.white24,
            backgroundColor: Color(0xFF1A1A22),
          ),
        ),
        home: const MainNavigationShell(),
      ),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DashboardScreen(),
    const ExploreScreen(),
    const MapScreen(),
    const Center(child: Text("APARTMENT COMING SOON")), // Placeholder if file missing
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.hub), label: "LINKS"),
          BottomNavigationBarItem(icon: Icon(Icons.radar), label: "EXPLORE"),
          BottomNavigationBarItem(icon: Icon(Icons.map), label: "CITY"),
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "ME"),
        ],
      ),
    );
  }
}