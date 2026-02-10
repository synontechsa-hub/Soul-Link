// lib/widgets/soul_card.dart

// "The Tarnished rises victorious.
// The Elden Ring is restored.
// Link City v1.5.4 Arise is ready for deployment."

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../models/relationship.dart';
import '../core/config.dart';

class SoulCard extends StatelessWidget {
  final SoulRelationship relationship;
  final VoidCallback onTap;

  const SoulCard({super.key, required this.relationship, required this.onTap});

  @override
  Widget build(BuildContext context) {
    // Use AppConfig for image URL
    final String fullImageUrl = AppConfig.getImageUrl(relationship.portrait_url);

    return InkWell( // Using InkWell for that ripple effect on tap
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: const BoxDecoration(
          border: Border(bottom: BorderSide(color: Colors.white10, width: 0.5)),
        ),
        child: Row(
          children: [
            // 🖼️ LARGE CIRCULAR PORTRAIT (Like your reference)
            _buildPortrait(fullImageUrl),
            
            const SizedBox(width: 15),
            
            // 📝 TEXT CONTENT (Name & Subtitle)
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        relationship.name, // Displaying the actual name!
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      // Timestamp or Status on the right
                      Text(
                        relationship.intimacyTier.split('_').last,
                        style: const TextStyle(color: Colors.white38, fontSize: 11),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Last seen at ${relationship.currentLocation.replaceAll('_', ' ')}",
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.5),
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPortrait(String imageUrl) {
    return Container(
      width: 55,
      height: 55,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: Colors.cyanAccent.withOpacity(0.2), width: 1.5),
      ),
      child: ClipOval(
        child: Image.network(
          imageUrl,
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) => 
            const Icon(Icons.person, color: Colors.white24, size: 30),
        ),
      ),
    );
  }
}