// frontend/lib/screens/settings_screen.dart
// version.py
// _dev/

import 'package:flutter/material.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _nsfwEnabled = false; // The Master Toggle

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ARCHITECT CONTROLS', style: TextStyle(letterSpacing: 2)),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildSectionHeader("CONTENT FILTERS"),
          SwitchListTile(
            title: const Text("ADULT CONTENT (NSFW)", style: TextStyle(color: Colors.white)),
            subtitle: const Text("Unlock uncensored interactions with Souls.", style: TextStyle(fontSize: 11, color: Colors.white38)),
            value: _nsfwEnabled,
            activeThumbColor: Colors.redAccent,
            onChanged: (val) => setState(() => _nsfwEnabled = val),
          ),
          const Divider(color: Colors.white10),
          
          _buildSectionHeader("SYSTEM STATUS"),
          const ListTile(
            leading: Icon(Icons.terminal, color: Colors.cyanAccent),
            title: Text("LEGION ENGINE V1.5.3-P"),
            subtitle: Text("Connected: USR-001 (Architect)"),
          ),
          const Divider(color: Colors.white10),

          _buildSectionHeader("ACCOUNT"),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.white38),
            title: const Text("TERMINATE SESSION", style: TextStyle(color: Colors.white70)),
            onTap: () {
              // Future Logout Logic
            },
          ),
          const SizedBox(height: 50),
          const Center(
            child: Text("SOULLINK PHOENIX — MADE BY THE ARCHITECT", 
              style: TextStyle(color: Colors.white10, fontSize: 10, letterSpacing: 2)),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Text(title, style: const TextStyle(color: Colors.cyanAccent, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.5)),
    );
  }
}