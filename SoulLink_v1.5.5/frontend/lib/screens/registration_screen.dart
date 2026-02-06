// frontend/lib/screens/registration_screen.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';

import '../services/auth_service.dart';

class RegistrationScreen extends StatefulWidget {
  const RegistrationScreen({super.key});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _usernameController = TextEditingController();
  final _displayController = TextEditingController();
  bool _isRegistering = false;
  String? _errorMessage;

  @override
  void dispose() {
    _usernameController.dispose();
    _displayController.dispose();
    super.dispose();
  }

  Future<void> _register() async {
    final username = _usernameController.text.trim();
    final displayName = _displayController.text.trim();

    if (username.isEmpty) {
      setState(() => _errorMessage = "IDENTIFIER REQUIRED");
      return;
    }
    if (username.length < 3) {
      setState(() => _errorMessage = "IDENTIFIER TOO SHORT (MIN 3)");
      return;
    }

    setState(() => _isRegistering = true);
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    final authService = AuthService();

    try {
      // 1. Register (Anonymous Auth for now)
      await authService.signInAnonymously();
      
      // 2. Update Profile with Name
      // Note: Backend might sync username from auth metadata or we rely on display_name
      await provider.apiService.updateUserProfile(
        name: displayName.isNotEmpty ? displayName : username
      );
      
      // 3. Auto-login / Init Dashboard
      await provider.initAfterAuth();
      
      // 4. Navigation handled by Main Consumer (or manual pop)
      if (mounted) {
         Navigator.pop(context); // Clear registration from stack
      }

    } catch (e) {
      setState(() => _errorMessage = e.toString().replaceAll("Exception:", "").trim());
    } finally {
      if (mounted) setState(() => _isRegistering = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.cyanAccent),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Container(
        padding: const EdgeInsets.all(30),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "NEW IDENTITY",
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              "ESTABLISH CONNECTION TO THE CITY",
              style: TextStyle(
                color: Colors.white54,
                fontSize: 12,
                letterSpacing: 1,
              ),
            ),
            const SizedBox(height: 40),
            
            // USERNAME FIELD
            TextField(
              controller: _usernameController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: "UNIQUE IDENTIFIER",
                labelStyle: const TextStyle(color: Colors.cyanAccent),
                hintText: "e.g. Neo123",
                hintStyle: const TextStyle(color: Colors.white24),
                enabledBorder: OutlineInputBorder(
                  borderSide: BorderSide(color: Colors.white.withOpacity(0.1)),
                  borderRadius: BorderRadius.circular(15),
                ),
                focusedBorder: const OutlineInputBorder(
                  borderSide: BorderSide(color: Colors.cyanAccent),
                  borderRadius: BorderRadius.all(Radius.circular(15)),
                ),
                prefixIcon: const Icon(Icons.fingerprint, color: Colors.cyanAccent),
              ),
            ),
            const SizedBox(height: 20),

            // DISPLAY NAME FIELD
            TextField(
              controller: _displayController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: "DISPLAY NAME (OPTIONAL)",
                labelStyle: const TextStyle(color: Colors.cyanAccent),
                hintText: "What should we call you?",
                hintStyle: const TextStyle(color: Colors.white24),
                enabledBorder: OutlineInputBorder(
                  borderSide: BorderSide(color: Colors.white.withOpacity(0.1)),
                  borderRadius: BorderRadius.circular(15),
                ),
                focusedBorder: const OutlineInputBorder(
                  borderSide: BorderSide(color: Colors.cyanAccent),
                  borderRadius: BorderRadius.all(Radius.circular(15)),
                ),
                prefixIcon: const Icon(Icons.badge_outlined, color: Colors.cyanAccent),
              ),
            ),

            if (_errorMessage != null) ...[
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.redAccent.withOpacity(0.1),
                  border: Border.all(color: Colors.redAccent.withOpacity(0.5)),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.redAccent, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Colors.redAccent, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const Spacer(),

            // REGISTER BUTTON
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: _isRegistering ? null : _register,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  foregroundColor: Colors.cyanAccent,
                  side: const BorderSide(color: Colors.cyanAccent, width: 2),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                child: _isRegistering
                    ? const CircularProgressIndicator(color: Colors.cyanAccent)
                    : const Text(
                        "FORGE IDENTITY",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          letterSpacing: 2,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
