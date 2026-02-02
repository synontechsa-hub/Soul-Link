// frontend/lib/screens/login_screen.dart
// version.py v1.5.3-P

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  bool _isConnecting = false;

  Future<void> _initiateLink() async {
    if (_usernameController.text.isEmpty) return;

    setState(() => _isConnecting = true);
    final provider = Provider.of<DashboardProvider>(context, listen: false);

    try {
      // We'll tell the API to create or fetch this user
      await provider.apiService.login(_usernameController.text);
      // If successful, the provider handles the state change and main.dart
      // will automatically switch to the Dashboard.
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("LINK FAILURE: $e"),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) setState(() => _isConnecting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      body: Container(
        padding: const EdgeInsets.all(30),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.Language, size: 80, color: Colors.cyanAccent),
            const SizedBox(height: 20),
            const Text(
              "SOUL-LINK SYSTEM",
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                letterSpacing: 4,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Text(
              "V1.5.3-P PHOENIX RISING",
              style: TextStyle(
                color: Colors.cyanAccent,
                fontSize: 10,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 60),
            TextField(
              controller: _usernameController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "ENTER IDENTIFIER",
                hintStyle: const TextStyle(color: Colors.white24),
                filled: true,
                fillColor: Colors.white.withOpacity(0.05),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(15),
                  borderSide: BorderSide.none,
                ),
                prefixIcon: const Icon(
                  Icons.person_outline,
                  color: Colors.cyanAccent,
                ),
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: _isConnecting ? null : _initiateLink,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
                child: _isConnecting
                    ? const CircularProgressIndicator(color: Colors.black)
                    : const Text(
                        "INITIATE LINK",
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
