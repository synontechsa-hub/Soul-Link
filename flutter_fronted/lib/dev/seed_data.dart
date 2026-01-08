import 'dart:convert';
import 'package:flutter/services.dart';
import '../state/app_session.dart';
import '../services/soul_registry.dart';
import '../models/user_model.dart';
import '../models/conversation_model.dart';
import '../models/message_model.dart';

// ─────────────────────────────────────────────
// 🏗️ DATA SEEDING ENGINE (SCALABLE)
// ─────────────────────────────────────────────

Future<void> seedAppSession(AppSession session) async {
  // 1️⃣ USER IDENTITY
  session.currentUser = UserModel(
    id: 'user_dev',
    screenName: 'Soul Wanderer',
    createdAt: DateTime.now(),
    economy: UserEconomy(currency: 1000, points: 500),
  );

  // 2️⃣ DYNAMIC BOT LOADING
  // List matches your exact filenames: Bot-Evangeline.json, etc.
  final List<String> activeBots = ['Bot-Evangeline', 'Bot-Echo', 'Bot-Nova'];

  for (String botFile in activeBots) {
    try {
      final String response = await rootBundle.loadString('assets/bots/$botFile.json');
      final Map<String, dynamic> data = json.decode(response);
      
      // Map JSON to our strict Dart Model
      final bot = SoulRegistry.mapJsonToBot(data);
      session.bots[bot.id] = bot;
      
      // 3️⃣ INITIALIZE STARTING CONVERSATIONS
      // This wires the bot into the "Chats" tab immediately
      _seedInitialConversation(session, bot);

      print("🧬 Soul Linked: ${bot.name}");
    } catch (e) {
      print("⚠️ Failed to link $botFile: $e");
    }
  }
}

// ─────────────────────────────────────────────
// 🧬 STYLIZED COMPONENTS: CONVO STARTER
// ─────────────────────────────────────────────

void _seedInitialConversation(AppSession session, var bot) {
  final convoId = 'convo_${bot.id}';
  
  // Only add if it doesn't exist to prevent duplicates on hot-reload
  if (!session.conversations.containsKey(convoId)) {
    session.conversations[convoId] = ConversationModel(
      id: convoId,
      userId: session.currentUser!.id,
      botId: bot.id,
      createdAt: DateTime.now(),
      lastUpdated: DateTime.now(),
      messages: [
        MessageModel.bot("Connection established. Waiting for input..."),
      ],
      state: ConversationState(progressionLevel: 1),
    );
  }
}