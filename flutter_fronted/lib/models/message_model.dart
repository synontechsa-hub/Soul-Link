// ─────────────────────────────────────────────
// 💬 MESSAGE ENTITIES
// ─────────────────────────────────────────────

enum MessageRole {
  user,
  bot,
}

class MessageModel {
  final MessageRole role;
  final String content;
  final DateTime timestamp;

  MessageModel({
    required this.role,
    required this.content,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  // ─────────────────────────────────────────────
  // 🏗️ CONVENIENCE CONSTRUCTORS
  // ─────────────────────────────────────────────

  /// Creates a message attributed to the human user
  factory MessageModel.user(String content) {
    return MessageModel(
      role: MessageRole.user,
      content: content,
    );
  }

  /// Creates a message attributed to the AI bot
  factory MessageModel.bot(String content) {
    return MessageModel(
      role: MessageRole.bot,
      content: content,
    );
  }

  // ─────────────────────────────────────────────
  // 🧠 CHAT UI HELPERS
  // ─────────────────────────────────────────────

  bool get isFromUser => role == MessageRole.user;
  bool get isFromBot => role == MessageRole.bot;

  /// Returns a shortened preview of the message for list views
  String get preview => content.length > 50 
      ? '${content.substring(0, 50)}...' 
      : content;

  // ─────────────────────────────────────────────
  // 🔄 SERIALIZATION
  // ─────────────────────────────────────────────

  Map<String, dynamic> toJson() {
    return {
      'role': role.name,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      // 🧠 EVOLUTION LOGIC: Safe enum lookup
      role: MessageRole.values.firstWhere(
        (e) => e.name == json['role'],
        orElse: () => MessageRole.user, 
      ),
      content: json['content'] ?? '',
      timestamp: json['timestamp'] != null 
          ? DateTime.parse(json['timestamp']) 
          : DateTime.now(),
    );
  }
}