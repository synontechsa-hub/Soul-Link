import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../widgets/social_login_button.dart';
import 'chats/chat_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final auth = AuthService();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  void handleEmailLogin() async {
    await auth.loginWithEmail(emailController.text, passwordController.text);
  }

  void handleGuestLogin() async {
    await auth.loginAsGuest();

    if (!mounted) return;

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => ChatScreen(botName: "Evangeline"),
      ),
    );
  }

  void handleGoogleLogin() async {
    await auth.loginWithGoogle();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E0E11),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              "SoulLink",
              style: TextStyle(fontSize: 32, color: Colors.white),
            ),
            const SizedBox(height: 24),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                hintText: "Email",
                fillColor: Color(0xFFF2F3F6),
                filled: true,
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                hintText: "Password",
                fillColor: Color(0xFFF2F3F6),
                filled: true,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: handleEmailLogin,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFE53935),
              ),
              child: const Text("Login with Email"),
            ),
            const SizedBox(height: 16),
            SocialLoginButton(label: "Google", onTap: handleGoogleLogin),
            SocialLoginButton(
              label: "Continue as Guest",
              onTap: handleGuestLogin,
            ),
          ],
        ),
      ),
    );
  }
}
