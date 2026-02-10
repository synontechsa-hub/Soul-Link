// frontend/lib/screens/dashboard_screen.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/relationship.dart';  // ← Added for SoulRelationship
import './chat_screen.dart';         // ← Kept/confirmed for ChatScreen (assume same dir)

import '../widgets/soul_card.dart';

import '../providers/websocket_provider.dart';
import '../widgets/time_display.dart';  // ← Added TimeDisplay widget

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    // 🔌 Link WebSocket Time Events to Dashboard Sync
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ws = Provider.of<WebSocketProvider>(context, listen: false);
      final dash = Provider.of<DashboardProvider>(context, listen: false);
      
      ws.onTimeAdvance = (data) {
        if (mounted) dash.handleTimeAdvance(data);
      };
    });
  }

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardProvider>();

    return Scaffold(
      backgroundColor: Colors.black, // Keeping that Cyberpunk feel
      appBar: AppBar(
        title: Row(
          children: [
             const TimeDisplay(), // 🕰️ Added Time Display
             const SizedBox(width: 12),
             const Text('LINK CITY', 
              style: TextStyle(letterSpacing: 2.0, fontWeight: FontWeight.bold, fontSize: 16)
            ),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.cyanAccent, size: 20),
            onPressed: () => dashboard.syncDashboard(),
          ),
        ],
      ),
      body: _buildBody(dashboard),
    );
  }

  Widget _buildBody(DashboardProvider dashboard) {
    if (dashboard.isLoading) {
      return const Center(child: CircularProgressIndicator(color: Colors.cyanAccent));
    }

    final state = dashboard.state;
    if (state == null || state.activeSouls.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.sensors_off, size: 48, color: Colors.white.withAlpha(26)),  // ← Fixed opacity (0.1 → 26/255)
            const SizedBox(height: 16),
            const Text("NO ACTIVE SIGNALS", style: TextStyle(color: Colors.white24, letterSpacing: 2)),
            TextButton(
              onPressed: () => dashboard.syncDashboard(), 
              child: const Text("RESCAN CITY", style: TextStyle(color: Colors.cyanAccent))
            )
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: state.activeSouls.length,
      itemBuilder: (context, index) {
        final rel = state.activeSouls[index];
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 12.0),
          child: SoulCard(
            relationship: rel, 
            onTap: () => _openChat(context, rel),
          ),
        );
      },
    );
  }

  void _openChat(BuildContext context, SoulRelationship rel) {  // ← Moved INSIDE the class (before or after build is fine)
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(relationship: rel),
      ),
    );
  }
}