import 'package:flutter/material.dart';
import '../services/bot_loader.dart';
import '../models/bot.dart';
import 'chat_screen.dart';

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  late Future<List<Bot>> botsFuture;
  List<Bot> _allBots = [];
  List<Bot> _filteredBots = [];
  String _searchQuery = "";
  String _selectedFilter = "All";

  final List<String> filters = [
    "All",
    "Recommend",
    "Anime",
    "Female",
    "Real",
    "Male",
  ];

  @override
  void initState() {
    super.initState();
    botsFuture = BotLoader.loadAllBots();
    botsFuture.then((bots) {
      setState(() {
        _allBots = bots;
        _filteredBots = bots;
      });
    });
  }

  void _applyFilters() {
    setState(() {
      _filteredBots = _allBots.where((bot) {
        final matchesSearch =
            bot.name.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            bot.archetype.toLowerCase().contains(_searchQuery.toLowerCase()) ||
            bot.description.toLowerCase().contains(_searchQuery.toLowerCase());

        final matchesFilter = _selectedFilter == "All"
            ? true
            : bot.archetype.toLowerCase().contains(
                _selectedFilter.toLowerCase(),
              );

        return matchesSearch && matchesFilter;
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E0E11), // Neutral-900
      appBar: AppBar(
        title: const Text("Explore Bots"),
        backgroundColor: const Color(0xFF181A1F), // Neutral-800
      ),
      body: Column(
        children: [
          // 🔍 Search bar
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              decoration: InputDecoration(
                hintText: "Search bots...",
                filled: true,
                fillColor: const Color(0xFFF2F3F6), // Neutral-100
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                prefixIcon: const Icon(Icons.search, color: Color(0xFF6B6F7A)),
              ),
              onChanged: (value) {
                _searchQuery = value;
                _applyFilters();
              },
            ),
          ),

          // 🎛️ Filter chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: filters.map((filter) {
                final isSelected = _selectedFilter == filter;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(filter),
                    selected: isSelected,
                    selectedColor: const Color(0xFF7E57C2), // Purple-500
                    backgroundColor: const Color(0xFF181A1F),
                    labelStyle: TextStyle(
                      color: isSelected
                          ? Colors.white
                          : const Color(0xFF6B6F7A),
                    ),
                    onSelected: (_) {
                      setState(() {
                        _selectedFilter = filter;
                        _applyFilters();
                      });
                    },
                  ),
                );
              }).toList(),
            ),
          ),

          const SizedBox(height: 12),

          // 🗂️ Bot grid
          Expanded(
            child: FutureBuilder<List<Bot>>(
              future: botsFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                } else if (snapshot.hasError) {
                  return const Center(child: Text("Error loading bots"));
                } else {
                  return _filteredBots.isEmpty
                      ? const Center(
                          child: Text(
                            "No bots found",
                            style: TextStyle(color: Colors.white),
                          ),
                        )
                      : GridView.builder(
                          padding: const EdgeInsets.all(16),
                          gridDelegate:
                              const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2,
                                childAspectRatio: 0.8,
                                crossAxisSpacing: 12,
                                mainAxisSpacing: 12,
                              ),
                          itemCount: _filteredBots.length,
                          itemBuilder: (context, index) {
                            final bot = _filteredBots[index];
                            return GestureDetector(
                              onTap: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => ChatScreen(bot: bot),
                                  ),
                                );
                              },
                              child: Container(
                                decoration: BoxDecoration(
                                  color: const Color(0xFF181A1F),
                                  borderRadius: BorderRadius.circular(16),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.3),
                                      blurRadius: 6,
                                      offset: const Offset(2, 4),
                                    ),
                                  ],
                                ),
                                padding: const EdgeInsets.all(12),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      bot.name,
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                        color: Color(0xFF7E57C2), // Purple-500
                                      ),
                                    ),
                                    const SizedBox(height: 6),
                                    Text(
                                      bot.archetype,
                                      style: const TextStyle(
                                        fontSize: 14,
                                        color: Color(0xFFB39DDB), // Purple-300
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Expanded(
                                      child: Text(
                                        bot.description,
                                        style: const TextStyle(
                                          fontSize: 12,
                                          color: Color(
                                            0xFFF2F3F6,
                                          ), // Neutral-100
                                        ),
                                        overflow: TextOverflow.fade,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        );
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}
