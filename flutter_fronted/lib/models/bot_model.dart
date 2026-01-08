class BotModel {
  final String id;
  final String name;
  final String description;
  final String avatarUrl;

  /// Defines how the bot behaves and speaks
  final BotPersona persona;

  /// Defines how the bot handles memory & relationship growth
  final BotMemoryPolicy memoryPolicy;

  BotModel({
    required this.id,
    required this.name,
    required this.description,
    required this.avatarUrl,
    required this.persona,
    required this.memoryPolicy,
  });
}

class BotPersona {
  /// The system prompt or core personality definition
  final String systemPrompt;

  /// Human-readable personality traits (used by UI & tuning)
  final List<String> traits;

  BotPersona({
    required this.systemPrompt,
    required this.traits,
  });
}

class BotMemoryPolicy {
  /// short = session only
  /// long = persistent
  /// hybrid = summarized + recent
  final String scope;

  /// Higher values = stronger memory retention
  final int retentionStrength;

  BotMemoryPolicy({
    required this.scope,
    required this.retentionStrength,
  });
}
