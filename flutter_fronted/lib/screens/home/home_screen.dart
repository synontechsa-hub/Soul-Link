import 'package:flutter/material.dart';
import '../../state/app_session.dart';
import '../../models/bot_model.dart';
import '../../widgets/bot_card.dart'; // Ensure you create this reusable widget

// ─────────────────────────────────────────────
// 🏠 HOME SCREEN (THE PERSONALIZED HUB)
// ─────────────────────────────────────────────

class HomeScreen extends StatelessWidget {
  final AppSession session;

  const HomeScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    // 🧠 RECOMMENDATION LOGIC
    // For now, we take the first bot as "Featured" and the rest as "Recommended"
    final allBots = session.bots.values.toList();
    final featuredBot = allBots.isNotEmpty ? allBots.first : null;
    final recommendedBots = allBots.length > 1 ? allBots.sublist(1) : allBots;

    return Scaffold(
      backgroundColor: Colors.black,
      body: CustomScrollView(
        slivers: [
          // ─────────────────────────────────────────────
          // 🎭 HERO SECTION: FEATURED SOUL
          // ─────────────────────────────────────────────
          SliverToBoxAdapter(
            child: featuredBot != null 
              ? _FeaturedSoulHero(bot: featuredBot) 
              : const SizedBox(height: 100),
          ),

          // ─────────────────────────────────────────────
          // 🏷️ CATEGORY SELECTOR (FAVORITE TAGS)
          // ─────────────────────────────────────────────
          SliverToBoxAdapter(
            child: _TrendingTagsSection(
              tags: ['Mystic', 'Cyberpunk', 'Friendly', 'Cold', 'Tsundere'],
            ),
          ),

          // ─────────────────────────────────────────────
          // 🌟 RECOMMENDED FOR YOU
          // ─────────────────────────────────────────────
          const SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.fromLTRB(20, 24, 20, 12),
              child: Text(
                "Recommended for You",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
              ),
            ),
          ),

          SliverToBoxAdapter(
            child: SizedBox(
              height: 200,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: recommendedBots.length,
                itemBuilder: (context, index) {
                  return Container(
                    width: 150,
                    margin: const EdgeInsets.only(right: 12),
                    child: _SoulMiniCard(bot: recommendedBots[index]),
                  );
                },
              ),
            ),
          ),

          // ─────────────────────────────────────────────
          // 🔥 RECENTLY ACTIVE SOULS
          // ─────────────────────────────────────────────
          const SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.fromLTRB(20, 32, 20, 12),
              child: Text(
                "Trending Souls",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
              ),
            ),
          ),

          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) => _TrendingSoulTile(bot: allBots[index % allBots.length]),
                childCount: allBots.length,
              ),
            ),
          ),
          
          const SliverToBoxAdapter(child: SizedBox(height: 100)), // Bottom padding
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────
// 🧬 UI COMPONENTS
// ─────────────────────────────────────────────

class _FeaturedSoulHero extends StatelessWidget {
  final BotModel bot;
  const _FeaturedSoulHero({required this.bot});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 400,
      width: double.infinity,
      decoration: BoxDecoration(
        image: DecorationImage(
          image: NetworkImage(bot.avatarUrl.isNotEmpty ? bot.avatarUrl : "https://picsum.photos/seed/hero/800/1200"),
          fit: BoxFit.cover,
        ),
      ),
      child: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter, end: Alignment.bottomCenter,
            colors: [Colors.transparent, Colors.black],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.end,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("DAILY FEATURED SOUL", style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.w900, letterSpacing: 2)),
            Text(bot.name, style: const TextStyle(fontSize: 42, fontWeight: FontWeight.bold, color: Colors.white)),
            Text(bot.description, maxLines: 2, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {}, 
              style: ElevatedButton.styleFrom(backgroundColor: Colors.white, foregroundColor: Colors.black),
              child: const Text("CHAT NOW"),
            )
          ],
        ),
      ),
    );
  }
}

class _TrendingTagsSection extends StatelessWidget {
  final List<String> tags;
  const _TrendingTagsSection({required this.tags});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: tags.map((tag) => Padding(
          padding: const EdgeInsets.only(right: 8),
          child: ActionChip(
            label: Text(tag),
            backgroundColor: Colors.grey.shade900,
            labelStyle: const TextStyle(color: Colors.white),
            onPressed: () {},
          ),
        )).toList(),
      ),
    );
  }
}

class _SoulMiniCard extends StatelessWidget {
  final BotModel bot;
  const _SoulMiniCard({required this.bot});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              image: DecorationImage(
                image: NetworkImage(bot.avatarUrl.isNotEmpty ? bot.avatarUrl : "https://picsum.photos/seed/${bot.id}/200/300"),
                fit: BoxFit.cover,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(bot.name, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        Text(bot.persona.traits.isNotEmpty ? bot.persona.traits.first : "Mysterious", style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}

class _TrendingSoulTile extends StatelessWidget {
  final BotModel bot;
  const _TrendingSoulTile({required this.bot});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(vertical: 4),
      leading: CircleAvatar(backgroundImage: NetworkImage(bot.avatarUrl)),
      title: Text(bot.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      subtitle: Text(bot.description, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.grey)),
      trailing: const Icon(Icons.arrow_forward_ios, size: 14, color: Colors.grey),
    );
  }
}