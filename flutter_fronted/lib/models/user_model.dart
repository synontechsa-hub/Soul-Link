class UserModel {
  final String id;
  final String screenName;
  final DateTime createdAt;

  /// Optional profile details
  final int? age;
  final String? gender;

  /// User-owned economy & progression
  final UserEconomy economy;

  UserModel({
    required this.id,
    required this.screenName,
    required this.createdAt,
    this.age,
    this.gender,
    required this.economy,
  });
}

class UserEconomy {
  /// Premium or earned in-app currency
  final int currency;

  /// Non-premium progression points
  final int points;

  UserEconomy({
    required this.currency,
    required this.points,
  });
}
