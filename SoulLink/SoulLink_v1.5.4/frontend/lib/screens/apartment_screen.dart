import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/modals/mirror_edit_modal.dart';
import '../widgets/hub_tile.dart';

class ApartmentScreen extends StatefulWidget {
  const ApartmentScreen({super.key});

  @override
  State<ApartmentScreen> createState() => _ApartmentScreenState();
}

class _ApartmentScreenState extends State<ApartmentScreen> {
  @override
  Widget build(BuildContext context) {
    return Hero(
      tag: 'location_linkside_apartment',
      child: Scaffold(
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
            HubTile(
              icon: Icons.hotel,
              label: "BED",
              subtitle: "End Turn",
              color: Colors.blueAccent,
              onTap: () => _handleEndTurn(context),
            ),
            HubTile(
              icon: Icons.face,
              label: "MIRROR",
              subtitle: "Persona Config",
              color: Colors.cyanAccent,
              onTap: () => _showMirrorDialog(context),
            ),
            HubTile(
              icon: Icons.radio,
              label: "RADIO",
              subtitle: "Manual Tuning",
              color: Colors.orangeAccent,
              onTap: () => _showRadioDialog(context),
            ),
            HubTile(
              icon: Icons.tv,
              label: "TELEVISION",
              subtitle: "No Signal",
              color: Colors.purpleAccent.withOpacity(0.3),
              onTap: () {},
            ),
            HubTile(
              icon: Icons.weekend,
              label: "COUCH",
              subtitle: "Wait for Guests",
              color: Colors.brown.withOpacity(0.3),
              onTap: () {},
            ),
            HubTile(
              icon: Icons.window,
              label: "WINDOW",
              subtitle: "The City Deep",
              color: Colors.blueAccent.withOpacity(0.3),
              onTap: () {},
            ),
            HubTile(
              icon: Icons.logout,
              label: "DOOR",
              subtitle: "Logout",
              color: Colors.redAccent,
              onTap: () => _handleLogout(context),
            ),
          ],
        ),
      ),
    );
  }


  Future<void> _handleEndTurn(BuildContext context) async {
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Text("END TURN?", style: TextStyle(color: Colors.white)),
        content: const Text(
          "Advance time to the next slot?\nSouls will move to their routine locations.",
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("CANCEL", style: TextStyle(color: Colors.white38)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text("ADVANCE TIME", style: TextStyle(color: Colors.cyanAccent)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final result = await provider.apiService.advanceTimeSlot();
      if (!mounted) return;
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("TIME ADVANCED: ${result['new_time_slot'].toString().toUpperCase()}"),
          backgroundColor: Colors.blueAccent,
        ),
      );
      
      provider.syncDashboard();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Failed to advance time: $e"), backgroundColor: Colors.red),
        );
      }
    }
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
          style: const TextStyle(color: Colors.orangeAccent, fontStyle: FontStyle.italic, fontFamily: 'monospace'),
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
      builder: (context) => const MirrorEditModal(),
    );
  }
}

