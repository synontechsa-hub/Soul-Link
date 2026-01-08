import 'package:flutter/material.dart';

import '../../state/app_session.dart';
import '../../models/conversation_model.dart';
import '../../models/bot_model.dart';
import '../../models/message_model.dart';
import '../../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  final AppSession session;
  final String conversationId;

  const ChatScreen({
    super.key,
    required this.session,
    required this.conversationId,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  bool isLoading = false;

  Future<void> _sendMessage(
    ConversationModel conversation,
    BotModel bot,
  ) async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      widget.session.addUserMessage(conversation.id, text);
      isLoading = true;
    });

    _controller.clear();

    try {
      final reply = await ApiService.sendMessage(
        botName: bot.name,
        message: text,
      );

      setState(() {
        widget.session.addBotMessage(conversation.id, reply);
      });
    } catch (_) {
      setState(() {
        widget.session.addBotMessage(
          conversation.id,
          '⚠️ Connection error. Is the backend running?',
        );
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final conversation =
        widget.session.conversations[widget.conversationId];
    if (conversation == null) {
      return const Scaffold(
        body: Center(child: Text('Conversation not found')),
      );
    }

    final bot = widget.session.bots[conversation.botId];
    if (bot == null) {
      return const Scaffold(
        body: Center(child: Text('Bot not found')),
      );
    }

    final messages = conversation.messages;

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(bot.name),
            Text(
              'Bond ${conversation.state.progressionLevel}',
              style: const TextStyle(
                fontSize: 12,
                color: Colors.white54,
              ),
            ),
          ],
        ),
        backgroundColor: const Color(0xFF0E0E11),
      ),

      backgroundColor: const Color(0xFF0E0E11),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                final isUser = msg.role == MessageRole.user;

                return Align(
                  alignment:
                      isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    constraints: const BoxConstraints(maxWidth: 500),
                    decoration: BoxDecoration(
                      color: isUser
                          ? const Color(0xFF6C63FF)
                          : const Color(0xFF2A2A2E),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      msg.content,
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                );
              },
            ),
          ),

          if (isLoading)
            const Padding(
              padding: EdgeInsets.all(8),
              child: Text(
                'Typing...',
                style: TextStyle(color: Colors.white54),
              ),
            ),

          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: 'Say something...',
                      filled: true,
                      fillColor: Color(0xFF1E1E24),
                      border: OutlineInputBorder(),
                    ),
                    onSubmitted: (_) =>
                        _sendMessage(conversation, bot),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send, color: Colors.white),
                  onPressed: () =>
                      _sendMessage(conversation, bot),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
