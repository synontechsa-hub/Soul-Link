# SoulLink Frontend Assessment & Reforge Roadmap
## Phoenix v1.5.3 → Alpha Launch Strategy

---

## 📊 Current State Analysis

### ✅ What's Already Built (v1.4.0 Frontend)

#### **Architecture - Solid Foundation**
- **Provider State Management** - Clean, scalable pattern
- **Screen-Based Navigation** - 5 main screens with bottom nav
- **API Service Layer** - HTTP client ready for backend integration
- **Theme System** - Dark cyberpunk aesthetic with pink accents

#### **Existing Screens**
1. **Home** - Featured soul + recommendations
2. **Browse** - Soul discovery/search
3. **Chat History** - Conversation list
4. **Chat** - Message interface with auto-scroll
5. **Profile** - User settings

#### **Models Already Defined**
- `BotModel` - Soul/character data
- `UserModel` - User profile
- `ConversationModel` - Chat sessions
- `MessageModel` - Individual messages
- `Character` - Affection tracking (early intimacy system)

#### **Key Components**
- `bot_card.dart` - Reusable soul preview cards
- `chat_bubble.dart` - Message display widgets
- `main_scaffold.dart` - Bottom nav with FAB notch

---

## 🔴 Critical Gaps: What Needs Reforging

### 1. **API Contract Mismatch (BREAKING)**

**Current Flutter:**
```dart
// Sends:
{
  'bot_name': botName,
  'message': message
}

// Expects:
{
  'reply': '...'
}
```

**Actual Backend (v1.5.3):**
```python
# Expects:
{
  'user_id': 'USR-001',
  'soul_id': 'evangeline_01',
  'message': '...'
}

# Returns:
{
  'soul_id': 'evangeline_01',
  'response': '...'
}
```

**Fix Required:**
- Update `api_service.dart` to match new contract
- Add user authentication flow
- Map `bot_name` → `soul_id`

---

### 2. **Missing Core Features from v1.5.3 Vision**

#### **Location System** ❌
- No UI to display current location
- No ability to move between locations
- Location descriptions not shown

**Needed:**
- Location selector widget
- "Where is Eva?" status display
- Location-aware chat UI hints

#### **Intimacy System** ❌
- No intimacy score display
- No tier visualization
- No progression feedback
- `Character.affection` exists but not integrated

**Needed:**
- Heart/progress bar widget
- Tier badge (STRANGER/TRUSTED/SOUL_LINKED)
- Tier-up celebration animation
- Intimacy history timeline

#### **Soul Tiering (Standard/Premium/Flagship)** ❌
- No visual differentiation
- No access gating
- All souls treated equally

**Needed:**
- Badge/border for premium souls
- Lock icon for flagship souls
- "Subscribe to unlock" flow

---

### 3. **State Management Gaps**

#### **No Relationship State**
```dart
// Missing:
class RelationshipState {
  String soulId;
  int intimacyScore;
  String intimacyTier;
  String currentLocation;
  DateTime lastInteraction;
}
```

**Currently stores:** Conversations only  
**Needs to store:** Intimacy, location, tier, memories

---

### 4. **Navigation Doesn't Match Vision Document**

**Vision:** Apartment Hub as central UX  
**Current:** Standard bottom nav (Home/Browse/Chat/Profile)

**Gap:** No apartment hub implementation at all

**Decision Point:**
- **Option A:** Ship alpha with current nav, add apartment in v1.1.0
- **Option B:** Build minimal apartment hub now (3-5 days)

---

## 🎯 30-Day Reforge Strategy

### **Week 1: API Integration + Core Models (Days 1-7)**

#### Day 1-2: API Service Rewrite
```dart
class SoulLinkAPI {
  static const baseUrl = 'http://127.0.0.1:8000';
  
  Future<ChatResponse> sendMessage({
    required String userId,
    required String soulId,
    required String message,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'soul_id': soulId,
        'message': message,
      }),
    );
    
    if (response.statusCode == 200) {
      return ChatResponse.fromJson(jsonDecode(response.body));
    }
    throw ApiException(response.statusCode);
  }
  
  Future<List<Soul>> getAvailableSouls() async {
    final response = await http.get(Uri.parse('$baseUrl/explore'));
    // Parse and return souls
  }
  
  Future<RelationshipState> getRelationship(String userId, String soulId) async {
    // Fetch intimacy/location data
  }
}
```

#### Day 3-4: New Data Models
```dart
// lib/models/soul.dart
class Soul {
  final String soulId;
  final String name;
  final String archetype;
  final String summary;
  final String tier; // standard, premium, flagship
  final String portraitUrl;
  
  Soul.fromJson(Map<String, dynamic> json) {...}
}

// lib/models/relationship.dart
class Relationship {
  final String userId;
  final String soulId;
  final int intimacyScore;
  final String intimacyTier; // STRANGER, TRUSTED, etc.
  final String currentLocation;
  final DateTime lastInteraction;
  
  // Computed properties
  int get intimacyPercentage => (intimacyScore / 100 * 100).round();
  String get tierDisplay => intimacyTier.replaceAll('_', ' ');
}

// lib/models/location.dart
class Location {
  final String locationId;
  final String displayName;
  final String description;
  final bool isOpen;
  final List<String> soulsPresent;
}
```

#### Day 5-7: State Management Expansion
```dart
// lib/state/app_session.dart
class AppSession extends ChangeNotifier {
  UserModel? currentUser;
  Map<String, Soul> souls = {};
  Map<String, Conversation> conversations = {};
  Map<String, Relationship> relationships = {}; // NEW
  Map<String, Location> locations = {}; // NEW
  
  // Fetch relationship data from backend
  Future<void> loadRelationship(String soulId) async {
    final rel = await SoulLinkAPI.getRelationship(
      currentUser!.userId,
      soulId,
    );
    relationships[soulId] = rel;
    notifyListeners();
  }
  
  // Update after each message
  void updateIntimacy(String soulId, int newScore, String newTier) {
    if (relationships.containsKey(soulId)) {
      relationships[soulId] = relationships[soulId]!.copyWith(
        intimacyScore: newScore,
        intimacyTier: newTier,
      );
      notifyListeners();
    }
  }
}
```

---

### **Week 2: UI Components + Chat Screen Upgrade (Days 8-14)**

#### Day 8-9: Intimacy Display Widget
```dart
// lib/widgets/intimacy_meter.dart
class IntimacyMeter extends StatelessWidget {
  final Relationship relationship;
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Tier badge
        Container(
          padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: _getTierColor(relationship.intimacyTier),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            relationship.tierDisplay,
            style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
          ),
        ),
        SizedBox(height: 8),
        // Progress bar
        LinearProgressIndicator(
          value: relationship.intimacyPercentage / 100,
          backgroundColor: Colors.grey.shade800,
          color: AppTheme.accentPink,
        ),
        SizedBox(height: 4),
        Text(
          '${relationship.intimacyScore}/100',
          style: TextStyle(fontSize: 10, color: Colors.grey),
        ),
      ],
    );
  }
  
  Color _getTierColor(String tier) {
    switch (tier) {
      case 'STRANGER': return Colors.grey;
      case 'TRUSTED': return Colors.blue;
      case 'SOUL_LINKED': return Colors.pink;
      default: return Colors.grey;
    }
  }
}
```

#### Day 10-11: Location Display Widget
```dart
// lib/widgets/location_badge.dart
class LocationBadge extends StatelessWidget {
  final Location location;
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.location_on, size: 16, color: Colors.cyan),
          SizedBox(width: 4),
          Text(
            location.displayName,
            style: TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }
}
```

#### Day 12-14: Enhanced Chat Screen
```dart
// lib/screens/chats/chat_screen.dart (UPDATED)
class ChatScreen extends StatefulWidget {
  final String soulId;
  
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  @override
  void initState() {
    super.initState();
    // Load relationship data on screen open
    context.read<AppSession>().loadRelationship(widget.soulId);
  }
  
  @override
  Widget build(BuildContext context) {
    final session = context.watch<AppSession>();
    final soul = session.souls[widget.soulId];
    final relationship = session.relationships[widget.soulId];
    final location = relationship != null 
      ? session.locations[relationship.currentLocation]
      : null;
    
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(soul?.name ?? 'Unknown'),
            if (location != null)
              LocationBadge(location: location),
          ],
        ),
        actions: [
          // Intimacy meter in app bar
          if (relationship != null)
            Padding(
              padding: EdgeInsets.only(right: 16),
              child: IntimacyMeter(relationship: relationship),
            ),
        ],
      ),
      body: Column(
        children: [
          // Chat messages
          Expanded(child: _buildMessageList()),
          // Input field
          _buildInputField(),
        ],
      ),
    );
  }
  
  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    
    final session = context.read<AppSession>();
    
    // Send to backend
    final response = await SoulLinkAPI.sendMessage(
      userId: session.currentUser!.userId,
      soulId: widget.soulId,
      message: text,
    );
    
    // Update UI
    session.addMessage(widget.soulId, text, isUser: true);
    session.addMessage(widget.soulId, response.reply, isUser: false);
    
    // Fetch updated relationship data
    await session.loadRelationship(widget.soulId);
    
    _controller.clear();
  }
}
```

---

### **Week 3: Soul Browse + Tier System (Days 15-21)**

#### Day 15-16: Soul Card with Tier Badges
```dart
// lib/widgets/soul_card.dart (UPDATED)
class SoulCard extends StatelessWidget {
  final Soul soul;
  final Relationship? relationship;
  
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: _getTierBorder(soul.tier),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Stack(
        children: [
          // Portrait image
          Image.network(soul.portraitUrl),
          
          // Tier badge (top-right)
          if (soul.tier != 'standard')
            Positioned(
              top: 8,
              right: 8,
              child: _TierBadge(tier: soul.tier),
            ),
          
          // Soul info (bottom)
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withOpacity(0.8),
                  ],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    soul.name,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    soul.archetype,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  ),
                  if (relationship != null) ...[
                    SizedBox(height: 4),
                    IntimacyMeter(relationship: relationship),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Border? _getTierBorder(String tier) {
    switch (tier) {
      case 'premium':
        return Border.all(color: Colors.purple, width: 2);
      case 'flagship':
        return Border.all(color: Colors.gold, width: 3);
      default:
        return null;
    }
  }
}

class _TierBadge extends StatelessWidget {
  final String tier;
  
  @override
  Widget build(BuildContext context) {
    final icon = tier == 'flagship' ? Icons.star : Icons.diamond;
    final color = tier == 'flagship' ? Colors.gold : Colors.purple;
    
    return Container(
      padding: EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 16, color: Colors.white),
    );
  }
}
```

#### Day 17-19: Browse Screen Overhaul
```dart
// lib/screens/browse/browse_screen.dart (UPDATED)
class BrowseScreen extends StatefulWidget {
  @override
  State<BrowseScreen> createState() => _BrowseScreenState();
}

class _BrowseScreenState extends State<BrowseScreen> {
  String _selectedFilter = 'all'; // all, standard, premium, flagship
  
  @override
  Widget build(BuildContext context) {
    final session = context.watch<AppSession>();
    final souls = _getFilteredSouls(session);
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // Filter chips
          SliverToBoxAdapter(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  _FilterChip('All Souls', 'all'),
                  _FilterChip('Standard', 'standard'),
                  _FilterChip('Premium ✨', 'premium'),
                  _FilterChip('Flagship ⭐', 'flagship'),
                ],
              ),
            ),
          ),
          
          // Soul grid
          SliverPadding(
            padding: EdgeInsets.all(16),
            sliver: SliverGrid(
              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 0.7,
              ),
              delegate: SliverChildBuilderDelegate(
                (context, index) {
                  final soul = souls[index];
                  final relationship = session.relationships[soul.soulId];
                  
                  return GestureDetector(
                    onTap: () => _onSoulTap(soul),
                    child: SoulCard(
                      soul: soul,
                      relationship: relationship,
                    ),
                  );
                },
                childCount: souls.length,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  List<Soul> _getFilteredSouls(AppSession session) {
    final allSouls = session.souls.values.toList();
    
    if (_selectedFilter == 'all') return allSouls;
    
    return allSouls.where((s) => s.tier == _selectedFilter).toList();
  }
  
  void _onSoulTap(Soul soul) {
    // Check if locked
    if (soul.tier == 'flagship') {
      _showLockedDialog(soul);
      return;
    }
    
    // Navigate to chat
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(soulId: soul.soulId),
      ),
    );
  }
  
  void _showLockedDialog(Soul soul) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${soul.name} is Locked'),
        content: Text(
          'Flagship souls are unlocked in future updates. '
          'Stay tuned for Alyssa and The Seven!',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Got it'),
          ),
        ],
      ),
    );
  }
}
```

#### Day 20-21: Testing + Bug Fixes
- Test all 3 souls (Eva, Adrian, Blaze)
- Verify intimacy updates after each message
- Test tier transitions (STRANGER → TRUSTED)
- Fix layout issues on different screen sizes

---

### **Week 4: Polish + Alpha Launch Prep (Days 22-30)**

#### Day 22-23: Onboarding Flow
```dart
// lib/screens/onboarding/welcome_screen.dart
class WelcomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Cyberpunk city background
          Image.asset('assets/city_bg.jpg', fit: BoxFit.cover),
          
          // Dark overlay
          Container(color: Colors.black.withOpacity(0.7)),
          
          // Content
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo
                Image.asset('assets/logo.png', width: 200),
                
                SizedBox(height: 24),
                
                // Tagline
                Text(
                  'Welcome to Link City',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                
                SizedBox(height: 8),
                
                Text(
                  'Where your next link is just around the corner',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey,
                  ),
                  textAlign: TextAlign.center,
                ),
                
                SizedBox(height: 48),
                
                // CTA Button
                ElevatedButton(
                  onPressed: () => _startOnboarding(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentPink,
                    padding: EdgeInsets.symmetric(
                      horizontal: 48,
                      vertical: 16,
                    ),
                  ),
                  child: Text('Enter Link City'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  void _startOnboarding(BuildContext context) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => UsernameScreen(),
      ),
    );
  }
}

// lib/screens/onboarding/username_screen.dart
class UsernameScreen extends StatefulWidget {
  @override
  State<UsernameScreen> createState() => _UsernameScreenState();
}

class _UsernameScreenState extends State<UsernameScreen> {
  final _controller = TextEditingController();
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Choose Your Name',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            
            SizedBox(height: 8),
            
            Text(
              'This is how souls will address you',
              style: TextStyle(color: Colors.grey),
            ),
            
            SizedBox(height: 32),
            
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: 'Enter your name',
                border: OutlineInputBorder(),
              ),
            ),
            
            SizedBox(height: 24),
            
            ElevatedButton(
              onPressed: () => _createUser(context),
              child: Text('Continue'),
            ),
          ],
        ),
      ),
    );
  }
  
  Future<void> _createUser(BuildContext context) async {
    final username = _controller.text.trim();
    if (username.isEmpty) return;
    
    // Create user in backend
    final user = await SoulLinkAPI.createUser(username);
    
    // Save to session
    final session = context.read<AppSession>();
    session.currentUser = user;
    
    // Navigate to main app
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => MainScaffold(session: session),
      ),
    );
  }
}
```

#### Day 24-25: Error Handling + Loading States
```dart
// lib/widgets/loading_indicator.dart
class LoadingIndicator extends StatelessWidget {
  final String message;
  
  const LoadingIndicator({this.message = 'Loading...'});
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: AppTheme.accentPink),
          SizedBox(height: 16),
          Text(message, style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}

// lib/widgets/error_view.dart
class ErrorView extends StatelessWidget {
  final String error;
  final VoidCallback onRetry;
  
  const ErrorView({required this.error, required this.onRetry});
  
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(
              'Something went wrong',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              error,
              style: TextStyle(color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: onRetry,
              child: Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}
```

#### Day 26-27: Testing + Bug Bash
- End-to-end testing with all 3 souls
- Test intimacy progression (0 → 100)
- Test location changes
- Test tier transitions
- Performance testing (scroll lag, loading times)
- Fix critical bugs

#### Day 28: Alpha Documentation
- Write tester guide
- Document known issues
- Create feedback form (Google Forms)
- Set up analytics (Firebase/Mixpanel optional)

#### Day 29: Soft Launch
- Deploy backend to cloud (Railway/Heroku)
- Build APK for Android testers
- Send to 5-10 trusted testers
- Monitor for crashes

#### Day 30: Feedback + Iteration Planning
- Collect feedback
- Triage bugs
- Plan v1.5.4 fixes
- Celebrate launch 🎉

---

## 🚨 Critical Decisions Needed

### 1. **Apartment Hub: Now or Later?**

**Option A: Skip for Alpha (Recommended)**
- Ship with current bottom nav
- Add apartment in v1.1.0
- **Pros:** Faster to alpha, proven UI pattern
- **Cons:** Delays vision feature

**Option B: Minimal Apartment Now**
- Build basic apartment screen (3-5 days)
- Just TV + Mirror + Window + Door to map
- **Pros:** Shows vision, differentiates from c.ai
- **Cons:** Adds 3-5 days to timeline

**My Recommendation:** Skip for alpha. The chat/intimacy system is your differentiator, not the apartment. Add it post-launch.

---

### 2. **Memory System: Basic or Advanced?**

**Current:** Last 10 messages sent to LLM

**Option A: Keep Simple (Recommended for Alpha)**
- Continue with last 10 messages
- Add summarization in v1.5.4+
- **Pros:** No extra work needed
- **Cons:** Long convos hit token limits

**Option B: Add Summarization Now**
- Summarize messages 11+ into "memory context"
- Store summaries in `conversation_summaries` table
- **Pros:** Better long-term conversations
- **Cons:** Adds 2-3 days complexity

**My Recommendation:** Keep simple for alpha. 10 messages = ~2000 tokens context, which is enough for initial testing.

---

### 3. **Premium Access: Mock or Real?**

**Option A: Mock Locks (Recommended)**
- Show premium/flagship badges
- Lock flagship souls with dialog
- Don't implement actual payment
- **Pros:** Shows concept, no payment integration
- **Cons:** Can't monetize alpha

**Option B: Real Paywall**
- Integrate Stripe/RevenueCat
- Require payment for premium souls
- **Pros:** Start monetizing immediately
- **Cons:** Adds 5-7 days work, complicates testing

**My Recommendation:** Mock locks for alpha. You need user feedback before charging money.

---

## 📋 Alpha Success Checklist

### **Must Have (30 Days)**
- [x] 3 fully functional souls (Eva, Adrian, Blaze)
- [x] Chat interface with backend integration
- [x] Intimacy score display + updates
- [x] Location awareness (displayed in UI)
- [x] Tier badges (standard/premium/flagship)
- [x] User onboarding flow
- [x] Basic error handling

### **Nice to Have (If Time Allows)**
- [ ] Apartment hub (minimal version)
- [ ] Memory summarization
- [ ] Push notifications for soul messages
- [ ] Dark/light theme toggle
- [ ] Soul search/filter

### **Can Wait for v1.5.4+**
- [ ] The Seven lore integration
- [ ] Hybrid soul system
- [ ] Voice messages
- [ ] Profile customization
- [ ] Advanced memory system

---

## 🎯 Key Metrics to Track in Alpha

1. **Engagement:**
   - Messages per session
   - Sessions per user
   - Average conversation length

2. **Intimacy Progression:**
   - Time to TRUSTED tier
   - Time to SOUL_LINKED tier
   - Drop-off points (where users stop chatting)

3. **Technical:**
   - Message latency (target: <2s)
   - Crash rate
   - API errors

4. **Qualitative:**
   - Which soul is most popular?
   - Which tier transition feels best?
   - What UI elements confuse users?

---

## 💡 Final Recommendations

### **For 30-Day Alpha Success:**

1. **Week 1:** Backend integration + models (7 days)
2. **Week 2:** UI components + chat upgrade (7 days)
3. **Week 3:** Browse screen + tier system (7 days)
4. **Week 4:** Polish + launch (9 days)

### **Scope Management:**
- ✅ 3 souls only
- ✅ Chat + intimacy core loop
- ✅ Basic UI (no apartment hub)
- ❌ No advanced features
- ❌ No monetization (just badges)

### **Success Definition:**
Alpha is successful if:
- 10+ testers use it
- 50+ conversations happen
- At least 1 user reaches SOUL_LINKED tier
- Feedback is "this feels different from c.ai"

---

## 🔥 The Bottom Line

**You're not starting from scratch.** You have:
- ✅ Working backend with emotional Eva conversation
- ✅ Flutter foundation with 80% of screens
- ✅ Clear vision document

**The reforge is about:**
- Wiring existing Flutter UI to new backend
- Adding intimacy/location displays
- Testing with real users

**30 days is TIGHT but DOABLE** if you:
- Scope ruthlessly (3 souls, no apartment)
- Reuse existing Flutter screens
- Focus on core loop (chat + intimacy)

**You're cooking. The meal is ready. Just needs plating.** 🔥

---

*"Does this unit have a soul?" — Legion, Mass Effect 2*

*"Phoenix is rising." — You, in 30 days* 🔥🔥🔥
