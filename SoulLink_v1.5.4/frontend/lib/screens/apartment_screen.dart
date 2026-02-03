// frontend/lib/screens/apartment_screen.dart
// version.py v1.5.4 Arise

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';

class ApartmentScreen extends StatefulWidget {
  const ApartmentScreen({super.key});

  @override
  State<ApartmentScreen> createState() => _ApartmentScreenState();
}

class _ApartmentScreenState extends State<ApartmentScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A22),
        elevation: 0,
        title: const Text(
          'LINKSIDE APARTMENT',
          style: TextStyle(letterSpacing: 2, fontWeight: FontWeight.w900, fontSize: 16),
        ),
      ),
      body: GridView.count(
        padding: const EdgeInsets.all(24),
        crossAxisCount: 2,
        mainAxisSpacing: 20,
        crossAxisSpacing: 20,
        children: [
          _buildHubItem(
            context,
            icon: Icons.bed,
            label: "BED",
            subtitle: "Terminate Session",
            color: Colors.redAccent,
            onTap: () => _handleLogout(context),
          ),
          _buildHubItem(
            context,
            icon: Icons.face,
            label: "MIRROR",
            subtitle: "Persona Config",
            color: Colors.cyanAccent,
            onTap: () => _showMirrorDialog(context),
          ),
          _buildHubItem(
            context,
            icon: Icons.radio,
            label: "RADIO",
            subtitle: "Manual Tuning",
            color: Colors.orangeAccent,
            onTap: () => _showRadioDialog(context),
          ),
          _buildHubItem(
            context,
            icon: Icons.tv,
            label: "TELEVISION",
            subtitle: "No Signal",
            color: Colors.purpleAccent.withOpacity(0.3),
            onTap: () {},
          ),
          _buildHubItem(
            context,
            icon: Icons.weekend,
            label: "COUCH",
            subtitle: "Wait for Guests",
            color: Colors.brown.withOpacity(0.3),
            onTap: () {},
          ),
          _buildHubItem(
            context,
            icon: Icons.window,
            label: "WINDOW",
            subtitle: "The City Deep",
            color: Colors.blueAccent.withOpacity(0.3),
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildHubItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A22),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withOpacity(0.2), width: 1.5),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 12),
            Text(
              label,
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, letterSpacing: 1),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(color: Colors.white24, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }

  void _handleLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Text("TERMINATE SESSION?", style: TextStyle(color: Colors.white)),
        content: const Text("Are you sure you want to go to sleep?", style: TextStyle(color: Colors.white70)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("STAY AWAKE", style: TextStyle(color: Colors.cyanAccent)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Provider.of<DashboardProvider>(context, listen: false).logout();
              Navigator.of(context).popUntil((route) => route.isFirst);
            },
            child: const Text("LOGOUT", style: TextStyle(color: Colors.redAccent)),
          ),
        ],
      ),
    );
  }

  void _showRadioDialog(BuildContext context) {
    final broadcasts = [
      "CRITICAL: Soul presence detected in Sector 7. Avoid the Skylink Tower.",
      "WEATHER: Synth-rain expected at 22:00. Watch your chronos.",
      "THE ARCHITECT: 'The cycle ends here. We must be better.'",
      "STATIC: ...link established... signal unstable...",
      "AD: Visit Crimson Arms. Where memories never fade.",
      "LORE: They say the Seven were never humans. Just prototypes.",
      "RADIO: Frequency 104.2 — Play it loud, play it deep.",
    ];
    final random = (DateTime.now().millisecondsSinceEpoch % broadcasts.length);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Row(
          children: [
            Icon(Icons.radio, color: Colors.orangeAccent),
            SizedBox(width: 12),
            Text("MANUAL TUNING", style: TextStyle(color: Colors.white, fontSize: 14, letterSpacing: 2)),
          ],
        ),
        content: Text(
          broadcasts[random],
          style: const TextStyle(color: Colors.orangeAccent, fontStyle: FontStyle.italic, family: 'monospace'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text("CLOSE", style: TextStyle(color: Colors.white38))),
        ],
      ),
    );
  }

  void _showMirrorDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const _MirrorModal(),
    );
  }
}

class _MirrorModal extends StatefulWidget {
  const _MirrorModal();

  @override
  State<_MirrorModal> createState() => _MirrorModalState();
}

class _MirrorModalState extends State<_MirrorModal> {
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
      setState(() {
        _nameCtrl.text = user.display_name ?? "";
        _bioCtrl.text = user.bio ?? "";
        _gender = user.genderIdentity ?? "Not Specified";
        _isLoading = false;
      });
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