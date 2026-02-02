// frontend/lib/screens/map_screen.dart
// version.py v1.5.3-P (Unified Snake Case)

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/relationship.dart';

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
    final api = Provider.of<DashboardProvider>(
      context,
      listen: false,
    ).apiService;
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

  Future<void> _moveToLocation(String locationId, String locationName) async {
    if (_selectedSoulId == null) return;

    final provider = Provider.of<DashboardProvider>(context, listen: false);
    try {
      await provider.apiService.moveSoul(
        soulId: _selectedSoulId!,
        locationId: locationId,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("SIGNAL REROUTED: SOUL MOVING TO $locationName"),
          backgroundColor: Colors.cyan[900],
        ),
      );

      provider.syncDashboard();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("MOVE FAILED: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final dashboard = context.watch<DashboardProvider>();
    final state = dashboard.state;

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      appBar: AppBar(
        title: const Text(
          'CITY RADAR',
          style: TextStyle(
            letterSpacing: 3,
            fontWeight: FontWeight.w900,
            fontSize: 16,
          ),
        ),
        backgroundColor: const Color(0xFF1A1A22),
        elevation: 0,
      ),
      body: Column(
        children: [
          if (state != null) _buildRadarSelector(state.activeSouls),
          Expanded(
            child: _isLoadingLocs
                ? const Center(
                    child: CircularProgressIndicator(color: Colors.cyanAccent),
                  )
                : GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          mainAxisSpacing: 12,
                          crossAxisSpacing: 12,
                          childAspectRatio: 0.85,
                        ),
                    itemCount: _locations.length,
                    itemBuilder: (context, index) {
                      return _buildTacticalNode(
                        _locations[index],
                        state?.activeSouls ?? [],
                      );
                    },
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
      decoration: const BoxDecoration(
        color: Color(0xFF1A1A22),
        border: Border(bottom: BorderSide(color: Colors.white10)),
      ),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: souls.length,
        itemBuilder: (context, index) {
          final soul = souls[index];
          bool isSelected = _selectedSoulId == soul.soulId;

          return GestureDetector(
            onTap: () => setState(
              () => _selectedSoulId = isSelected ? null : soul.soulId,
            ),
            child: Container(
              margin: const EdgeInsets.only(right: 20),
              width: 70,
              child: Column(
                children: [
                  Stack(
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundColor: isSelected
                            ? Colors.cyanAccent
                            : Colors.white10,
                        child: CircleAvatar(
                          radius: 26,
                          backgroundColor: Colors.black,
                          // ✅ FIXED: Using portrait_url (Snake Case)
                          backgroundImage: (soul.portrait_url.isNotEmpty)
                              ? NetworkImage(
                                  "http://localhost:8000${soul.portrait_url}",
                                )
                              : null,
                          child: soul.portrait_url.isEmpty
                              ? const Icon(Icons.person, color: Colors.white10)
                              : null,
                        ),
                      ),
                      if (isSelected)
                        const Positioned(
                          right: 0,
                          bottom: 0,
                          child: CircleAvatar(
                            radius: 10,
                            backgroundColor: Colors.cyanAccent,
                            child: Icon(
                              Icons.gps_fixed,
                              size: 12,
                              color: Colors.black,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    soul.name.toUpperCase(),
                    style: TextStyle(
                      fontSize: 10,
                      color: isSelected ? Colors.cyanAccent : Colors.white54,
                      fontWeight: isSelected
                          ? FontWeight.bold
                          : FontWeight.normal,
                      letterSpacing: 1,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTacticalNode(dynamic loc, List<SoulRelationship> allSouls) {
    final soulsHere = allSouls
        .where((s) => s.currentLocation == loc['id'])
        .toList();
    bool canMoveHere = _selectedSoulId != null;

    return GestureDetector(
      onTap: () {
        if (canMoveHere) {
          _moveToLocation(loc['id'], loc['name']);
        }
      },
      child: Container(
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A22),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: soulsHere.isNotEmpty
                ? Colors.cyanAccent.withOpacity(0.3)
                : Colors.white10,
            width: 1,
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(19),
          child: Stack(
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      loc['name'].toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w900,
                        fontSize: 12,
                        letterSpacing: 1,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      loc['desc'] ?? "Sector Restricted",
                      style: const TextStyle(
                        color: Colors.white38,
                        fontSize: 9,
                      ),
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
              Positioned(
                bottom: 12,
                left: 12,
                right: 12,
                child: Row(
                  children: [
                    if (soulsHere.isEmpty)
                      const Text(
                        "NO SIGNALS",
                        style: TextStyle(
                          color: Colors.white10,
                          fontSize: 8,
                          fontWeight: FontWeight.bold,
                        ),
                      )
                    else
                      ...soulsHere
                          .map(
                            (s) => Container(
                              margin: const EdgeInsets.only(right: 6),
                              width: 12,
                              height: 12,
                              decoration: BoxDecoration(
                                color: Colors.cyanAccent,
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.cyanAccent.withOpacity(0.5),
                                    blurRadius: 4,
                                    spreadRadius: 1,
                                  ),
                                ],
                              ),
                            ),
                          )
                          .toList(),
                  ],
                ),
              ),
              if (canMoveHere)
                Positioned.fill(
                  child: Container(
                    color: Colors.cyanAccent.withOpacity(0.05),
                    child: const Center(
                      child: Icon(
                        Icons.add_location_alt,
                        color: Colors.cyanAccent,
                        size: 30,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
