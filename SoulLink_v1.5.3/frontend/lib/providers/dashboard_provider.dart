// frontend/lib/providers/dashboard_provider.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/dashboard_state.dart';
import '../models/user_model.dart';

class DashboardProvider extends ChangeNotifier {
  final ApiService apiService; // Position 1
  DashboardState? _state;
  User? _currentUser;
  bool _isLoading = false;

  // THE FIX: Standard positional constructor
  DashboardProvider(this.apiService);

  DashboardState? get state => _state;
  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  bool get isLoggedIn => _currentUser != null;

  /// CORE-LOOP: Profile is complete if the user has defined a gender or a bio.
  /// This ensures they have passed through the Mirror at least once.
  bool get isProfileComplete {
    if (_currentUser == null) return false;
    // Check if critical fields are set
    final hasGender = _currentUser!.genderIdentity != null && _currentUser!.genderIdentity != "Not Specified";
    final hasBio = _currentUser!.bio != null && _currentUser!.bio!.isNotEmpty;
    return hasGender || hasBio;
  }

  Future<void> login(String username) async {
    _isLoading = true;
    notifyListeners();
    try {
      final data = await apiService.login(username);
      if (data['profile'] != null) {
        _currentUser = User.fromJson(data['profile']);
      }
      await syncDashboard();
    } catch (e) {
      debugPrint("Login Error: $e");
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refreshUser() async {
    try {
      final data = await apiService.getUserProfile();
      _currentUser = User.fromJson(data);
      notifyListeners();
    } catch (e) {
      debugPrint("Refresh User Error: $e");
    }
  }

  void logout() {
    _currentUser = null;
    apiService.userId = null;
    notifyListeners();
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
}