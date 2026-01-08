import 'package:flutter/material.dart';
import 'dart:ui'; // Required for Glassmorphism (BackdropFilter)
import '../services/auth_service.dart';
import '../widgets/social_login_button.dart';
import '../home/home_screen.dart'; // Navigate to Home after login

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final auth = AuthService();
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  bool _isLoading = false;

  void handleGuestLogin() async {
    setState(() => _isLoading = true);
    await auth.loginAsGuest();
    if (!mounted) return;
    
    // Smooth transition to the main hub
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => HomeScreen(session: auth.session)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // ─────────────────────────────────────────────
          // 🖼️ BACKGROUND: THE POSTER GIRL
          // ─────────────────────────────────────────────
          Positioned.fill(
            child: Image.asset(
              'assets/images/poster_girl.jpg', // Path to your art
              fit: BoxFit.cover,
            ),
          ),

          // ─────────────────────────────────────────────
          // 🎭 GRADIENT OVERLAY (For Text Readability)
          // ─────────────────────────────────────────────
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.black.withOpacity(0.2),
                    Colors.black.withOpacity(0.8),
                    Colors.black,
                  ],
                ),
              ),
            ),
          ),

          // ─────────────────────────────────────────────
          // 🧪 LOGIN FORM (GLASSMORPHIC)
          // ─────────────────────────────────────────────
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 30),
              child: Column(
                children: [
                  const Spacer(),
                  
                  // LOGO / BRANDING
                  const Text(
                    "SoulLink",
                    style: TextStyle(
                      fontSize: 48, 
                      fontWeight: FontWeight.w900, 
                      color: Colors.white,
                      letterSpacing: 4,
                    ),
                  ),
                  const Text(
                    "SYNCHRONIZE YOUR IDENTITY",
                    style: TextStyle(color: Colors.blueAccent, letterSpacing: 2, fontSize: 10),
                  ),
                  
                  const SizedBox(height: 40),

                  // EMAIL FIELD
                  _buildGlassField(
                    controller: emailController,
                    hint: "Neural Email",
                    icon: Icons.alternate_email,
                  ),
                  const SizedBox(height: 15),

                  // PASSWORD FIELD
                  _buildGlassField(
                    controller: passwordController,
                    hint: "Access Key",
                    icon: Icons.lock_outline,
                    isPassword: true,
                  ),

                  const SizedBox(height: 25),

                  // LOGIN BUTTON
                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton(
                      onPressed: () {}, 
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blueAccent,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                      ),
                      child: const Text("INITIALIZE LINK", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                    ),
                  ),

                  const SizedBox(height: 20),

                  // SOCIAL LOGINS
                  Row(
                    children: [
                      const Expanded(child: Divider(color: Colors.white24)),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        child: Text("OR JOIN AS", style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 10)),
                      ),
                      const Expanded(child: Divider(color: Colors.white24)),
                    ],
                  ),

                  const SizedBox(height: 20),

                  SocialLoginButton(
                    label: "GUEST WANDERER", 
                    onTap: handleGuestLogin,
                  ),

                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
          
          if (_isLoading)
            const Center(child: CircularProgressIndicator(color: Colors.blueAccent)),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────
  // 🧬 GLASSMORPHISM WIDGET HELPER
  // ─────────────────────────────────────────────
  Widget _buildGlassField({
    required TextEditingController controller,
    required String hint,
    required IconData icon,
    bool isPassword = false,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(15),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            border: Border.all(color: Colors.white.withOpacity(0.1)),
            borderRadius: BorderRadius.circular(15),
          ),
          child: TextField(
            controller: controller,
            obscureText: isPassword,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              prefixIcon: Icon(icon, color: Colors.white54, size: 20),
              hintText: hint,
              hintStyle: const TextStyle(color: Colors.white24),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(vertical: 15),
            ),
          ),
        ),
      ),
    );
  }
}