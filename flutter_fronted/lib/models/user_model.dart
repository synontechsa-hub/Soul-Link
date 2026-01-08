// ─────────────────────────────────────────────
// 👤 USER PROFILE MODEL
// ─────────────────────────────────────────────

class UserModel {
  final String id;
  final String screenName;
  final DateTime createdAt;

  /// Optional profile details
  final int? age;
  final String? gender;

  /// 🧠 ECONOMY & PROGRESSION
  /// Encapsulates all financial and experience point logic
  final UserEconomy economy;

  UserModel({
    required this.id,
    required this.screenName,
    required this.createdAt,
    this.age,
    this.gender,
    required this.economy,
  });

  // ───────── Serialization ─────────

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'screenName': screenName,
      'createdAt': createdAt.toIso8601String(),
      'age': age,
      'gender': gender,
      'economy': economy.toJson(),
    };
  }

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      screenName: json['screenName'] ?? 'Guest',
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
      age: json['age'],
      gender: json['gender'],
      economy: UserEconomy.fromJson(json['economy'] ?? {}),
    );
  }
}

// ─────────────────────────────────────────────
// 💰 USER ECONOMY (FINANCIAL DNA)
// ─────────────────────────────────────────────

class UserEconomy {
  /// Premium or earned in-app currency (e.g., Gems/Coins)
  final int currency;

  /// Non-premium progression points (e.g., XP/Leveling)
  final int points;

  UserEconomy({
    required this.currency,
    required this.points,
  });

  // 🧠 ECONOMY EVOLUTION HELPERS
  
  /// Check if the user can afford a specific cost
  bool canAfford(int cost) => currency >= cost;

  /// Logic for displaying "Level" based on accumulated points
  /// Example: 100 points per level
  int get calculatedLevel => (points / 100).floor() + 1;

  // ───────── Serialization ─────────

  Map<String, dynamic> toJson() {
    return {
      'currency': currency,
      'points': points,
    };
  }

  factory UserEconomy.fromJson(Map<String, dynamic> json) {
    return UserEconomy(
      currency: json['currency'] ?? 0,
      points: json['points'] ?? 0,
    );
  }
}