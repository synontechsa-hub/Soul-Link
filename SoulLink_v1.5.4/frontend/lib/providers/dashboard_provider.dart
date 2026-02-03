// frontend/lib/providers/dashboard_provider.dart
// version.py v1.5.4 Arise

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/dashboard_state.dart';
import '../models/user_model.dart' as model;
import 'package:supabase_flutter/supabase_flutter.dart';

class DashboardProvider extends ChangeNotifier {
  final ApiService apiService;
  DashboardState? _state;
  model.User? _currentUser;
  bool _isLoading = false;

  DashboardProvider(this.apiService) {
    // If we have a session, hydrate the provider immediately
    if (Supabase.instance.client.auth.currentSession != null) {
      initAfterAuth();
    }
  }

  DashboardState? get state => _state;
  model.User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _currentUser != null;

  /// CORE-LOOP: Profile is complete if the user has defined a gender or a bio.
  bool get isProfileComplete {
    if (_currentUser == null) return false;
    final hasGender = _currentUser!.genderIdentity != null && _currentUser!.genderIdentity != "Not Specified";
    final hasBio = _currentUser!.bio != null && _currentUser!.bio!.isNotEmpty;
    // Basic check: If data exists, it's "complete" enough for the dashboard
    return hasGender || hasBio;
  }

  /// Initialize state after successful Supabase Auth
  /// Fetches the profile from the Backend (JIT Sync) and then the dashboard.
  Future<void> initAfterAuth() async {
    _isLoading = true;
    notifyListeners();
    try {
      await refreshUser();
      await syncDashboard();
    } catch (e) {
      debugPrint("Init Error: $e");
      // If 401, logout?
      if (e.toString().contains("401")) { // Basic check
         logout();
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refreshUser() async {
    try {
      final data = await apiService.getUserProfile();
      _currentUser = model.User.fromJson(data);
      notifyListeners();
    } catch (e) {
      debugPrint("Refresh User Error: $e");
      rethrow;
    }
  }

  Future<void> syncDashboard() async {
    _isLoading = true;
    notifyListeners();
    try {
      _state = await apiService.getDashboard();
    } catch (e) {
      debugPrint("Sync Error: $e");
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void logout() {
    Supabase.instance.client.auth.signOut();
    _currentUser = null;
    notifyListeners();
  }
}