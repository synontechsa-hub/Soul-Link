// frontend/lib/models/relationship.dart
// version.py v1.5.3-P

class SoulRelationship {
  final String soulId;
  final String name;
  final String archetype;
  final String currentLocation;
  final String intimacyTier;
  final int intimacyScore;
  final bool isArchitect;
  final bool nsfwUnlocked;
  final String lastInteraction;
  final String portrait_url; // 🖼️ THE MISSING LINK

  SoulRelationship({
    required this.soulId,
    required this.name,
    required this.archetype,
    required this.currentLocation,
    required this.intimacyTier,
    required this.intimacyScore,
    required this.isArchitect,
    required this.nsfwUnlocked,
    required this.lastInteraction,
    required this.portrait_url, // Added to constructor
  });

  factory SoulRelationship.fromJson(Map<String, dynamic> json) {
    return SoulRelationship(
      soulId: json['soul_id'] ?? "",
      name: json['name'] ?? "Unknown",
      archetype: json['archetype'] ?? "Unknown",
      currentLocation: json['location'] ?? "Unknown",
      intimacyTier: json['tier'] ?? "STRANGER",
      intimacyScore: json['intimacy_score'] ?? 0,
      isArchitect: json['is_architect'] ?? false,
      nsfwUnlocked: json['nsfw_unlocked'] ?? false,
      lastInteraction: json['last_interaction'] ?? "",
      // ✅ Map the backend field to the model
      portrait_url: json['portrait_url'] ?? "/assets/images/souls/default.jpg",
    );
  }
}