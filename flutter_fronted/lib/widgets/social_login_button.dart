import 'package:flutter/material.dart';

class SocialLoginButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const SocialLoginButton({
    required this.label,
    required this.onTap,
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onTap,
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF7E57C2),
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
      ),
      child: Text(label, style: const TextStyle(color: Colors.white)),
    );
  }
}
