import 'package:flutter/material.dart';
import '../../state/app_session.dart';
import '../../models/bot_model.dart';

// ─────────────────────────────────────────────
// 🌎 BROWSE SCREEN (THE SOUL GALLERY)
// ─────────────────────────────────────────────

class BrowseScreen extends StatelessWidget {
  final AppSession session;

  const BrowseScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    // 🧠 EVOLUTION LOGIC: Convert the session bots map to a displayable list
    final bots = session.bots.values.toList();

    return Scaffold(
      backgroundColor: Colors.black,
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          // ─────────────────────────────────────────────
          // 🏷️ DYNAMIC HEADER
          // ─────────────────────────────────────────────
          const SliverAppBar(
            expandedHeight: 140,
            floating: true,
            pinned: true,
            backgroundColor: Colors.black,
            flexibleSpace: FlexibleSpaceBar(
              titlePadding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              title: Text(
                "Discover Souls",
                style: TextStyle(
                  fontWeight: FontWeight.w900, 
                  color: Colors.white,
                  letterSpacing: 1.1,
                ),
              ),
              centerTitle: false,
            ),
          ),

          // ─────────────────────────────────────────────
          // 🃏 CHARACTER GRID
          // ─────────────────────────────────────────────
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            sliver: SliverGrid(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2, 
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: 0.72, // Optimized for portrait portraits
              ),
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final bot = bots[index];
                  return _SoulCard(
                    bot: bot,
                    onTap: () => _handleSoulSelection(context, bot),
                  );
                },
                childCount: bots.length,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _handleSoulSelection(BuildContext context, BotModel bot) {
    // Future: Logic to start a conversation or open a deep profile view
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Connecting to ${bot.name}..."), duration: const Duration(seconds: 1)),
    );
  }
}

// ─────────────────────────────────────────────
// 🧬 THE SOUL CARD (DOSSIR VIEW)
// ─────────────────────────────────────────────

class _SoulCard extends StatelessWidget {
  final BotModel bot;
  final VoidCallback onTap;

  const _SoulCard({required this.bot, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.1), width: 1),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // 🖼️ CHARACTER IMAGE (Fallback to seed if empty)
          Image.network(
            bot.avatarUrl.isNotEmpty 
                ? bot.avatarUrl 
                : "https://picsum.photos/seed/${bot.id}/400/600",
            fit: BoxFit.cover,
          ),

          // 🧠 THE "DEPTH" GRADIENT
          // Ensures readability regardless of image brightness
          const DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Colors.transparent, Colors.black87, Colors.black],
                stops: [0.4, 0.85, 1.0],
              ),
            ),
          ),

          // 📝 SOUL DATA OVERLAY
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.end,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 🧠 TRAIT CHIP (First trait only for UI space)
                if (bot.persona.traits.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.blueAccent.withOpacity(0.7),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      bot.persona.traits.first.toUpperCase(),
                      style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                const SizedBox(height: 6),
                Text(
                  bot.name,
                  style: const TextStyle(
                    fontSize: 18, 
                    fontWeight: FontWeight.bold, 
                    color: Colors.white,
                    height: 1.1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  bot.description,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 11, color: Colors.white70),
                ),
              ],
            ),
          ),
          
          // 🧠 INTERACTION LAYER
          Material(
            color: Colors.transparent,
            child: InkWell(onTap: onTap),
          ),
        ],
      ),
    );
  }
}