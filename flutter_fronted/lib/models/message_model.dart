class MessageModel {
  final String id;
  final String conversationId;
  final String sender; // "user" or "bot"
  final String senderId;
  final String content;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  MessageModel({
    required this.id,
    required this.conversationId,
    required this.sender,
    required this.senderId,
    required this.content,
    required this.timestamp,
    this.metadata,
  });
}
