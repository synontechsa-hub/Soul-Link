// frontend/lib/widgets/map/tactical_node.dart
import 'package:flutter/material.dart';
import '../../models/relationship.dart';

class TacticalNode extends StatefulWidget {
  final dynamic loc;
  final List<SoulRelationship> allSouls;
  final String? selectedSoulId;
  final Function(String locationId, String locationName) onMoveSoul;
  final Function(dynamic loc, List<SoulRelationship> allSouls) onShowDetails;

  const TacticalNode({
    super.key,
    required this.loc,
    required this.allSouls,
    this.selectedSoulId,
    required this.onMoveSoul,
    required this.onShowDetails,
  });

  @override
  State<TacticalNode> createState() => _TacticalNodeState();
}

class _TacticalNodeState extends State<TacticalNode> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.5).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final soulsHere = widget.allSouls.where((s) => s.currentLocation == widget.loc['location_id']).toList();
    
    // DEBUG: Check why souls aren't showing
    if (widget.allSouls.isNotEmpty && widget.loc['location_id'] == 'travel_hub') { // Just check one known location or all
       // print("📍 Checking ${widget.loc['location_id']} (${widget.loc['display_name']})");
       // for (var s in widget.allSouls) {
       //   if (s.currentLocation == widget.loc['location_id']) {
       //      print("   ✅ Found soul ${s.soulName} here!");
       //   } else {
       //      // print("   ❌ Soul ${s.soulName} is at ${s.currentLocation}");
       //   }
       // }
    }

    bool canMoveSoulHere = widget.selectedSoulId != null;
    final presentSoulsIds = widget.loc['present_souls'] as List? ?? [];

    return GestureDetector(
      onTap: () {
        if (canMoveSoulHere) {
          widget.onMoveSoul(widget.loc['location_id'], widget.loc['display_name'] ?? widget.loc['name'] ?? 'UNKNOWN');
        } else {
          widget.onShowDetails(widget.loc, widget.allSouls);
        }
      },
      child: Hero(
        tag: 'location_${widget.loc['location_id'] ?? widget.loc['id']}',
        child: Container(
          decoration: BoxDecoration(
            color: const Color(0xFF1A1A22),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: soulsHere.isNotEmpty ? Colors.cyanAccent.withOpacity(0.3) : Colors.white10,
              width: 1,
            ),
          ),
          child: Stack(
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      (widget.loc['display_name'] ?? widget.loc['name'] ?? 'UNKNOWN').toString().toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w900,
                        fontSize: 12,
                        letterSpacing: 1,
                        decoration: TextDecoration.none,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.loc['desc'] ?? "Signal strength nominal.",
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white38, fontSize: 10),
                    ),
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
                    children: [
                      if (soulsHere.isEmpty && presentSoulsIds.isEmpty)
                        const Text(
                          "NO SIGNALS",
                          style: TextStyle(
                            color: Colors.white10,
                            fontSize: 8,
                            fontWeight: FontWeight.bold,
                            decoration: TextDecoration.none,
                          ),
                        )
                      else
                        // Only show linked souls (cyan dots)
                        ...soulsHere.map((s) => _PulseDot(color: Colors.cyanAccent, animation: _pulseAnimation)),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PulseDot extends StatelessWidget {
  final Color color;
  final Animation<double> animation;
  final bool hasBorder;

  const _PulseDot({
    required this.color,
    required this.animation,
    this.hasBorder = false,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        return Container(
          margin: const EdgeInsets.only(right: 4),
          width: 8 * animation.value,
          height: 8 * animation.value,
          decoration: BoxDecoration(
            color: color.withOpacity(0.8),
            shape: BoxShape.circle,
            border: hasBorder ? Border.all(color: Colors.white24, width: 1) : null,
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.3),
                blurRadius: 4,
                spreadRadius: 2,
              ),
            ],
          ),
        );
      },
    );
  }
}
