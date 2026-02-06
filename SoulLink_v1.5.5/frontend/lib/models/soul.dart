// frontend/lib/models/soul.dart
// version.py
// _dev/

// "Does this unit have a soul?"
// - Legion - Mass Effect 2
class Soul {
  final String soulId;
  final String name;
  final String summary;
  final String archetype;
  final Map<String, dynamic> aestheticPillar;

  Soul({
    required this.soulId,
    required this.name,
    required this.summary,
    required this.archetype,
    required this.aestheticPillar,
  });

  // The "Factory" - how we turn raw JSON from the API into a Dart Object
  // Ironic... my backend had a souls_forge in 1.5.1 that handled only json reading!
  // See the little nod to the forge in locations? Ehe... It's the soul forge!
  // Coming into play later in the roadmap, for now... it exists as a concept ;)
  factory Soul.fromJson(Map<String, dynamic> json) {
    return Soul(
      soulId: json['id'] ?? json['soul_id'],
      name: json['name'],
      summary: json['summary'] ?? "A mysterious soul...",
      archetype: json['archetype'] ?? "Unknown",
      aestheticPillar: json['aesthetic_pillar'] ?? {},
    );
  }
}