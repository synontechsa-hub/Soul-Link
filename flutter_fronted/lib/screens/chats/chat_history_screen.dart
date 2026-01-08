import 'package:flutter/material.dart';
import '../../state/app_session.dart';
import '../../models/conversation_model.dart';
import '../../models/bot_model.dart';

class ChatHistoryScreen extends StatelessWidget {
  final AppSession session;

  const ChatHistoryScreen({super.key, required this.session});

  @override
  Widget build(BuildContext context) {
    final conversations = session.conversations.values.toList()
      ..sort((a, b) => b.lastUpdated.compareTo(a.lastUpdated));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chats'),
        backgroundColor: Colors.black,
      ),
      body: ListView.builder(
        itemCount: conversations.length,
        itemBuilder: (context, index) {
          final conversation = conversations[index];
          final bot = session.bots[conversation.botId];

          if (bot == null) return const SizedBox.shrink();

          return _ChatHistoryTile(
            bot: bot,
            conversation: conversation,
            onTap: () {
              // Step 3 will wire this
            },
          );
        },
      ),
    );
  }
}

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
    final lastMessage = conversation.messages.isNotEmpty
        ? conversation.messages.last.content
        : 'Start a conversation';

    return ListTile(
      onTap: onTap,
      leading: CircleAvatar(
        backgroundImage: NetworkImage(bot.avatarUrl),
      ),
      title: Text(
        bot.name,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
      subtitle: Text(
        lastMessage,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Text(
        _formatTime(conversation.lastUpdated),
        style: const TextStyle(fontSize: 12, color: Colors.grey),
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inDays > 0) {
      return '${difference.inDays}d';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}h';
    } else {
      return '${difference.inMinutes}m';
    }
  }
}
