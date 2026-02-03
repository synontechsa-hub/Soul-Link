// frontend/lib/services/api_service.dart
// version.py
// _dev/

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/dashboard_state.dart';

class ApiService {
  static const String baseUrl = "http://localhost:8000/api/v1";
  String? userId;

  ApiService({this.userId});

  Map<String, String> get _headers {
    final headers = {"Content-Type": "application/json"};
    if (userId != null) {
      headers["X-User-Id"] = userId!;
    }
    return headers;
  }

  // --- AUTHENTICATION ---

  Future<Map<String, dynamic>> login(String username) async {
    final response = await http.post(
      Uri.parse("$baseUrl/users/login"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": username}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      userId = data['user_id']; // Update the service's current user ID
      return data;
    } else {
      throw Exception("Login Failed: ${response.body}");
    }
  }

  Future<Map<String, dynamic>> register(String username, {String? displayName}) async {
    final response = await http.post(
      Uri.parse("$baseUrl/users/register"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": username,
        if (displayName != null) "display_name": displayName,
      }),
    );

    if (response.statusCode == 200) {
      // Registration successful, return data (maybe auto-login depending on flow)
      return jsonDecode(response.body);
    } else {
      throw Exception("Registration Failed: ${response.body}");
    }
  }

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