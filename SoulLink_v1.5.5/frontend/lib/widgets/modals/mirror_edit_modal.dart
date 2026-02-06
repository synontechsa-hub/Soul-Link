import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/dashboard_provider.dart';

class MirrorEditModal extends StatefulWidget {
  const MirrorEditModal({super.key});

  @override
  State<MirrorEditModal> createState() => _MirrorEditModalState();
}

class _MirrorEditModalState extends State<MirrorEditModal> {
  final _nameCtrl = TextEditingController();
  final _bioCtrl = TextEditingController();
  String _gender = "Not Specified";
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadPersona();
  }

  Future<void> _loadPersona() async {
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    final user = provider.currentUser;
    if (user != null) {
      if (mounted) {
        setState(() {
          _nameCtrl.text = user.displayName ?? ""; 
          _bioCtrl.text = user.bio ?? "";
          _gender = user.genderIdentity ?? "Not Specified";
          _isLoading = false;
        });
      }
    } else {
      // Fallback: This shouldn't happen if user is logged in
       if (mounted) Navigator.pop(context);
    }
  }

  Future<void> _savePersona() async {
    final api = Provider.of<DashboardProvider>(context, listen: false).apiService;
    try {
      await api.updateUserProfile(
        name: _nameCtrl.text.trim(),
        bio: _bioCtrl.text.trim(),
        gender: _gender,
      );
      if (mounted) {
        await Provider.of<DashboardProvider>(context, listen: false).refreshUser();
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Identity Secured."), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      debugPrint("Sync Failed: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
      decoration: const BoxDecoration(
        color: Color(0xFF0A0A0E),
        borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
      ),
      padding: const EdgeInsets.all(24),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "THE MIRROR",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.cyanAccent, letterSpacing: 4),
            ),
            const Text("PERSONA CONFIG", style: TextStyle(color: Colors.white38, fontSize: 10)),
            const SizedBox(height: 30),
            _buildInput("DISPLAY NAME", _nameCtrl),
            const SizedBox(height: 20),
            _buildInput("BIO", _bioCtrl, maxLines: 3),
            const SizedBox(height: 20),
            const Text("GENDER IDENTITY", style: TextStyle(color: Colors.white38, fontSize: 10)),
            _buildGenderDropdown(),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: _savePersona,
                style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent, foregroundColor: Colors.black),
                child: const Text("UPDATE IDENTITY", style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInput(String label, TextEditingController ctrl, {int maxLines = 1}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.white38, fontSize: 10)),
        const SizedBox(height: 8),
        TextField(
          controller: ctrl,
          maxLines: maxLines,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            filled: true,
            fillColor: const Color(0xFF1A1A22),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
      ],
    );
  }

  Widget _buildGenderDropdown() {
    return DropdownButtonFormField<String>(
      value: _gender,
      dropdownColor: const Color(0xFF1A1A22),
      style: const TextStyle(color: Colors.cyanAccent),
      items: ["Not Specified", "Male", "Female", "Non-Binary", "Cybernetic"]
          .map((g) => DropdownMenuItem(value: g, child: Text(g)))
          .toList(),
      onChanged: (val) => setState(() => _gender = val!),
      decoration: const InputDecoration(enabledBorder: UnderlineInputBorder(borderSide: BorderSide(color: Colors.white10))),
    );
  }
}
