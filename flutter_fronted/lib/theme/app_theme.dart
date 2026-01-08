import 'package:flutter/material.dart';

class AppTheme {
  static const Color accentPink = Color(0xFFFF4D8D);
  static const Color darkBackground = Color(0xFF000000);
  static const Color cardBackground = Color(0xFF1A1A1A);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: darkBackground,
      primaryColor: accentPink,
      cardColor: cardBackground,
      colorScheme: const ColorScheme.dark(
        primary: accentPink,
        secondary: accentPink,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: darkBackground,
        selectedItemColor: accentPink,
        unselectedItemColor: Colors.grey,
        showSelectedLabels: false,
        showUnselectedLabels: false,
      ),
    );
  }
}
