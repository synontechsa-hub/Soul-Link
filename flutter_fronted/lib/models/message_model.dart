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

  /// Convenience constructors
  factory MessageModel.user(String content) {
    return MessageModel(
      role: MessageRole.user,
      content: content,
    );
  }

  factory MessageModel.bot(String content) {
    return MessageModel(
      role: MessageRole.bot,
      content: content,
    );
  }

  /// Serialization
  Map<String, dynamic> toJson() {
    return {
      'role': role.name,
      'content': content,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      role: MessageRole.values.byName(json['role']),
      content: json['content'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}
