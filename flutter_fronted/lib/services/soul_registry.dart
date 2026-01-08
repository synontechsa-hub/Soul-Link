import '../models/bot_model.dart';

// ─────────────────────────────────────────────
// 🏗️ SOUL REGISTRY (JSON PARSER)
// ─────────────────────────────────────────────

class SoulRegistry {
  /// 🧠 MAPPER: Converts your backend JSON structure into a BotModel.
  /// This handles the specific keys like 'Core Identity' and 'Dialogue Model'.
  static BotModel mapJsonToBot(Map<String, dynamic> json) {
    final core = json['Core Identity'] ?? {};
    final diag = json['Dialogue Model'] ?? {};
    final personality = json['Personality'] ?? {};
    final traits = personality['Traits'] ?? [];
    final cards = json['Cards'] as List? ?? [];

    return BotModel(
      id: 'bot_${core['Name'].toString().toLowerCase()}',
      name: core['Name'] ?? 'Unknown',
      description: core['Background'] ?? '',
      
      // Use the first card as the primary avatar
      avatarUrl: cards.isNotEmpty ? cards[0] : 'assets/characters/default.png',
      
      persona: BotPersona(
        systemPrompt: diag['SystemPrompt'] ?? '',
        traits: List<String>.from(traits),
      ),

      memoryPolicy: BotMemoryPolicy(
        // 🧩 ARCHETYPE LOGIC: 
        // Gothic Lolitas (Evangeline) get Long memory.
        // Glitch AIs (Echo) or Innocent Children (Nova) get Short/Hybrid.
        scope: _assignScope(core['Archetype']),
        retentionStrength: 7,
      ),
    );
  }

  // 🧬 STYLIZED COMPONENTS: ARCHETYPE MAPPING
  static MemoryScope _assignScope(String? archetype) {
    switch (archetype) {
      case 'Gothic Lolita':
        return MemoryScope.long;
      case 'Glitch AI':
        return MemoryScope.short;
      case 'Innocent AI Child':
        return MemoryScope.hybrid;
      default:
        return MemoryScope.hybrid;
    }
  }
}