// ─────────────────────────────────────────────
// 🤖 BOT CORE MODEL
// ─────────────────────────────────────────────

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

  // ───────── Serialization ─────────

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
      id: json['id'] ?? '',
      name: json['name'] ?? 'Unknown Bot',
      description: json['description'] ?? '',
      avatarUrl: json['avatarUrl'] ?? '',
      persona: BotPersona.fromJson(json['persona'] ?? {}),
      memoryPolicy: BotMemoryPolicy.fromJson(json['memoryPolicy'] ?? {}),
    );
  }
}

// ─────────────────────────────────────────────
// 🎭 BOT PERSONA (BEHAVIORAL DNA)
// ─────────────────────────────────────────────

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
      systemPrompt: json['systemPrompt'] ?? '',
      // Safe casting of dynamic list to String list
      traits: (json['traits'] as List?)?.map((e) => e.toString()).toList() ?? [],
    );
  }
}

// ─────────────────────────────────────────────
// 💾 BOT MEMORY POLICY (COGNITIVE RULES)
// ─────────────────────────────────────────────

enum MemoryScope { short, long, hybrid }

class BotMemoryPolicy {
  /// Determines the persistence strategy (session, persistent, or summarized)
  final MemoryScope scope;

  /// Higher values = stronger memory retention (used in bond evolution)
  final int retentionStrength;

  BotMemoryPolicy({
    required this.scope,
    required this.retentionStrength,
  });

  // 🧠 MEMORY CONFIGURATION HELPERS
  bool get isPersistent => scope == MemoryScope.long || scope == MemoryScope.hybrid;
  bool get usesSummarization => scope == MemoryScope.hybrid;

  Map<String, dynamic> toJson() {
    return {
      'scope': scope.name, // Saves enum as string "short", "long", etc.
      'retentionStrength': retentionStrength,
    };
  }

  factory BotMemoryPolicy.fromJson(Map<String, dynamic> json) {
    return BotMemoryPolicy(
      // 🧠 EVOLUTION LOGIC: Safely parse enum from string
      scope: MemoryScope.values.firstWhere(
        (e) => e.name == json['scope'],
        orElse: () => MemoryScope.short,
      ),
      retentionStrength: json['retentionStrength'] ?? 0,
    );
  }
}