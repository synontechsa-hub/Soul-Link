import 'package:flutter/material.dart';

class ExploreSoulCard extends StatelessWidget {
  final Map<String, dynamic> soul;
  final String imageUrl;
  final VoidCallback onTap;

  const ExploreSoulCard({
    super.key,
    required this.soul,
    required this.imageUrl,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bool isLinked = soul['is_linked'] ?? false;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isLinked
                ? Colors.cyanAccent.withOpacity(0.5)
                : Colors.white10,
            width: 1,
          ),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(19),
          child: Stack(
            children: [
              // 🖼️ Full Card Image
              Positioned.fill(
                child: Image.network(
                  imageUrl,
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) => Container(
                    color: const Color(0xFF1A1A22),
                    child: const Icon(
                      Icons.person,
                      color: Colors.white24,
                      size: 40,
                    ),
                  ),
                ),
              ),
              // 🌑 Bottom Shadow Gradient
              Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.transparent,
                        Colors.black.withOpacity(0.1),
                        Colors.black.withOpacity(0.9),
                      ],
                    ),
                  ),
                ),
              ),
              // 📝 Soul Info Overlay
              Positioned(
                bottom: 12,
                left: 12,
                right: 12,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      soul['name'].toString().toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        letterSpacing: 1,
                      ),
                    ),
                    Text(
                      soul['archetype'] ?? "UNKNOWN",
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: Colors.cyanAccent,
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    // Action Label
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: isLinked
                            ? Colors.transparent
                            : Colors.cyanAccent,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.cyanAccent),
                      ),
                      child: Text(
                        isLinked ? "CHAT" : "LINK",
                        style: TextStyle(
                          color: isLinked ? Colors.cyanAccent : Colors.black,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
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
