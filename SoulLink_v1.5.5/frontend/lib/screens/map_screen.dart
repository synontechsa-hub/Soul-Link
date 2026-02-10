// frontend/lib/screens/map_screen.dart
// version.py v1.5.4 Arise

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/relationship.dart';
import '../core/version.dart';
import '../core/config.dart';
import '../widgets/map/radar_selector.dart';
import '../widgets/map/tactical_node.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  String? _selectedSoulId;
  List<dynamic> _locations = [];
  bool _isLoadingLocs = true;

  @override
  void initState() {
    super.initState();
    _fetchLocations();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final provider = Provider.of<DashboardProvider>(context);
    final user = provider.currentUser;
    // Note: We no longer need to check local _currentTimeSlot
    if (user != null && !_isLoadingLocs) {
       // Check if we need to refresh (implement more precise checking if needed)
       // For now, if the user state changed, we might want to refresh
    }
  }

  Future<void> _fetchLocations() async {
    final api = Provider.of<DashboardProvider>(context, listen: false).apiService;
    try {
      final data = await api.getMapLocations();
      if (mounted) {
        setState(() {
          _locations = data;
          _isLoadingLocs = false;
        });
      }
    } catch (e) {
      debugPrint("🛰️ MAP RADAR FAILURE: $e");
      if (mounted) setState(() => _isLoadingLocs = false);
    }
  }

  Future<void> _moveSoulTo(String locationId, String locationName) async {
    if (_selectedSoulId == null) return;
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    try {
      await provider.apiService.moveSoul(soulId: _selectedSoulId!, locationId: locationId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("SIGNAL REROUTED: SOUL MOVING TO $locationName"), backgroundColor: Colors.cyan[900]),
      );
      provider.syncDashboard();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("MOVE FAILED: $e")));
    }
  }

  Future<void> _moveUserTo(BuildContext modalContext, String locationId, String locationName) async {
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    try {
      await provider.apiService.moveUser(locationId: locationId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("IDENTITY TRANSMARKED: YOU ENTERED $locationName"), backgroundColor: Colors.green),
      );
      provider.refreshUser();
      Navigator.pop(modalContext); // Close modal using its own context
    } catch (e) {
      if (mounted) Navigator.pop(modalContext); // Close anyway on error if mounted
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("USER MOVE FAILED: $e")));
    }
  }

  void _showLocationDetails(dynamic loc, List<SoulRelationship> allSouls) {
    final soulsHere = allSouls.where((s) => s.currentLocation == loc['location_id']).toList();
    
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: Color(0xFF1A1A22),
          borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text((loc['display_name'] ?? loc['name'] ?? 'UNKNOWN').toString().toUpperCase(), style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 18, letterSpacing: 2)),
            Text(loc['desc'] ?? "Scanning sector... Signal strength nominal.", style: const TextStyle(color: Colors.white38, fontSize: 12)),
            const Divider(color: Colors.white10, height: 30),
            const Text("SIGNALS DETECTED:", style: TextStyle(color: Colors.white54, fontSize: 10, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            if (soulsHere.isEmpty)
              const Text("NO SOULS DETECTED IN SECTOR", style: TextStyle(color: Colors.white10, fontSize: 12))
            else
              SizedBox(
                height: 60,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: soulsHere.length,
                  itemBuilder: (context, i) => Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: CircleAvatar(
                      radius: 20,
                      backgroundColor: Colors.cyanAccent.withOpacity(0.2),
                      backgroundImage: (soulsHere[i].portrait_url.isNotEmpty) ? NetworkImage(AppConfig.getImageUrl(soulsHere[i].portrait_url)) : null,
                      child: soulsHere[i].portrait_url.isEmpty ? const Icon(Icons.person, color: Colors.white38) : null,
                    ),
                  ),
                ),
              ),
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.location_on),
                label: const Text("ENTER LOCATION", style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.5)),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.cyanAccent, foregroundColor: Colors.black),
                onPressed: () => _moveUserTo(context, loc['location_id'], loc['display_name'] ?? loc['name'] ?? 'UNKNOWN'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardProvider>();
    final state = dashboard.state;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      appBar: AppBar(
        title: Text(
          'CITY RADAR — ${SoulLinkVersion.codename.toUpperCase()}',
          style: const TextStyle(letterSpacing: 2, fontWeight: FontWeight.w900, fontSize: 16),
        ),
        backgroundColor: const Color(0xFF1A1A22),
        elevation: 0,
      ),
      body: Column(
        children: [
          if (state != null && dashboard.currentUser?.accountTier == 'architect')
            RadarSelector(
              souls: state.activeSouls,
              selectedSoulId: _selectedSoulId,
              onSoulSelected: (id) => setState(() => _selectedSoulId = id),
            ),
          Expanded(
            child: _isLoadingLocs
                ? const Center(child: CircularProgressIndicator(color: Colors.cyanAccent))
                : GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      childAspectRatio: 0.85,
                    ),
                    itemCount: _locations.length,
                    itemBuilder: (context, index) => TacticalNode(
                      loc: _locations[index],
                      allSouls: state?.activeSouls ?? [],
                      selectedSoulId: _selectedSoulId,
                      onMoveSoul: _moveSoulTo,
                      onShowDetails: _showLocationDetails,
                    ),
                  ),
          ),
        ],
      ),
    );
  }


  // Get time slot display info
  Map<String, dynamic> _getTimeSlotInfo(String timeSlot) {
    switch (timeSlot) {
      case 'morning':
        return {
          'name': 'Morning',
          'description': 'The city awakens to neon dawn',
          'icon': Icons.wb_sunny,
          'colors': [const Color(0xFFFF6B35), const Color(0xFFFFAA00)],
        };
      case 'afternoon':
        return {
          'name': 'Afternoon',
          'description': 'Peak activity across all sectors',
          'icon': Icons.wb_sunny_outlined,
          'colors': [const Color(0xFF00D9FF), const Color(0xFF0099FF)],
        };
      case 'evening':
        return {
          'name': 'Evening',
          'description': 'Golden hour descends on Link City',
          'icon': Icons.wb_twilight,
          'colors': [const Color(0xFFFF6B9D), const Color(0xFFC06C84)],
        };
      case 'night':
        return {
          'name': 'Night',
          'description': 'Neon lights illuminate the darkness',
          'icon': Icons.nightlight_round,
          'colors': [const Color(0xFF6B5B95), const Color(0xFF2A1B3D)],
        };
      case 'home_time':
        return {
          'name': 'Home Time',
          'description': 'The city sleeps, souls return home',
          'icon': Icons.bedtime,
          'colors': [const Color(0xFF1A1A2E), const Color(0xFF0F0F1E)],
        };
      default:
        return {
          'name': 'Unknown',
          'description': 'Time data unavailable',
          'icon': Icons.access_time,
          'colors': [const Color(0xFF1A1A22), const Color(0xFF0A0A0E)],
        };
    }
  }
}
