// frontend/lib/screens/chat_screen.dart
// version.py
// _dev/

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/dashboard_provider.dart';
import '../models/relationship.dart'; // Ensure this model is imported

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

  @override
  void initState() {
    super.initState();
    // Initialize state from the passed relationship
    _intimacyScore = widget.relationship.intimacyScore; // Using int from your model
    _currentLocation = widget.relationship.currentLocation;
    _currentTier = widget.relationship.intimacyTier;
    
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    try {
      final api = Provider.of<DashboardProvider>(context, listen: false).apiService;
      final history = await api.getChatHistory(widget.relationship.soulId);
      
      if (mounted) {
        setState(() {
          _messages.clear();
          for (var entry in history) {
            _messages.add({"role": entry['role'], "content": entry['content']});
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

  void _sendMessage() async {
    if (_messageController.text.isEmpty) return;
    final userMsg = _messageController.text;

    setState(() {
      _messages.add({"role": "user", "content": userMsg});
      _isSending = true;
    });
    _messageController.clear();
    _scrollToBottom();

    try {
      final api = Provider.of<DashboardProvider>(context, listen: false).apiService;
      
      // 📡 The API now returns the updated stats!
      final response = await api.sendMessage(widget.relationship.soulId, userMsg);
      
      if (mounted) {
        setState(() {
          _messages.add({"role": "soul", "content": response['response']});
          // ⚡ LIVE UPDATE: Update the meter and location immediately
          _intimacyScore = response['intimacy_score'] ?? _intimacyScore;
          _currentLocation = response['location'] ?? _currentLocation;
          _currentTier = response['tier'] ?? _currentTier;
        });
        _scrollToBottom();
      }
    } catch (e) {
      debugPrint("COMM ERROR: $e");
      setState(() => _messages.add({"role": "system", "content": "⚠️ CONNECTION LOST"}));
    } finally {
      if (mounted) setState(() => _isSending = false);
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
              backgroundColor: isArch ? Colors.amber.withValues(alpha: 0.2) : Colors.cyanAccent.withValues(alpha: 0.1),
              radius: 16,
              child: Icon(Icons.person, size: 16, color: isArch ? Colors.amber : Colors.cyanAccent),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(widget.relationship.name.toUpperCase(), 
                    style: TextStyle(fontSize: 14, letterSpacing: 1, color: isArch ? Colors.amber : Colors.white)
                  ),
                  Row(
                    children: [
                      const Icon(Icons.location_on, size: 10, color: Colors.white38),
                      const SizedBox(width: 4),
                      Text(_currentLocation.replaceAll('_', ' ').toUpperCase(), 
                        style: const TextStyle(fontSize: 10, color: Colors.white38)
                      ),
                    ],
                  )
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
            valueColor: AlwaysStoppedAnimation<Color>(isArch ? Colors.amber : Colors.cyanAccent),
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
                if (msg['role'] == 'system') return _buildSystemMessage(msg['content']!);
                return _buildMessageBubble(msg['content']!, msg['role'] == 'user', isArch);
              },
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
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isUser 
              ? (isArch ? Colors.amber.withValues(alpha: 0.15) : Colors.cyanAccent.withValues(alpha: 0.15)) 
              : const Color(0xFF1A1A22),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(12),
            topRight: const Radius.circular(12),
            bottomLeft: isUser ? const Radius.circular(12) : Radius.zero,
            bottomRight: isUser ? Radius.zero : const Radius.circular(12),
          ),
          border: Border.all(
            color: isUser 
              ? (isArch ? Colors.amber.withValues(alpha: 0.5) : Colors.cyanAccent.withValues(alpha: 0.5)) 
              : Colors.white10
          ),
        ),
        child: Text(content, style: const TextStyle(color: Colors.white, height: 1.4)),
      ),
    );
  }
  
  Widget _buildSystemMessage(String content) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8.0),
        child: Text(content, style: const TextStyle(color: Colors.redAccent, fontSize: 10, letterSpacing: 1)),
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
          Expanded(
            child: TextField(
              controller: _messageController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: "Send signal...",
                hintStyle: const TextStyle(color: Colors.white24),
                filled: true,
                fillColor: const Color(0xFF1A1A22),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(20), borderSide: BorderSide.none),
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
              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white54))
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