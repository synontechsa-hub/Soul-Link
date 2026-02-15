// lib/screens/apartment_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/modals/mirror_edit_modal.dart';
import '../widgets/hub_tile.dart';
import '../services/ad_service.dart';

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
            style: TextStyle(
              letterSpacing: 2,
              fontWeight: FontWeight.w900,
              fontSize: 16,
            ),
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
              imagePath: '/assets/images/user_loft/bed_pod.jpg',
              onTap: () => _handleEndTurn(context),
            ),
            HubTile(
              icon: Icons.face,
              label: "MIRROR",
              subtitle: "Persona Config",
              color: Colors.cyanAccent,
              imagePath: '/assets/images/user_loft/smart_mirror.jpg',
              onTap: () => _showMirrorDialog(context),
            ),
            HubTile(
              icon: Icons.checkroom,
              label: "WARDROBE",
              subtitle: "Skins & Outfits",
              color: Colors.pinkAccent,
              imagePath: '/assets/images/user_loft/persona_wardrobe.jpg',
              onTap: () => _showWardrobeDialog(context),
            ),
            HubTile(
              icon: Icons.kitchen,
              label: "FRIDGE",
              subtitle: "Buffs & Energy",
              color: Colors.greenAccent,
              imagePath: '/assets/images/user_loft/energy_fridge.jpg',
              onTap: () => _showFridgeDialog(context),
            ),
            HubTile(
              icon: Icons.radio,
              label: "RADIO",
              subtitle: "Manual Tuning",
              color: Colors.orangeAccent,
              imagePath: '/assets/images/user_loft/retro_radio.jpg',
              onTap: () => _showRadioDialog(context),
            ),
            HubTile(
              icon: Icons.tv,
              label: "TELEVISION",
              subtitle: "Ads & Lore",
              color: Colors.purpleAccent,
              imagePath: '/assets/images/user_loft/lofi_tv.jpg',
              onTap: () => _showTVDialog(context),
            ),
            HubTile(
              icon: Icons.collections,
              label: "MEMORY WALL",
              subtitle: "Milestones",
              color: Colors.amberAccent,
              imagePath: '/assets/images/user_loft/memory_wall.jpg',
              onTap: () => _showMemoryWallDialog(context),
            ),
            HubTile(
              icon: Icons.weekend,
              label: "COUCH",
              subtitle: "Wait for Guests",
              color: Colors.brown,
              imagePath: '/assets/images/user_loft/neuro_couch.jpg',
              onTap: () {},
            ),
            HubTile(
              icon: Icons.window,
              label: "WINDOW",
              subtitle: "The City Deep",
              color: Colors.blue,
              imagePath: '/assets/images/user_loft/city_window.jpg',
              onTap: () {},
            ),
            HubTile(
              icon: Icons.logout,
              label: "DOOR",
              subtitle: "Terminate",
              color: Colors.redAccent,
              imagePath: '/assets/images/user_loft/bulkhead_door.jpg',
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
            child: const Text(
              "CANCEL",
              style: TextStyle(color: Colors.white38),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text(
              "ADVANCE TIME",
              style: TextStyle(color: Colors.cyanAccent),
            ),
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
          content: Text(
            "TIME ADVANCED: ${result['new_time_slot'].toString().toUpperCase()}",
          ),
          backgroundColor: Colors.blueAccent,
        ),
      );

      provider.syncDashboard();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Failed to advance time: $e"),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _handleLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Text(
          "TERMINATE SESSION?",
          style: TextStyle(color: Colors.white),
        ),
        content: const Text(
          "Are you sure you want to go to sleep?",
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              "STAY AWAKE",
              style: TextStyle(color: Colors.cyanAccent),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Provider.of<DashboardProvider>(context, listen: false).logout();
              Navigator.of(context).popUntil((route) => route.isFirst);
            },
            child: const Text(
              "LOGOUT",
              style: TextStyle(color: Colors.redAccent),
            ),
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
            Text(
              "MANUAL TUNING",
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                letterSpacing: 2,
              ),
            ),
          ],
        ),
        content: Text(
          broadcasts[random],
          style: const TextStyle(
            color: Colors.orangeAccent,
            fontStyle: FontStyle.italic,
            fontFamily: 'monospace',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("CLOSE", style: TextStyle(color: Colors.white38)),
          ),
        ],
      ),
    );
  }

  void _showTVDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Row(
          children: [
            Icon(Icons.tv, color: Colors.purpleAccent),
            SizedBox(width: 12),
            Text(
              "INCOMING SIGNAL",
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                letterSpacing: 2,
              ),
            ),
          ],
        ),
        content: const Text(
          "Encrypted transmission detected on secure channel.\n\nREWARD: +50 Signal Stability",
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              "IGNORE",
              style: TextStyle(color: Colors.white38),
            ),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _playAd(context);
            },
            child: const Text(
              "DECRYPT (WATCH AD)",
              style: TextStyle(color: Colors.cyanAccent),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _playAd(BuildContext context) async {
    final adService = Provider.of<AdService>(context, listen: false);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Accessing Neural Network..."),
        duration: Duration(seconds: 1),
        backgroundColor: Colors.purpleAccent,
      ),
    );

    final success = await adService.showAd(
      AdType.rewarded,
      onReward: (type, amount) {
        if (!mounted) return;
        _showRewardDialog(context, type, amount);
      },
    );

    if (!success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Signal lost. Ad failed to load."),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _showRewardDialog(BuildContext context, String type, int amount) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Text(
          "TRANSMISSION COMPLETE",
          style: TextStyle(color: Colors.greenAccent),
        ),
        content: Text(
          "Signal Stabilized!\n+$amount Stability restored.",
          style: const TextStyle(color: Colors.white),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("ACCEPT"),
          ),
        ],
      ),
    );
  }

  void _showFridgeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Row(
          children: [
            Icon(Icons.kitchen, color: Colors.greenAccent),
            SizedBox(width: 12),
            Text(
              "REFRIGERATOR",
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
                letterSpacing: 2,
              ),
            ),
          ],
        ),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: Icon(Icons.flash_on, color: Colors.cyanAccent),
              title: Text(
                "Energy Bottle",
                style: TextStyle(color: Colors.white),
              ),
              subtitle: Text(
                "Restores 20 Energy",
                style: TextStyle(color: Colors.white54),
              ),
            ),
            ListTile(
              leading: Icon(Icons.star, color: Colors.amberAccent),
              title: Text("Synth-Fruit", style: TextStyle(color: Colors.white)),
              subtitle: Text(
                "+1 Charisma Buff (1h)",
                style: TextStyle(color: Colors.white54),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("CLOSE", style: TextStyle(color: Colors.white38)),
          ),
        ],
      ),
    );
  }

  void _showWardrobeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => const SimpleDialog(
        backgroundColor: Color(0xFF1A1A22),
        title: Text("WARDROBE", style: TextStyle(color: Colors.pinkAccent)),
        children: [
          Padding(
            padding: EdgeInsets.all(16),
            child: Text(
              "Skins system coming soon in v1.6.0...",
              style: TextStyle(color: Colors.white54),
            ),
          ),
        ],
      ),
    );
  }

  void _showMemoryWallDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => const SimpleDialog(
        backgroundColor: Color(0xFF1A1A22),
        title: Text("MEMORY WALL", style: TextStyle(color: Colors.amberAccent)),
        children: [
          Padding(
            padding: EdgeInsets.all(16),
            child: Text(
              "Snapshots gallery coming soon...",
              style: TextStyle(color: Colors.white54),
            ),
          ),
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
