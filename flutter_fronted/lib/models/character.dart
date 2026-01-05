class Character {
  final String name;
  final List<String> cards;   // e.g. ["assets/characters/arael_1.png", "assets/characters/arael_2.png"]
  final int affection;

  Character({
    required this.name,
    required this.cards,
    required this.affection,
  });
}