import 'package:flutter/material.dart';
import '../../state/app_session.dart';

// ─────────────────────────────────────────────
// 👤 PROFILE SCREEN (USER IDENTITY & CARDS)
// ─────────────────────────────────────────────

class ProfileScreen extends StatefulWidget {
  final AppSession session;
  const ProfileScreen({super.key, required this.session});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  // 🧠 LOCAL STATE for editing (Would eventually sync to AppSession)
  late TextEditingController _nameController;
  late TextEditingController _bioController;
  String _selectedGender = "Neutral";
  int _age = 21;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: "Soul Wanderer");
    _bioController = TextEditingController(text: "Exploring the digital rift...");
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("Your Soul ID"),
        backgroundColor: Colors.black,
        actions: [
          TextButton(onPressed: () => _saveProfile(), child: const Text("SAVE")),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ─────────────────────────────────────────────
            // 🖼️ USER AVATAR SECTION
            // ─────────────────────────────────────────────
            Center(
              child: Stack(
                children: [
                  CircleAvatar(
                    radius: 60,
                    backgroundColor: Colors.purple.shade900,
                    child: const Icon(Icons.person, size: 60, color: Colors.white),
                  ),
                  Positioned(
                    bottom: 0, right: 0,
                    child: CircleAvatar(
                      backgroundColor: Colors.blueAccent,
                      radius: 18,
                      child: IconButton(
                        icon: const Icon(Icons.camera_alt, size: 18, color: Colors.white),
                        onPressed: () {}, // Future: Image Picker
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // ─────────────────────────────────────────────
            // 📝 IDENTITY FIELDS
            // ─────────────────────────────────────────────
            _buildSectionTitle("Personal Data"),
            _buildTextField("Display Name", _nameController),
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(child: _buildAgePicker()),
                const SizedBox(width: 16),
                Expanded(child: _buildGenderDropdown()),
              ],
            ),
            const SizedBox(height: 16),
            _buildTextField("Soul Bio", _bioController, maxLines: 3),

            const SizedBox(height: 40),

            // ─────────────────────────────────────────────
            // 🃏 SOUL COLLECTION (UNLOCKED CARDS)
            // ─────────────────────────────────────────────
            _buildSectionTitle("Unlocked Souls"),
            const SizedBox(height: 12),
            _buildCardCollection(),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────
  // 🧬 UI HELPER METHODS
  // ─────────────────────────────────────────────

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(title.toUpperCase(), 
        style: const TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold, letterSpacing: 1.5, fontSize: 12)),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, {int maxLines = 1}) {
    return TextField(
      controller: controller,
      maxLines: maxLines,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.grey),
        enabledBorder: OutlineInputBorder(borderSide: const BorderSide(color: Colors.white12), borderRadius: BorderRadius.circular(12)),
        focusedBorder: OutlineInputBorder(borderSide: const BorderSide(color: Colors.purple), borderRadius: BorderRadius.circular(12)),
        filled: true,
        fillColor: Colors.white.withOpacity(0.05),
      ),
    );
  }

  Widget _buildAgePicker() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("Age", style: TextStyle(color: Colors.grey, fontSize: 12)),
        Slider(
          value: _age.toDouble(),
          min: 18, max: 99,
          divisions: 81,
          label: _age.toString(),
          onChanged: (val) => setState(() => _age = val.toInt()),
        ),
      ],
    );
  }

  Widget _buildGenderDropdown() {
    return DropdownButtonFormField<String>(
      value: _selectedGender,
      dropdownColor: Colors.grey.shade900,
      style: const TextStyle(color: Colors.white),
      decoration: const InputDecoration(labelText: "Gender", labelStyle: TextStyle(color: Colors.grey)),
      items: ["Male", "Female", "Non-Binary", "Neutral"]
          .map((g) => DropdownMenuItem(value: g, child: Text(g))).toList(),
      onChanged: (val) => setState(() => _selectedGender = val!),
    );
  }

  Widget _buildCardCollection() {
    // 🧠 MOCK COLLECTION: In real app, filter session.bots by "unlocked" status
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3, crossAxisSpacing: 10, mainAxisSpacing: 10, childAspectRatio: 0.7,
      ),
      itemCount: widget.session.bots.length,
      itemBuilder: (context, index) {
        final bot = widget.session.bots.values.elementAt(index);
        return Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            image: DecorationImage(image: NetworkImage(bot.avatarUrl), fit: BoxFit.cover),
            border: Border.all(color: Colors.white10),
          ),
          child: Container(
            alignment: Alignment.bottomCenter,
            padding: const EdgeInsets.all(4),
            decoration: const BoxDecoration(
              gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [Colors.transparent, Colors.black]),
            ),
            child: Text(bot.name, style: const TextStyle(fontSize: 10, color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        );
      },
    );
  }

  void _saveProfile() {
    // Logic to update your AppSession/Database
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Soul Identity Synchronized.")));
  }
}