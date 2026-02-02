// frontend/lib/screens/apartment_screen.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';

class ApartmentScreen extends StatefulWidget {
  const ApartmentScreen({super.key});

  @override
  State<ApartmentScreen> createState() => _ApartmentScreenState();
}

class _ApartmentScreenState extends State<ApartmentScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _bioController = TextEditingController();
  String _selectedGender = "Not Specified";
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadPersona();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  // 📡 Step 1: Fetch the "Reflection" from the DB
  Future<void> _loadPersona() async {
    final api = Provider.of<DashboardProvider>(context, listen: false).apiService;
    try {
      final data = await api.getUserProfile();
      if (!mounted) return;

      setState(() {
        _nameController.text = data['display_name'] ?? "";
        _bioController.text = data['bio'] ?? "";
        _selectedGender = data['gender_identity'] ?? "Not Specified";
        _isLoading = false;
      });
    } catch (e) {
      debugPrint("Mirror Error: $e");
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  // ⚡ Step 2: Push the "Sync" to the DB
  Future<void> _savePersona() async {
    final api = Provider.of<DashboardProvider>(context, listen: false).apiService;

    // Early snackbar is safe (before any await)
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Synchronizing Identity..."),
          duration: Duration(seconds: 1),
        ),
      );
    }

    try {
      await api.updateUserProfile(
        name: _nameController.text.trim(),
        bio: _bioController.text.trim(),
        gender: _selectedGender,
      );

      if (!mounted) return;

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Identity Secured in Link City."),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      debugPrint("Profile update failed: $e");
      if (!mounted) return;

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Sync Failed: $e"),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Colors.black,
        body: Center(child: CircularProgressIndicator(color: Colors.cyanAccent)),
      );
    }

    return Scaffold(
      backgroundColor: Colors.black,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 60),
            const Text(
              "THE MIRROR",
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                letterSpacing: 4,
                color: Colors.cyanAccent,
              ),
            ),
            const Text(
              "PERSONA CONFIGURATION",
              style: TextStyle(fontSize: 10, color: Colors.white38, letterSpacing: 2),
            ),
            const SizedBox(height: 40),

            _buildLabel("DISPLAY NAME"),
            TextField(
              controller: _nameController,
              style: const TextStyle(color: Colors.white),
              decoration: _inputDecoration("Who are you in the city?"),
              textCapitalization: TextCapitalization.words,
            ),

            const SizedBox(height: 25),

            _buildLabel("BIO / NEURAL TRACE"),
            TextField(
              controller: _bioController,
              maxLines: 3,
              style: const TextStyle(color: Colors.white),
              decoration: _inputDecoration("Tell the souls about yourself..."),
            ),

            const SizedBox(height: 25),

            _buildLabel("GENDER IDENTITY"),
            Theme(
              data: Theme.of(context).copyWith(canvasColor: const Color(0xFF1A1A22)),
              child: DropdownButtonFormField<String>(
                initialValue: _selectedGender,  // ← Changed from value:
                style: const TextStyle(color: Colors.cyanAccent),
                decoration: _inputDecoration(""),
                items: const [
                  DropdownMenuItem(value: "Not Specified", child: Text("Not Specified")),
                  DropdownMenuItem(value: "Male", child: Text("Male")),
                  DropdownMenuItem(value: "Female", child: Text("Female")),
                  DropdownMenuItem(value: "Non-Binary", child: Text("Non-Binary")),
                  DropdownMenuItem(value: "Cybernetic", child: Text("Cybernetic")),
                ],
                onChanged: (val) {
                  if (val != null) setState(() => _selectedGender = val);
                },
              ),
            ),

            const SizedBox(height: 50),

            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: _savePersona,
                child: const Text(
                  "UPDATE IDENTITY",
                  style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 2),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLabel(String text) => Padding(
        padding: const EdgeInsets.only(bottom: 8.0),
        child: Text(
          text,
          style: const TextStyle(
            color: Colors.white38,
            fontSize: 10,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
          ),
        ),
      );

  InputDecoration _inputDecoration(String hint) => InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white10),
        filled: true,
        fillColor: const Color(0xFF1A1A22),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
        contentPadding: const EdgeInsets.all(16),
      );
}