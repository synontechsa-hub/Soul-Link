import '../state/app_session.dart';
import '../models/bot_model.dart';
import '../models/conversation_model.dart';
import '../models/message_model.dart';
import '../models/user_model.dart';

void seedAppSession(AppSession session) {
  // Create fake user
  final user = UserModel(
    id: 'user_1',
    screenName: 'Tester',
    createdAt: DateTime.now().subtract(const Duration(days: 10)),
    economy: UserEconomy(currency: 100, points: 250),
  );

  session.currentUser = user;

  // Create bots
  final botA = BotModel(
    id: 'bot_luna',
    name: 'Luna',
    description: 'A calm, thoughtful companion',
    avatarUrl: 'https://i.pravatar.cc/150?img=3',
    persona: BotPersona(
      systemPrompt: 'You are calm and emotionally supportive.',
      traits: ['gentle', 'empathetic'],
    ),
    memoryPolicy: BotMemoryPolicy(
      scope: 'hybrid',
      retentionStrength: 7,
    ),
  );

  final botB = BotModel(
    id: 'bot_ember',
    name: 'Ember',
    description: 'Energetic and playful',
    avatarUrl: 'https://i.pravatar.cc/150?img=5',
    persona: BotPersona(
      systemPrompt: 'You are playful and teasing.',
      traits: ['fun', 'bold'],
    ),
    memoryPolicy: BotMemoryPolicy(
      scope: 'short',
      retentionStrength: 4,
    ),
  );

  session.bots[botA.id] = botA;
  session.bots[botB.id] = botB;

  // Create conversations
  final convoA = ConversationModel(
    id: 'convo_luna',
    userId: user.id,
    botId: botA.id,
    createdAt: DateTime.now().subtract(const Duration(days: 3)),
    lastUpdated: DateTime.now().subtract(const Duration(minutes: 5)),
    messages: [
      MessageModel.bot(
        'Hey… I’m glad you came back.',
      ),
    ],
    state: ConversationState(
      progressionLevel: 2,
      memorySummary: 'User feels overwhelmed lately.',
    ),
  );

  final convoB = ConversationModel(
    id: 'convo_ember',
    userId: user.id,
    botId: botB.id,
    createdAt: DateTime.now().subtract(const Duration(days: 1)),
    lastUpdated: DateTime.now().subtract(const Duration(hours: 2)),
    messages: [
      MessageModel.bot(
        'So… did you miss me or what? 😏',
      ),
    ],
    state: ConversationState(
      progressionLevel: 1,
    ),
  );

  session.conversations[convoA.id] = convoA;
  session.conversations[convoB.id] = convoB;
}
