import 'package:flutter/material.dart';
import '../../state/app_session.dart';
import '../../models/bot_model.dart';
import '../../models/conversation_model.dart';
import '../../models/message_model.dart'; // Added for BondPhase logic
import 'chat_screen.dart';

// ─────────────────────────────────────────────
// 📜 CHAT HISTORY (THE INBOX)
// ─────────────────────────────────────────────

class ChatHistoryScreen extends StatelessWidget {
  final AppSession session;

  const ChatHistoryScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    // 🧠 SORTING LOGIC: Keep the most recent souls at the top
    final conversations = session.conversations.values.toList()
      ..sort((a, b) => b.lastUpdated.compareTo(a.lastUpdated));

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Connections', // Or "SoulLinks"
          style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2),
        ),
        centerTitle: false,
        elevation: 0,
      ),
      body: conversations.isEmpty
          ? _buildEmptyState()
          : ListView.separated(
              itemCount: conversations.length,
              separatorBuilder: (context, index) => const Divider(height: 1, indent: 80),
              itemBuilder: (context, index) {
                final conversation = conversations[index];
                final bot = session.bots[conversation.botId];

                if (bot == null) return const SizedBox.shrink();

                return _ChatHistoryTile(
                  bot: bot,
                  conversation: conversation,
                  onTap: () => _navigateToChat(context, conversation.id),
                );
              },
            ),
    );
  }

  void _navigateToChat(BuildContext context, String conversationId) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ChatScreen(
          session: session,
          conversationId: conversationId,
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return const Center(
      child: Text(
        "No souls linked yet.\nVisit the Browse tab to begin.",
        textAlign: TextAlign.center,
        style: TextStyle(color: Colors.grey),
      ),
    );
  }
}

// ─────────────────────────────────────────────
// 🧬 CHAT HISTORY TILE (SOULLINK VISUALS)
// ─────────────────────────────────────────────

class _ChatHistoryTile extends StatelessWidget {
  final BotModel bot;
  final ConversationModel conversation;
  final VoidCallback onTap;

  const _ChatHistoryTile({
    required this.bot,
    required this.conversation,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    // 🧠 LAST MESSAGE LOGIC
    final lastMessage = conversation.messages.isNotEmpty
        ? conversation.messages.last.content
        : 'Start a conversation';

    // 🧠 SOULLINK EVOLUTION: Get bond phase visual cue
    final phase = conversation.bondPhase;

    return ListTile(
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      leading: Stack(
        children: [
          CircleAvatar(
            radius: 28,
            backgroundColor: Colors.grey.shade900,
            backgroundImage: bot.avatarUrl.isNotEmpty ? NetworkImage(bot.avatarUrl) : null,
            child: bot.avatarUrl.isEmpty ? Text(bot.name[0], style: const TextStyle(fontSize: 20)) : null,
          ),
          // 🧠 BOND INDICATOR: Small badge showing relationship status
          Positioned(
            right: 0,
            bottom: 0,
            child: _buildBondBadge(phase),
          ),
        ],
      ),
      title: Row(
        children: [
          Expanded(
            child: Text(
              bot.name,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
          ),
          Text(
            _formatTime(conversation.lastUpdated),
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 4.0),
        child: Text(
          lastMessage,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            color: Colors.grey.shade400,
            fontSize: 14,
            // If the last message is from the bot, maybe style it differently?
            fontStyle: conversation.messages.isNotEmpty && conversation.messages.last.isFromBot 
                ? FontStyle.italic 
                : FontStyle.normal,
          ),
        ),
      ),
    );
  }

  // 🧠 EVOLUTION LOGIC: Map BondPhase to a visual icon/color
  Widget _buildBondBadge(BondPhase phase) {
    Color color;
    IconData icon;

    switch (phase) {
      case BondPhase.stranger: color = Colors.grey; icon = Icons.person_outline; break;
      case BondPhase.familiar: color = Colors.blue; icon = Icons.chat_bubble_outline; break;
      case BondPhase.trusted: color = Colors.green; icon = Icons.verified_user_outlined; break;
      case BondPhase.bonded: color = Colors.orange; icon = Icons.favorite_border; break;
      case BondPhase.linked: color = Colors.purple; icon = Icons.auto_awesome; break;
    }

    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        color: Colors.black,
        shape: BoxShape.circle,
        border: Border.all(color: color, width: 1.5),
      ),
      child: Icon(icon, size: 12, color: color),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    if (diff.inDays > 7) return '${(diff.inDays / 7).floor()}w';
    if (diff.inDays > 0) return '${diff.inDays}d';
    if (diff.inHours > 0) return '${diff.inHours}h';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m';
    return 'now';
  }
}