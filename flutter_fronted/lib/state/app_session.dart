import '../models/user_model.dart';
import '../models/bot_model.dart';
import '../models/conversation_model.dart';
import '../models/message_model.dart';

class AppSession {
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

  /// Convenience getter for the active conversation
  ConversationModel? get activeConversation {
    if (activeConversationId == null) return null;
    return conversations[activeConversationId];
  }

  /// Get the conversation for a specific bot (one per bot per user)
  ConversationModel? getConversationForBot(String botId) {
    return conversations.values
        .where((c) => c.botId == botId)
        .cast<ConversationModel?>()
        .firstWhere((c) => c != null, orElse: () => null);
  }

  // ─────────────────────────────────────────────
  // 🔹 MESSAGE & STATE MUTATION (THIS IS NEW)
  // ─────────────────────────────────────────────

  void addUserMessage(String conversationId, String content) {
    final conversation = conversations[conversationId];
    if (conversation == null) return;

    conversation.messages.add(
      MessageModel.user(content),
    );

    _evolveConversationState(conversation);
    conversation.lastUpdated = DateTime.now();
  }

  void addBotMessage(String conversationId, String content) {
    final conversation = conversations[conversationId];
    if (conversation == null) return;

    conversation.messages.add(
      MessageModel.bot(content),
    );

    conversation.lastUpdated = DateTime.now();
  }

  // ─────────────────────────────────────────────
  // 🧠 CONVERSATION EVOLUTION LOGIC
  // ─────────────────────────────────────────────

  void _evolveConversationState(ConversationModel conversation) {
    final currentState = conversation.state;

    conversation.state = ConversationState(
      progressionLevel: currentState.progressionLevel + 1,
      memorySummary: currentState.memorySummary,
    );
  }
}
