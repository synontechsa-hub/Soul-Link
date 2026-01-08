import 'message_model.dart';

class ConversationModel {
  final String id;
  final String userId;
  final String botId;

  final List<MessageModel> messages;

  final DateTime createdAt;
  DateTime lastUpdated;

  ConversationState state;

  ConversationModel({
    required this.id,
    required this.userId,
    required this.botId,
    required this.messages,
    required this.createdAt,
    required this.lastUpdated,
    required this.state,
  });

  // ───────── Serialization ─────────

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'botId': botId,
      'createdAt': createdAt.toIso8601String(),
      'lastUpdated': lastUpdated.toIso8601String(),
      'messages': messages.map((m) => m.toJson()).toList(),
      'state': state.toJson(),
    };
  }

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      id: json['id'],
      userId: json['userId'],
      botId: json['botId'],
      createdAt: DateTime.parse(json['createdAt']),
      lastUpdated: DateTime.parse(json['lastUpdated']),
      messages: (json['messages'] as List)
          .map((m) => MessageModel.fromJson(m))
          .toList(),
      state: ConversationState.fromJson(json['state']),
    );
  }
}

class ConversationState {
  final int progressionLevel;
  final String? memorySummary;

  ConversationState({
    required this.progressionLevel,
    this.memorySummary,
  });

  Map<String, dynamic> toJson() {
    return {
      'progressionLevel': progressionLevel,
      'memorySummary': memorySummary,
    };
  }

  factory ConversationState.fromJson(Map<String, dynamic> json) {
    return ConversationState(
      progressionLevel: json['progressionLevel'],
      memorySummary: json['memorySummary'],
    );
  }
}
