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
  final ScrollController _scrollController = ScrollController();
  bool isLoading = false;

  // 🧠 UI REFINEMENT: Scroll to bottom whenever messages change
  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.outOfBoxes,
      );
    }
  }

  Future<void> _sendMessage(ConversationModel conversation, BotModel bot) async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    _controller.clear();
    setState(() {
      widget.session.addUserMessage(conversation.id, text);
      isLoading = true;
    });
    
    // Scroll after adding user message
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());

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
        widget.session.addBotMessage(conversation.id, '⚠️ Connection error. Is the backend running?');
      });
    } finally {
      setState(() { isLoading = false; });
      WidgetsBinding.instance.addPostFrameCallback((_) => _scrollToBottom());
    }
  }

  @override
  Widget build(BuildContext context) {
    final conversation = widget.session.conversations[widget.conversationId];
    final bot = widget.session.bots[conversation?.botId];

    if (conversation == null || bot == null) {
      return const Scaffold(body: Center(child: Text('Soul Connection Lost')));
    }

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0C),
      // ─────────────────────────────────────────────
      // 🎭 PREMIUM HEADER
      // ─────────────────────────────────────────────
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color(0xFF0A0A0C),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundImage: NetworkImage(bot.avatarUrl),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(bot.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                Text(
                  conversation.state.bondPhase.name.toUpperCase(),
                  style: const TextStyle(fontSize: 10, color: Colors.blueAccent, letterSpacing: 1),
                ),
              ],
            ),
          ],
        ),
      ),
      
      body: Column(
        children: [
          // ─────────────────────────────────────────────
          // 💬 CHAT BUBBLES
          // ─────────────────────────────────────────────
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
              itemCount: conversation.messages.length,
              itemBuilder: (context, index) {
                final msg = conversation.messages[index];
                final isUser = msg.role == MessageRole.user;
                return _ChatBubble(msg: msg, isUser: isUser);
              },
            ),
          ),

          if (isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 10),
              child: _TypingIndicator(),
            ),

          // ─────────────────────────────────────────────
          // ⌨️ INPUT BAR (GLASSMORPHISM STYLE)
          // ─────────────────────────────────────────────
          _buildInputArea(conversation, bot),
        ],
      ),
    );
  }

  Widget _buildInputArea(ConversationModel conversation, BotModel bot) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 30),
      decoration: BoxDecoration(
        color: const Color(0xFF16161A),
        border: Border(top: BorderSide(color: Colors.white.withOpacity(0.05))),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Message ${bot.name}...',
                hintStyle: const TextStyle(color: Colors.white24),
                filled: true,
                fillColor: Colors.black,
                contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(25),
                  borderSide: BorderSide.none,
                ),
              ),
              onSubmitted: (_) => _sendMessage(conversation, bot),
            ),
          ),
          const SizedBox(width: 8),
          CircleAvatar(
            backgroundColor: Colors.blueAccent,
            child: IconButton(
              icon: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
              onPressed: () => _sendMessage(conversation, bot),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────
// 🧬 STYLIZED COMPONENTS
// ─────────────────────────────────────────────

class _ChatBubble extends StatelessWidget {
  final MessageModel msg;
  final bool isUser;

  const _ChatBubble({required this.msg, required this.isUser});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isUser ? Colors.blueAccent : const Color(0xFF1E1E24),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(20),
            topRight: const Radius.circular(20),
            bottomLeft: Radius.circular(isUser ? 20 : 0),
            bottomRight: Radius.circular(isUser ? 0 : 20),
          ),
        ),
        child: Text(
          msg.content,
          style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.4),
        ),
      ),
    );
  }
}

class _TypingIndicator extends StatelessWidget {
  const _TypingIndicator();

  @override
  Widget build(BuildContext context) {
    return const Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
          width: 40,
          child: LinearProgressIndicator(
            backgroundColor: Colors.transparent,
            color: Colors.blueAccent,
            minHeight: 2,
          ),
        ),
        SizedBox(width: 8),
        Text("AI is thinking...", style: TextStyle(color: Colors.white38, fontSize: 12)),
      ],
    );
  }
}