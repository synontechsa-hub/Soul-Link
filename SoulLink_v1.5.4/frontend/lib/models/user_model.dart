// frontend/lib/models/user_model.dart
// version.py
// _dev/

class User {
  final String userId;
  final String username;
  final String? displayName;
  final String? bio;
  final String? genderIdentity;
  final int? age;
  final String accountTier;
  final int gems;
  final int energy;
  final String currentLocation;

  User({
    required this.userId,
    required this.username,
    this.displayName,
    this.bio,
    this.genderIdentity,
    this.age,
    required this.accountTier,
    required this.gems,
    required this.energy,
    required this.currentLocation,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'] ?? '',
      username: json['username'] ?? '',
      displayName: json['display_name'],
      bio: json['bio'],
      genderIdentity: json['gender'] ?? json['gender_identity'],
      age: json['age'],
      accountTier: json['account_tier'] ?? 'Standard',
      gems: json['gems'] ?? 0,
      energy: json['energy'] ?? 0,
      currentLocation: json['current_location'] ?? 'linkside_apartment',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'username': username,
      'display_name': displayName,
      'bio': bio,
      'gender_identity': genderIdentity,
      'age': age,
      'account_tier': accountTier,
      'gems': gems,
      'energy': energy,
      'current_location': currentLocation,
    };
  }
}
