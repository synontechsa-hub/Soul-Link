// frontend/lib/screens/login_screen.dart
// version.py v1.5.3-P

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../services/auth_service.dart';
import '../providers/dashboard_provider.dart';
import '../core/version.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final AuthService _auth = AuthService();
  bool _isLoading = false;

  // New requirement: 3 Options
  // 1. Guest
  // 2. Email
  // 3. Social (Placeholder)

  Future<void> _handleGuestLogin() async {
    setState(() => _isLoading = true);
    try {
      await _auth.signInAnonymously();
      if (mounted) {
        // Trigger the provider to fetch profile (JIT sync on backend)
        await Provider.of<DashboardProvider>(context, listen: false).initAfterAuth();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Guest Login Failed: $e"), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showEmailLoginDialog() {
    showDialog(
      context: context,
      builder: (context) => const _EmailLoginDialog(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.hub, size: 80, color: Colors.cyanAccent),
              const SizedBox(height: 24),
              const Text(
                "SOUL-LINK SYSTEM",
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 4,
                ),
              ),
              Text(
                SoulLinkVersion.displayVersion.toUpperCase(),
                style: const TextStyle(
                  color: Colors.cyanAccent,
                  fontSize: 10,
                  letterSpacing: 2,
                ),
              ),
              const SizedBox(height: 64),

              if (_isLoading)
                const CircularProgressIndicator(color: Colors.cyanAccent)
              else ...[
                // 1. GUEST OPTION (Primary)
                _LoginButton(
                  label: "CONTINUE AS GUEST",
                  icon: Icons.person_outline,
                  color: Colors.cyanAccent,
                  textColor: Colors.black,
                  onPressed: _handleGuestLogin,
                ),
                const SizedBox(height: 16),

                // 2. EMAIL OPTION
                _LoginButton(
                  label: "LOGIN / REGISTER",
                  icon: Icons.email_outlined,
                  color: Colors.white10,
                  textColor: Colors.white,
                  onPressed: _showEmailLoginDialog,
                ),
                const SizedBox(height: 16),

                // 3. SOCIAL OPTION (Placeholder)
                const Opacity(
                  opacity: 0.5,
                  child: _LoginButton(
                    label: "SOCIAL LOGIN (Coming Soon)",
                    icon: Icons.public,
                    color: Colors.transparent,
                    textColor: Colors.white54,
                    onPressed: null, // Disabled
                  ),
                ),
              ]
            ],
          ),
        ),
      ),
    );
  }
}

class _LoginButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final Color textColor;
  final VoidCallback? onPressed;

  const _LoginButton({
    required this.label,
    required this.icon,
    required this.color,
    required this.textColor,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton.icon(
        icon: Icon(icon, color: textColor),
        label: Text(label, style: TextStyle(letterSpacing: 1.5, fontWeight: FontWeight.bold)),
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: textColor,
          side: onPressed == null ? const BorderSide(color: Colors.white12) : null,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
    );
  }
}

class _EmailLoginDialog extends StatefulWidget {
  const _EmailLoginDialog();

  @override
  State<_EmailLoginDialog> createState() => _EmailLoginDialogState();
}

class _EmailLoginDialogState extends State<_EmailLoginDialog> {
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final AuthService _auth = AuthService();
  bool _isLoading = false;
  bool _isRegistering = false;

  Future<void> _submit() async {
    final email = _emailCtrl.text.trim();
    final pass = _passCtrl.text.trim();
    if (email.isEmpty || pass.isEmpty) return;

    setState(() => _isLoading = true);
    try {
      if (_isRegistering) {
        await _auth.signUpWithEmail(email, pass);
        if (mounted) {
           Navigator.pop(context);
           ScaffoldMessenger.of(context).showSnackBar(
             const SnackBar(content: Text("Account Created! Please Login.")),
           );
        }
      } else {
        await _auth.signInWithEmail(email, pass);
        if (mounted) {
           Navigator.pop(context);
           await Provider.of<DashboardProvider>(context, listen: false).initAfterAuth();
        }
      }
    } on AuthException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: $e"), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1A1A22),
      title: Text(
        _isRegistering ? "CREATE ACCOUNT" : "LOGIN",
        style: const TextStyle(color: Colors.white, letterSpacing: 2, fontSize: 18),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _emailCtrl,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "EMAIL",
              labelStyle: TextStyle(color: Colors.white54),
              enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white24)),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _passCtrl,
            obscureText: true,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              labelText: "PASSWORD",
              labelStyle: TextStyle(color: Colors.white54),
              enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white24)),
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => setState(() => _isRegistering = !_isRegistering),
          child: Text(
            _isRegistering ? "Have an account? Login" : "No account? Register",
            style: const TextStyle(color: Colors.white54),
          ),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submit,
          style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent, foregroundColor: Colors.black),
          child: _isLoading 
            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) 
            : Text(_isRegistering ? "REGISTER" : "LOGIN"),
        ),
      ],
    );
  }
}
