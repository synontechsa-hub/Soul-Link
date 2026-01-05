import 'package:flutter/material.dart';
import '../widgets/chat_bubble.dart';
import '../models/character.dart';

class ChatScreen extends StatelessWidget {
  final Character character;

  const ChatScreen({super.key, required this.character});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black87,
        title: Row(
          children: [
            CircleAvatar(
              backgroundImage: AssetImage(character.cards[0]), // dynamic card
            ),
            const SizedBox(width: 10),
            Text(character.name, style: const TextStyle(color: Colors.white)),
            const Spacer(),
            const Icon(Icons.favorite, color: Colors.pinkAccent),
            Text("${character.affection}", style: const TextStyle(color: Colors.white)),
          ],
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          ChatBubble(
            text: "Hey there, beautiful. I don't suppose you thought of me today?",
            isUser: true,
          ),
          ChatBubble(
            text: "I missed you so much. Did you have a good day?",
            isUser: false,
          ),
        ],
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                decoration: InputDecoration(
                  hintText: "Send Message",
                  filled: true,
                  fillColor: Colors.white10,
                  hintStyle: const TextStyle(color: Colors.white54),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
                style: const TextStyle(color: Colors.white),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.send, color: Colors.pinkAccent),
              onPressed: () {},
            ),
          ],
        ),
      ),
    );
  }
}