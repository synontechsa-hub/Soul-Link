import 'package:flutter/material.dart';
import '../models/bot.dart';
import 'chat_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Placeholder recommended bot
    final Bot recommendedBot = Bot(
      name: "Arael",
      archetype: "Empathic Guide",
      description: "Helps users explore emotional depth and personal growth through conversation.",
    );

    return Scaffold(
      backgroundColor: const Color(0xFF0E0E11), // Neutral-900
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 16),
            // SoulLink logo
            SizedBox(
              height: 120,
              child: Image.asset(
                'assets/ui_ux/soullink_logo.png', // Add your mascot image here
                fit: BoxFit.contain,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              "Welcome to SoulLink",
              style: TextStyle(
                fontSize: 20,
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 24),
            // Recommended bot card
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 24),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF181A1F), // Neutral-800
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    recommendedBot.name,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF7E57C2), // Purple-500
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    recommendedBot.archetype,
                    style: const TextStyle(
                      fontSize: 16,
                      color: Color(0xFFB39DDB), // Purple-300
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    recommendedBot.description,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Color(0xFFF2F3F6), // Neutral-100
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFE53935), // Red-500
                      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ChatScreen(bot: recommendedBot),
                        ),
                      );
                    },
                    child: const Text("Chat Now", style: TextStyle(color: Colors.white)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}