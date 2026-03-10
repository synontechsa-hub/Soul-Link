// fontend/lib/models/dashboard_state.dart
// version.py
// _dev/

import 'relationship.dart';

class DashboardState {
  final String userId;
  final String username;
  final String displayName;
  final List<SoulRelationship> activeSouls;

  DashboardState({
    required this.userId,
    required this.username,
    required this.displayName,
    required this.activeSouls,
  });

  factory DashboardState.fromJson(Map<String, dynamic> json) {
    var list = json['active_souls'] as List;
    List<SoulRelationship> soulList = list.map((i) => SoulRelationship.fromJson(i)).toList();

    return DashboardState(
      userId: json['user_id'],
      username: json['username'],
      displayName: json['display_name'] ?? json['username'],
      activeSouls: soulList,
    );
  }
}