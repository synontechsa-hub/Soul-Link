// frontend/lib/screens/map_screen.dart
// version.py v1.5.4 Arise

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/relationship.dart';
import '../core/version.dart';

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

  Future<void> _moveUserTo(String locationId, String locationName) async {
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    try {
      await provider.apiService.moveUser(locationId: locationId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("IDENTITY TRANSMARKED: YOU ENTERED $locationName"), backgroundColor: Colors.green),
      );
      provider.refreshUser();
      Navigator.pop(context); // Close modal
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("USER MOVE FAILED: $e")));
    }
  }

  void _showLocationDetails(dynamic loc, List<SoulRelationship> allSouls) {
    final soulsHere = allSouls.where((s) => s.currentLocation == loc['id']).toList();
    
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
            Text(loc['name'].toUpperCase(), style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 18, letterSpacing: 2)),
            Text(loc['desc'] ?? "Sector data restricted.", style: const TextStyle(color: Colors.white38, fontSize: 12)),
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
                      backgroundImage: (soulsHere[i].portrait_url.isNotEmpty) ? NetworkImage("http://localhost:8000${soulsHere[i].portrait_url}") : null,
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
                onPressed: () => _moveUserTo(loc['id'], loc['name']),
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
          if (state != null) _buildRadarSelector(state.activeSouls),
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
                    itemBuilder: (context, index) => _buildTacticalNode(_locations[index], state?.activeSouls ?? []),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildRadarSelector(List<SoulRelationship> souls) {
    return Container(
      height: 110,
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: const BoxDecoration(color: Color(0xFF1A1A22), border: Border(bottom: BorderSide(color: Colors.white10))),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: souls.length,
        itemBuilder: (context, index) {
          final soul = souls[index];
          bool isSelected = _selectedSoulId == soul.soulId;
          return GestureDetector(
            onTap: () => setState(() => _selectedSoulId = isSelected ? null : soul.soulId),
            child: Container(
              margin: const EdgeInsets.only(right: 20),
              width: 70,
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: isSelected ? Colors.cyanAccent : Colors.white10,
                    child: CircleAvatar(
                      radius: 26,
                      backgroundColor: Colors.black,
                      backgroundImage: (soul.portrait_url.isNotEmpty) ? NetworkImage("http://localhost:8000${soul.portrait_url}") : null,
                      child: soul.portrait_url.isEmpty ? const Icon(Icons.person, color: Colors.white10) : null,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(soul.name.toUpperCase(), style: TextStyle(fontSize: 10, color: isSelected ? Colors.cyanAccent : Colors.white54, letterSpacing: 1), overflow: TextOverflow.ellipsis),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTacticalNode(dynamic loc, List<SoulRelationship> allSouls) {
    final soulsHere = allSouls.where((s) => s.currentLocation == loc['id']).toList();
    bool canMoveSoulHere = _selectedSoulId != null;

    return GestureDetector(
      onTap: () {
        if (canMoveSoulHere) {
          _moveSoulTo(loc['id'], loc['name']);
        } else {
          _showLocationDetails(loc, allSouls);
        }
      },
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A22),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: soulsHere.isNotEmpty ? Colors.cyanAccent.withOpacity(0.3) : Colors.white10, width: 1),
        ),
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(loc['name'].toUpperCase(), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 12, letterSpacing: 1)),
                  const SizedBox(height: 4),
                  Text(loc['desc'] ?? "Sector Restricted", style: const TextStyle(color: Colors.white38, fontSize: 9), maxLines: 2),
                ],
              ),
            ),
            if (canMoveSoulHere)
               const Center(child: Icon(Icons.add_location_alt, color: Colors.cyanAccent, size: 30))
            else
              Positioned(
                bottom: 12,
                left: 12,
                child: Row(
                  children: soulsHere.isEmpty 
                    ? [const Text("NO SIGNALS", style: TextStyle(color: Colors.white10, fontSize: 8, fontWeight: FontWeight.bold))]
                    : soulsHere.map((s) => Container(margin: const EdgeInsets.only(right: 4), width: 8, height: 8, decoration: const BoxDecoration(color: Colors.cyanAccent, shape: BoxShape.circle))).toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
