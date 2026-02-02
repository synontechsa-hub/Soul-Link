// frontend/lib/services/api_service.dart
// version.py
// _dev/

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/dashboard_state.dart';

class ApiService {
  static const String baseUrl = "http://localhost:8000/api/v1";
  final String userId;

  ApiService({required this.userId});

  Map<String, String> get _headers => {
        "Content-Type": "application/json",
        "X-User-Id": userId,
      };

  // --- MISSING METHODS RESTORED BELOW ---

  /// THE PULSE: Fetches the dashboard state
  Future<DashboardState> getDashboard() async {
    final response = await http.get(
      Uri.parse("$baseUrl/sync/dashboard"),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return DashboardState.fromJson(jsonDecode(response.body));
    } else {
      throw Exception("Failed to sync: ${response.statusCode}");
    }
  }

  /// THE VOICE: Sends a message to a soul
  Future<Map<String, dynamic>> sendMessage(String soulId, String message) async {
    final response = await http.post(
      Uri.parse("$baseUrl/chat/send"),
      headers: _headers,
      body: jsonEncode({
        "soul_id": soulId,
        "message": message,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Message failed: ${response.statusCode}");
    }
  }

  /// THE RECORD: Fetches message history
  Future<List<dynamic>> getChatHistory(String soulId) async {
    final response = await http.get(
      Uri.parse("$baseUrl/chat/history?soul_id=$soulId"),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("History failed: ${response.statusCode}");
    }
  }

  // --- EXISTING METHODS (Keep these too) ---

  Future<Map<String, dynamic>> getUserProfile() async {
    final response = await http.get(Uri.parse("$baseUrl/users/me"), headers: _headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Profile Error");
  }

  Future<void> updateUserProfile({String? name, String? bio, String? gender}) async {
    await http.patch(
      Uri.parse("$baseUrl/users/update"),
      headers: _headers,
      body: jsonEncode({
        if (name != null) "display_name": name,
        if (bio != null) "bio": bio,
        if (gender != null) "gender_identity": gender,
      }),
    );
  }

  Future<List<dynamic>> getMapLocations() async {
    final response = await http.get(Uri.parse("$baseUrl/map/locations"), headers: _headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Map Error");
  }

  Future<List<dynamic>> getExploreSouls() async {
    final response = await http.get(Uri.parse("$baseUrl/souls/explore"), headers: _headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Explore Error");
  }

  Future<Map<String, dynamic>> linkWithSoul(String soulId) async {
    final response = await http.post(Uri.parse("$baseUrl/souls/$soulId/link"), headers: _headers);
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Link Error");
  }

  Future<Map<String, dynamic>> moveSoul({required String soulId, required String locationId}) async {
    final response = await http.post(
      Uri.parse("$baseUrl/map/move?soul_id=$soulId&location_id=$locationId"),
      headers: _headers,
    );
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Move Error");
  }
}