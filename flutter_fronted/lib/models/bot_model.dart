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

  /// ---- Serialization ----

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'avatarUrl': avatarUrl,
      'persona': persona.toJson(),
      'memoryPolicy': memoryPolicy.toJson(),
    };
  }

  factory BotModel.fromJson(Map<String, dynamic> json) {
    return BotModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      avatarUrl: json['avatarUrl'],
      persona: BotPersona.fromJson(json['persona']),
      memoryPolicy: BotMemoryPolicy.fromJson(json['memoryPolicy']),
    );
  }
}

/// ---- Persona ----

class BotPersona {
  /// The system prompt or core personality definition
  final String systemPrompt;

  /// Human-readable personality traits (used by UI & tuning)
  final List<String> traits;

  BotPersona({
    required this.systemPrompt,
    required this.traits,
  });

  Map<String, dynamic> toJson() {
    return {
      'systemPrompt': systemPrompt,
      'traits': traits,
    };
  }

  factory BotPersona.fromJson(Map<String, dynamic> json) {
    return BotPersona(
      systemPrompt: json['systemPrompt'],
      traits: List<String>.from(json['traits']),
    );
  }
}

/// ---- Memory Policy ----

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

  Map<String, dynamic> toJson() {
    return {
      'scope': scope,
      'retentionStrength': retentionStrength,
    };
  }

  factory BotMemoryPolicy.fromJson(Map<String, dynamic> json) {
    return BotMemoryPolicy(
      scope: json['scope'],
      retentionStrength: json['retentionStrength'],
    );
  }
}
