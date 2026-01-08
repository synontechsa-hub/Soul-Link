import '../models/user_model.dart';
import '../models/bot_model.dart';
import '../models/conversation_model.dart';
import '../models/message_model.dart';
import 'package:flutter/foundation.dart';

class AppSession extends ChangeNotifier {
  /// The logged-in user
  UserModel? currentUser;

  /// All available bots (keyed by botId)
  final Map<String, BotModel> bots;

  /// All conversations (keyed by conversationId)
  final Map<String, ConversationModel> conversations;

  /// The currently active conversation
  String? activeConversationId;

  AppSession({
    this.currentUser,
    Map<String, BotModel>? bots,
    Map<String, ConversationModel>? conversations,
    this.activeConversationId,
  })  : bots = bots ?? {},
        conversations = conversations ?? {};

  // ─────────────────────────────────────────────
  // 🔍 GETTERS & QUERIES
  // ─────────────────────────────────────────────

  /// Convenience getter for the active conversation
  ConversationModel? get activeConversation {
    if (activeConversationId == null) return null;
    return conversations[activeConversationId];
  }

  /// Get the conversation for a specific bot (one per bot per user)
  ConversationModel? getConversationForBot(String botId) {
    // Optimization: Iterable.cast or .whereType can be cleaner, 
    // but firstWhere with orElse is the standard approach.
    return conversations.values.cast<ConversationModel?>().firstWhere(
      (c) => c?.botId == botId,
      orElse: () => null,
    );
  }

  // ─────────────────────────────────────────────
  // 🔹 MESSAGE & MUTATION LOGIC
  // ─────────────────────────────────────────────

  void addUserMessage(String conversationId, String content) {
    final conversation = conversations[conversationId];
    if (conversation == null) return;

    final message = MessageModel.user(content);
    
    // Mutation: Add message and update timestamps
    conversation.messages.add(message);
    conversation.lastUpdated = DateTime.now();

    // 🧠 Trigger Evolution logic
    conversation.state = _evolveConversationState(
      conversation: conversation,
      lastUserMessage: message,
    );

    notifyListeners();
  }

  void addBotMessage(String conversationId, String content) {
    final conversation = conversations[conversationId];
    if (conversation == null) return;

    conversation.messages.add(MessageModel.bot(content));
    conversation.lastUpdated = DateTime.now();

    notifyListeners();
  }

  // ─────────────────────────────────────────────
  // 🧠 CONVERSATION EVOLUTION ENGINE
  // ─────────────────────────────────────────────

  ConversationState _evolveConversationState({
    required ConversationModel conversation,
    required MessageModel lastUserMessage,
  }) {
    final current = conversation.state;
    final bot = bots[conversation.botId];
    
    // Accessing safety: If no bot is found, default to standard retention
    final retentionStrength = bot?.memoryPolicy.retentionStrength ?? 0;

    int nextLevel = current.progressionLevel;

    // 📈 BOND GROWTH RULES
    // 1. Effort Check: User message length must exceed a threshold influenced by bot retention.
    final bool isMeaningfulInteraction = lastUserMessage.content.length > (20 + retentionStrength);
    
    if (isMeaningfulInteraction) {
      nextLevel += 1;
    }

    // 📔 MEMORY RETENTION RULES (Placeholder for future logic)
    // You can implement summary truncation or key-value memory updates here.
    String? updatedSummary = current.memorySummary;

    return ConversationState(
      progressionLevel: nextLevel,
      memorySummary: updatedSummary,
    );
  }

  // ─────────────────────────────────────────────
  // ⚙️ SESSION CONTROLS
  // ─────────────────────────────────────────────

  void setActiveConversation(String conversationId) {
    if (!conversations.containsKey(conversationId)) return;
    activeConversationId = conversationId;
    notifyListeners();
  }
}