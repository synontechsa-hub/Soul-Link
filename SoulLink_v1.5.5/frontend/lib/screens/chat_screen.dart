// frontend/lib/screens/chat_screen.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../providers/websocket_provider.dart';
import '../models/relationship.dart';
import '../widgets/location_suggestion_sheet.dart';
import '../widgets/error_toast.dart';
import '../widgets/stability_bar.dart';
import '../services/ad_service.dart';

class ChatScreen extends StatefulWidget {
  // We pass the full relationship now to pre-fill the UI state
  final SoulRelationship relationship;

  const ChatScreen({super.key, required this.relationship});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  final List<Map<String, String>> _messages = [];
  bool _isSending = false;

  // 🧠 Local State for "Live" updates
  late int _intimacyScore;
  late String _currentLocation;
  late String _currentTier;

  // 📡 Stability Tracking
  double _currentStability = 100.0;
  bool _isLoadingStability = false;

  @override
  void initState() {
    super.initState();
    // Initialize state from the passed relationship
    _intimacyScore =
        widget.relationship.intimacyScore; // Using int from your model
    _currentLocation = widget.relationship.currentLocation;
    _currentTier = widget.relationship.intimacyTier;

    _loadHistory();
    _subscribeToWebSocket();
    _fetchStability();
  }

  void _subscribeToWebSocket() {
    final wsProvider = Provider.of<WebSocketProvider>(context, listen: false);

    // Listen for real-time chat messages
    wsProvider.onChatMessage = (data) {
      final soulId = data['soul_id'] as String?;

      // DISABLED: Prevent duplicate messages (we already add from HTTP response)
      // Only process messages for this soul
      // if (soulId == widget.relationship.soulId && mounted) {
      //   setState(() {
      //     _messages.add({"role": "soul", "content": data['response'] ?? ''});
      //     _intimacyScore = data['intimacy_score'] ?? _intimacyScore;
      //     _currentLocation = data['location'] ?? _currentLocation;
      //     _currentTier = data['tier'] ?? _currentTier;
      //   });
      //   _scrollToBottom();
      // }
    };
  }

  /// Strip movement commands from soul response
  String _stripMovementCommands(String text) {
    // Remove [MOVE_location_name] brackets
    return text.replaceAll(RegExp(r'\[MOVE_[^\]]+\]'), '').trim();
  }

  Future<void> _loadHistory() async {
    try {
      final api = Provider.of<DashboardProvider>(
        context,
        listen: false,
      ).apiService;
      final history = await api.getChatHistory(widget.relationship.soulId);

      if (mounted) {
        setState(() {
          _messages.clear();
          for (var entry in history) {
            _messages.add({
              "role": entry['role'],
              "content": _stripMovementCommands(entry['content'] ?? ''),
            });
          }
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint("📜 HISTORY FAULT: $e");
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _fetchStability() async {
    try {
      final api = Provider.of<DashboardProvider>(
        context,
        listen: false,
      ).apiService;
      final result = await api.getUserStability(widget.relationship.soulId);

      if (mounted) {
        setState(() {
          _currentStability =
              (result['signal_stability'] as num?)?.toDouble() ?? 100.0;
        });
      }
    } catch (e) {
      debugPrint("📡 Stability fetch error: $e");
    }
  }

  void _sendMessage() async {
    if (_messageController.text.isEmpty) return;

    // Check if stability is 0
    if (_currentStability <= 0) {
      _showStabilityBlocker();
      return;
    }

    final userMsg = _messageController.text;

    setState(() {
      _messages.add({"role": "user", "content": userMsg});
      _isSending = true;
    });
    _messageController.clear();
    _scrollToBottom();

    try {
      final api = Provider.of<DashboardProvider>(
        context,
        listen: false,
      ).apiService;

      // 📡 The API now returns the updated stats!
      final response = await api.sendMessage(
        widget.relationship.soulId,
        userMsg,
      );

      if (mounted) {
        setState(() {
          _messages.add({
            "role": "soul",
            "content": _stripMovementCommands(response['response']),
          });
          // ⚡ LIVE UPDATE: Update the meter and location immediately
          _intimacyScore = response['intimacy_score'] ?? _intimacyScore;
          _currentLocation = response['location'] ?? _currentLocation;
          _currentTier = response['tier'] ?? _currentTier;
        });
        _scrollToBottom();

        // Fetch updated stability after message
        _fetchStability();
      }
    } catch (e) {
      debugPrint("COMM ERROR: $e");
      if (mounted) {
        ErrorToast.show(context, ErrorToast.parseError(e));
        setState(
          () => _messages.add({
            "role": "system",
            "content": "⚠️ CONNECTION LOST",
          }),
        );
      }
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  void _suggestLocation() async {
    try {
      final api = Provider.of<DashboardProvider>(
        context,
        listen: false,
      ).apiService;
      final locations = await api.getMapLocations();

      if (!mounted) return;

      showModalBottomSheet(
        context: context,
        backgroundColor: Colors.transparent,
        builder: (context) => LocationSuggestionSheet(
          locations: locations,
          onSelect: (name, id) {
            // Send a cinematic suggestion
            _messageController.text =
                "I was thinking... maybe we should head over to $name?";
            _sendMessage();
          },
        ),
      );
    } catch (e) {
      debugPrint("📍 LOC FETCH FAULT: $e");
    }
  }

  void _showStabilityBlocker() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A22),
        title: const Text(
          "SIGNAL LOST",
          style: TextStyle(color: Colors.redAccent),
        ),
        content: const Text(
          "Neural link stability has dropped to 0%.\n\nReturn to your apartment to restore the signal.",
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("DISMISS"),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Exit chat
            },
            child: const Text(
              "GO TO APARTMENT",
              style: TextStyle(color: Colors.cyanAccent),
            ),
          ),
        ],
      ),
    );
  }

  void _boostStability() async {
    final adService = Provider.of<AdService>(context, listen: false);

    setState(() => _isLoadingStability = true);

    final success = await adService.showAd(
      AdType.rewarded,
      onReward: (type, amount) {
        if (!mounted) return;
        _fetchStability();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Signal restored! +$amount Stability"),
            backgroundColor: Colors.greenAccent,
          ),
        );
      },
    );

    if (mounted) {
      setState(() => _isLoadingStability = false);

      if (!success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Failed to load ad. Try again."),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    bool isArch = widget.relationship.isArchitect;

    return Scaffold(
      // 🌌 Dark Background matching the App Theme
      backgroundColor: const Color(0xFF0A0A0E),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1A22),
        elevation: 0,
        titleSpacing: 0,
        title: Row(
          children: [
            // Tiny Portrait Placeholder
            CircleAvatar(
              backgroundColor: isArch
                  ? Colors.amber.withValues(alpha: 0.2)
                  : Colors.cyanAccent.withValues(alpha: 0.1),
              radius: 16,
              child: Icon(
                Icons.person,
                size: 16,
                color: isArch ? Colors.amber : Colors.cyanAccent,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.relationship.name.toUpperCase(),
                    style: TextStyle(
                      fontSize: 14,
                      letterSpacing: 1,
                      color: isArch ? Colors.amber : Colors.white,
                    ),
                  ),
                  Row(
                    children: [
                      const Icon(
                        Icons.location_on,
                        size: 10,
                        color: Colors.white38,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _currentLocation.replaceAll('_', ' ').toUpperCase(),
                        style: const TextStyle(
                          fontSize: 10,
                          color: Colors.white38,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(4),
          child: LinearProgressIndicator(
            value: (_intimacyScore % 100) / 100, // Simple 0-100 loop for now
            backgroundColor: Colors.black,
            valueColor: AlwaysStoppedAnimation<Color>(
              isArch ? Colors.amber : Colors.cyanAccent,
            ),
            minHeight: 2,
          ),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                if (msg['role'] == 'system')
                  return _buildSystemMessage(msg['content']!);
                return _buildMessageBubble(
                  msg['content']!,
                  msg['role'] == 'user',
                  isArch,
                );
              },
            ),
          ),
          // 📡 Stability Bar
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: StabilityBar(
              stability: _currentStability,
              onBoost: _boostStability,
              isLoading: _isLoadingStability,
            ),
          ),
          _buildInputArea(isArch),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(String content, bool isUser, bool isArch) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? (isArch
                    ? Colors.amber.withValues(alpha: 0.15)
                    : Colors.cyanAccent.withValues(alpha: 0.15))
              : const Color(0xFF1A1A22),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(12),
            topRight: const Radius.circular(12),
            bottomLeft: isUser ? const Radius.circular(12) : Radius.zero,
            bottomRight: isUser ? Radius.zero : const Radius.circular(12),
          ),
          border: Border.all(
            color: isUser
                ? (isArch
                      ? Colors.amber.withValues(alpha: 0.5)
                      : Colors.cyanAccent.withValues(alpha: 0.5))
                : Colors.white10,
          ),
        ),
        child: Text(
          content,
          style: const TextStyle(color: Colors.white, height: 1.4),
        ),
      ),
    );
  }

  Widget _buildSystemMessage(String content) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Text(
          content,
          style: const TextStyle(
            color: Colors.redAccent,
            fontSize: 10,
            letterSpacing: 1,
          ),
        ),
      ),
    );
  }

  Widget _buildInputArea(bool isArch) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Color(0xFF0F0F13),
        border: Border(top: BorderSide(color: Colors.white10)),
      ),
      child: Row(
        children: [
          // 🗺️ RENDEZVOUS BUTTON
          IconButton(
            icon: const Icon(Icons.explore_outlined, color: Colors.white38),
            onPressed: _suggestLocation,
            tooltip: 'Suggest Rendezvous',
          ),
          const SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: _messageController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "Send signal...",
                hintStyle: const TextStyle(color: Colors.white24),
                filled: true,
                fillColor: const Color(0xFF1A1A22),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(20),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: _isSending
                ? Colors.transparent
                : (isArch ? Colors.amber : Colors.cyanAccent),
            radius: 20,
            child: _isSending
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white54,
                    ),
                  )
                : IconButton(
                    icon: const Icon(Icons.send, size: 18, color: Colors.black),
                    onPressed: _sendMessage,
                  ),
          ),
        ],
      ),
    );
  }
}
