// frontend/lib/services/api_service.dart
// version.py
// _dev/

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import '../core/config.dart';
import '../models/dashboard_state.dart';

class ApiService {
  // Use AppConfig for dynamic URL configuration
  static String get baseUrl => '${AppConfig.apiBaseUrl}/api/v1';
  String? userId;

  ApiService({this.userId});

  // --- HEADERS WITH JWT ---
  
  Map<String, String> get _headers {
    final session = Supabase.instance.client.auth.currentSession;
    final token = session?.accessToken;
    
    // Debug: Print token (first 10 chars)
    if (token != null) print("🔑 API Call with Token: ${token.substring(0, 10)}...");

    return {
      "Content-Type": "application/json",
      if (token != null) "Authorization": "Bearer $token",
    };
  }

  // --- AUTHENTICATION (Supabase handled, only JIT sync here if needed) ---
  
  // Note: Login/Register is now done via AuthService (Supabase SDK) directly.
  // The Backend 'Sync' happens automatically on 'getUserProfile' or middleware.

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
    try {
      final response = await http.get(Uri.parse("$baseUrl/users/me"), headers: _headers);
      if (response.statusCode == 200) return jsonDecode(response.body);
      
      print("❌ PROFILE ERROR: Status=${response.statusCode}, Body=${response.body}");
      throw Exception("Profile Error: ${response.statusCode}");
    } catch (e) {
      print("❌ PROFILE EXCEPTION: $e");
      rethrow;
    }
  }

  Future<void> updateUserProfile({String? name, String? bio, String? gender}) async {
    await http.patch(
      Uri.parse("$baseUrl/users/update"),
      headers: _headers,
      body: jsonEncode({
        if (name != null) "display_name": name,
        if (bio != null) "bio": bio,
        if (gender != null) "gender": gender,
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

  Future<Map<String, dynamic>> moveUser({required String locationId}) async {
    final response = await http.patch(
      Uri.parse("$baseUrl/users/move"),
      headers: _headers,
      body: jsonEncode({"location_id": locationId}),
    );
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("User Move Error");
  }

  // --- TIME SLOT SYSTEM ---

  Future<Map<String, dynamic>> advanceTimeSlot({String? targetSlot}) async {
    final response = await http.post(
      Uri.parse("$baseUrl/time/advance"),
      headers: _headers,
      body: jsonEncode({
        if (targetSlot != null) "target_slot": targetSlot,
      }),
    );
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Time Advance Error: ${response.body}");
  }

  Future<Map<String, dynamic>> getCurrentTimeState() async {
    final response = await http.get(
      Uri.parse("$baseUrl/time/current"),
      headers: _headers,
    );
    if (response.statusCode == 200) return jsonDecode(response.body);
    throw Exception("Time State Error");
  }

  Future<List<dynamic>> getAllTimeSlots() async {
    final response = await http.get(Uri.parse("$baseUrl/time/slots"));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['slots'];
    }
    throw Exception("Time Slots Error");
  }
}