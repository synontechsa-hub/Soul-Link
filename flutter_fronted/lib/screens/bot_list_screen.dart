import 'package:flutter/material.dart';
import '../services/bot_loader.dart';
import '../models/bot.dart';
import 'chat_screen.dart';

class BotListScreen extends StatefulWidget {
  const BotListScreen({super.key});

  @override
  State<BotListScreen> createState() => _BotListScreenState();
}

class _BotListScreenState extends State<BotListScreen> {
  late Future<List<Bot>> botsFuture;

  @override
  void initState() {
    super.initState();
    botsFuture = BotLoader.loadBots();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E0E11), // Neutral-900
      appBar: AppBar(
        title: const Text("SoulLink Bots"),
        backgroundColor: const Color(0xFF181A1F), // Neutral-800
      ),
      body: FutureBuilder<List<Bot>>(
        future: botsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return const Center(child: Text("Error loading bots"));
          } else {
            final bots = snapshot.data!;
            return ListView.builder(
              itemCount: bots.length,
              itemBuilder: (context, index) {
                final bot = bots[index];
                return Card(
                  color: const Color(0xFF181A1F),
                  child: ListTile(
                    title: Text(
                      bot.name,
                      style: const TextStyle(color: Colors.white),
                    ),
                    subtitle: Text(
                      bot.archetype,
                      style: const TextStyle(color: Colors.grey),
                    ),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => ChatScreen(bot: bot)),
                      );
                    },
                  ),
                );
              },
            );
          }
        },
      ),
    );
  }
}
