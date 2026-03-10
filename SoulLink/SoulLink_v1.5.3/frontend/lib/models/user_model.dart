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
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'] ?? '',
      username: json['username'] ?? '',
      displayName: json['display_name'],
      bio: json['bio'],
      // Handle both 'gender' (from backend) and 'gender_identity' (legacy)
      genderIdentity: json['gender'] ?? json['gender_identity'],
      age: json['age'],
      accountTier: json['account_tier'] ?? 'Standard',
      gems: json['gems'] ?? 0,
      energy: json['energy'] ?? 0,
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
    };
  }
}
