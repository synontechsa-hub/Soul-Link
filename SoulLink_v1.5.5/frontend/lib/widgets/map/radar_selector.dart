// frontend/lib/widgets/map/radar_selector.dart
import 'package:flutter/material.dart';
import '../../models/relationship.dart';

class RadarSelector extends StatelessWidget {
  final List<SoulRelationship> souls;
  final String? selectedSoulId;
  final Function(String? soulId) onSoulSelected;

  const RadarSelector({
    super.key,
    required this.souls,
    required this.selectedSoulId,
    required this.onSoulSelected,
  });

  @override
  Widget build(BuildContext context) {
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
          bool isSelected = selectedSoulId == soul.soulId;
          return GestureDetector(
            onTap: () => onSoulSelected(isSelected ? null : soul.soulId),
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
                      backgroundImage: (soul.portrait_url.isNotEmpty)
                          ? NetworkImage("http://localhost:8000${soul.portrait_url}")
                          : null,
                      child: soul.portrait_url.isEmpty
                          ? const Icon(Icons.person, color: Colors.white10)
                          : null,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    soul.name.toUpperCase(),
                    style: TextStyle(
                      fontSize: 10,
                      color: isSelected ? Colors.cyanAccent : Colors.white54,
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
}
