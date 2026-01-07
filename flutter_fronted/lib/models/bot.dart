class Bot {
  final String name;
  final String archetype;
  final String description;

  Bot({required this.name, required this.archetype, required this.description});

  factory Bot.fromJson(Map<String, dynamic> json) {
    return Bot(
      name: json['name'],
      archetype: json['archetype'],
      description: json['description'],
    );
  }
}
