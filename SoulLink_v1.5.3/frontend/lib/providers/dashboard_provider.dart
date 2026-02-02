// frontend/lib/providers/dashboard_provider.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/dashboard_state.dart';

class DashboardProvider extends ChangeNotifier {
  final ApiService apiService; // Position 1
  DashboardState? _state;
  bool _isLoading = false;

  // THE FIX: Standard positional constructor
  DashboardProvider(this.apiService);

  DashboardState? get state => _state;
  bool get isLoading => _isLoading;

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