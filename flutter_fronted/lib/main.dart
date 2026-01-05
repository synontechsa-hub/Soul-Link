import 'package:flutter/material.dart';
import 'screens/chat_screen.dart';
import 'models/character.dart';

void main() {
  // Example character instance
  Character arael = Character(
    name: "Arael",
    cards: [
      "assets/characters/arael_1.png",
      "assets/characters/arael_2.png",
    ],
    affection: 114,
  );

  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    home: ChatScreen(character: arael),
  ));
}