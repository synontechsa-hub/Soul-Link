// frontend/lib/services/auth_service.dart
// version.py v1.5.3-P

import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:flutter/foundation.dart';

class AuthService {
  final SupabaseClient _supabase = Supabase.instance.client;

  User? get user => _supabase.auth.currentUser;
  String? get currentJwt => _supabase.auth.currentSession?.accessToken;
  String? get currentUserId => _supabase.auth.currentUser?.id;

  Stream<AuthState> get authStateChanges => _supabase.auth.onAuthStateChange;

  /// 1. GUEST LOGIN (Anonymous)
  /// Creates a ghost UUID in Supabase which can be upgraded later.
  Future<AuthResponse> signInAnonymously() async {
    try {
      final response = await _supabase.auth.signInAnonymously();
      debugPrint("👻 Signed in as Guest: ${response.user?.id}");
      return response;
    } catch (e) {
      debugPrint("❌ Guest Login Failed: $e");
      rethrow;
    }
  }

  /// 2. EMAIL LOGIN
  Future<AuthResponse> signInWithEmail(String email, String password) async {
    return _supabase.auth.signInWithPassword(email: email, password: password);
  }

  /// 3. EMAIL SIGNUP
  Future<AuthResponse> signUpWithEmail(String email, String password) async {
    return _supabase.auth.signUp(email: email, password: password);
  }

  /// 4. UPGRADE GUEST TO EMAIL (Preserves UUID)
  /// Uses updateUser to attach an email/password to the anonymous account.
  Future<UserResponse> upgradeGuestToEmail(String email, String password) async {
    try {
      final response = await _supabase.auth.updateUser(
        UserAttributes(email: email, password: password),
      );
      debugPrint("📧 Upgraded Guest to Email: ${response.user?.email}");
      return response;
    } catch (e) {
      debugPrint("❌ Upgrade Failed: $e");
      rethrow; // Handle UI error
    }
  }

  Future<void> signOut() async {
    await _supabase.auth.signOut();
  }
}
