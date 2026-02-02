// frontend/lib/screens/explore_screen.dart
// version.py v1.5.3-P

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../providers/dashboard_provider.dart';
import './chat_screen.dart';

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  List<dynamic> _souls = [];
  List<dynamic> _filteredSouls = [];
  bool _isLoading = true;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _scanForSignals();
    _searchController.addListener(_filterSouls);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _scanForSignals() async {
    final api = Provider.of<DashboardProvider>(
      context,
      listen: false,
    ).apiService;
    try {
      final data = await api.getExploreSouls();
      if (mounted) {
        setState(() {
          _souls = data;
          _filteredSouls = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _filterSouls() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      _filteredSouls = _souls.where((soul) {
        final name = (soul['name'] ?? '').toLowerCase();
        final archetype = (soul['archetype'] ?? '').toLowerCase();
        return name.contains(query) || archetype.contains(query);
      }).toList();
    });
  }

  Future<void> _initiateLink(String soulId) async {
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    try {
      await provider.apiService.linkWithSoul(soulId);
      await provider.syncDashboard();
      _scanForSignals();
    } catch (e) {
      debugPrint("Link Error: $e");
    }
  }

  void _openChat(Map<String, dynamic> soulData) {
    final provider = Provider.of<DashboardProvider>(context, listen: false);
    final relationships = provider.state?.activeSouls ?? [];

    try {
      final relationship = relationships.firstWhere(
        (rel) => rel.soulId == soulData['id'],
      );
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ChatScreen(relationship: relationship),
        ),
      );
    } catch (e) {
      debugPrint("Chat Navigate Error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    final String rawApiBase =
        dotenv.env['API_URL'] ?? 'http://localhost:8000/api/v1';
    final String apiBase = rawApiBase.trim();
    final String serverRoot = apiBase.replaceAll('/api/v1', '');

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A22),
        elevation: 0,
        title: const Text(
          'EXPLORE',
          style: TextStyle(letterSpacing: 3, fontWeight: FontWeight.w900),
        ),
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Search for Souls...',
                hintStyle: const TextStyle(color: Colors.white24),
                prefixIcon: const Icon(Icons.search, color: Colors.cyanAccent),
                filled: true,
                fillColor: const Color(0xFF1A1A22),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(30),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          Expanded(
            child: _isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Colors.cyanAccent),
                  )
                : GridView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          childAspectRatio: 0.75,
                          crossAxisSpacing: 12,
                          mainAxisSpacing: 12,
                        ),
                    itemCount: _filteredSouls.length,
                    itemBuilder: (context, index) {
                      final soul = _filteredSouls[index];
                      // Flexible path logic to handle backend key variations
                      final String path =
                          soul['portrait_url'] ??
                          soul['image_url'] ??
                          '/assets/images/souls/default_01.jpeg';
                      final String imageUrl = "$serverRoot$path";
                      return _buildSoulCard(soul, imageUrl);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildSoulCard(Map<String, dynamic> soul, String imageUrl) {
    final bool isLinked = soul['is_linked'] ?? false;

    return GestureDetector(
      onTap: () => isLinked ? _openChat(soul) : _initiateLink(soul['id']),
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
