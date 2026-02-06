// frontend/lib/widgets/location_suggestion_sheet.dart
import 'package:flutter/material.dart';

class LocationSuggestionSheet extends StatelessWidget {
  final List<dynamic> locations;
  final Function(String locationName, String locationId) onSelect;

  const LocationSuggestionSheet({
    super.key, 
    required this.locations, 
    required this.onSelect
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
      decoration: const BoxDecoration(
        color: Color(0xFF13131A),
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "SUGGEST RENDEZVOUS",
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  fontSize: 14,
                ),
              ),
              IconButton(
                onPressed: () => Navigator.pop(context),
                icon: const Icon(Icons.close, color: Colors.white38, size: 20),
              )
            ],
          ),
          const SizedBox(height: 12),
          ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.4,
            ),
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: locations.length,
              itemBuilder: (context, index) {
                final loc = locations[index];
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.05),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _getCategoryIcon(loc['category']), 
                      color: Colors.cyanAccent, 
                      size: 20
                    ),
                  ),
                  title: Text(
                    loc['display_name'],
                    style: const TextStyle(color: Colors.white, fontSize: 14),
                  ),
                  subtitle: Text(
                    loc['category'] ?? "General",
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.3), fontSize: 11),
                  ),
                  trailing: const Icon(Icons.chevron_right, color: Colors.white10),
                  onTap: () {
                    onSelect(loc['display_name'], loc['location_id']);
                    Navigator.pop(context);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String? category) {
    switch (category?.toLowerCase()) {
      case 'residential': return Icons.home;
      case 'commercial': return Icons.shopping_cart;
      case 'nightlife': return Icons.nightlife;
      case 'wellness': return Icons.spa;
      case 'dining': return Icons.restaurant;
      case 'landmark': return Icons.location_city;
      case 'cultural': return Icons.menu_book;
      case 'sports': return Icons.fitness_center;
      case 'entertainment': return Icons.videogame_asset;
      case 'underground': return Icons.security;
      case 'public_hub': return Icons.groups;
      default: return Icons.explore;
    }
  }
}
