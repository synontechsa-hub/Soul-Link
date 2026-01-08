import 'message_model.dart';

class ConversationModel {
  final String id;
  final String userId;
  final String botId;
  final List<MessageModel> messages;
  final DateTime createdAt;
  final DateTime lastUpdated;

  // Optional state that summarizes the relationship
  final ConversationState? state;

  ConversationModel({
    required this.id,
    required this.userId,
    required this.botId,
    required this.messages,
    required this.createdAt,
    required this.lastUpdated,
    this.state,
  });
}

class ConversationState {
  final int progressionLevel;
  final String? memorySummary;

  ConversationState({
    required this.progressionLevel,
    this.memorySummary,
  });
}
