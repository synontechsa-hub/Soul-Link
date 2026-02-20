# Multi-LLM Workflow Guide for SoulLink v1.6.0 Sprint
## Optimized for Solo Dev Speed + Quality

**Your Setup:**
- Sonnet 4.6 (Antigravity)
- Gemini Flash 3 (Antigravity)
- Gemini 3.1 Pro (Antigravity)
- Claude Haiku 4.5 (Web)
- Gemini 3 Pro (Web)
- GPT-5 (Web)
- Grok (Web)
- Copilot (IDE)

---

## 🎯 THE OPTIMAL WORKFLOW

### TIER 1: PRIMARY TOOLS (Keep open at all times)

#### **SONNET 4.6** — "The Implementation Engine"
**What it's best at:** Deep code implementation, detailed API design, SQL optimization  
**What to ask it:** Implementation questions, code reviews, architectural changes  
**When to use:** When you need production-grade code

**Example Tasks:**
```
✓ "Implement memory_service.py with store/retrieve methods"
✓ "Review my LinkState migration for issues"
✓ "Optimize this database query for speed"
✓ "Write the APScheduler background task for stability decay"
✓ "Debug why my async function is hanging"
```

**Red Flags (Don't ask Sonnet):**
```
✗ "Should I use Redis or database for caching?" (strategy, not implementation)
✗ "What's the best architecture for my entire system?" (too big-picture)
✗ "Make me laugh" (it'll try, fail, waste tokens)
```

**Workflow Tips:**
- Keep conversation **focused on ONE file/system**
- Ask for **complete, production-ready code** (not pseudocode)
- Request **inline comments** for complex logic
- Say **"Test this works before returning"** if critical

---

#### **CLAUDE HAIKU 4.5 (Me)** — "The Architect & Auditor"
**What I'm best at:** Big-picture strategy, system design, gap analysis, decision-making  
**What to ask me:** Planning, architecture, "should I do X or Y", audit review  
**When to use:** Before/after major work, decision points, comprehensive reviews

**Example Tasks:**
```
✓ "Is my priority order correct for v1.6.0?"
✓ "Should LinkState have X field or Y field?"
✓ "Review my implementation plan for memory system"
✓ "What's the critical path to alpha launch?"
✓ "Help me decide: background task or cron job?"
✓ "Audit this system for gaps I might have missed"
```

**Red Flags (Don't ask me):**
```
✗ "Write me the memory_service.py code" (ask Sonnet)
✗ "Debug this Python error" (ask Sonnet or Copilot)
✗ "Optimize this SQL query" (ask Sonnet)
```

**Workflow Tips:**
- Ask **before** major implementation work
- Use my audits to **validate Sonnet's approach**
- I'm good at **catching architectural problems** others miss
- Ask me **"what did I miss?" about your plan**

---

#### **GEMINI FLASH 3** — "The Speed Demon"
**What it's best at:** Quick answers, syntax issues, small fixes, fast iteration  
**What to ask it:** "How do I [quick thing]", small code snippets, imports  
**When to use:** When you need an answer in < 2 minutes, small blockers

**Example Tasks:**
```
✓ "How do I format a datetime in Python?"
✓ "What's the Pydantic syntax for enum fields?"
✓ "Quick fix: how do I import this module?"
✓ "What does this error mean?"
✓ "Should I use @property or a method here?"
✓ "Write a 5-line utility function to..."
```

**Red Flags (Don't ask Flash):**
```
✗ "Design my memory system" (needs Sonnet/me)
✗ "Review my entire implementation" (it'll be shallow)
✗ "Help me debug a complex async issue" (ask Sonnet)
```

**Workflow Tips:**
- **Keep it in Antigravity** (that's where Flash lives)
- Don't ask Flash to think deeply — it shines at fast, shallow answers
- Perfect for **unblocking yourself quickly**
- **Close the tab after** — don't let it distract you

---

### TIER 2: DECISION-MAKING TOOLS (Use when Tier 1 disagrees)

#### **GEMINI 3.1 PRO** — "The Lateral Thinker"
**What it's best at:** Novel approaches, creative solutions, complex multi-system thinking  
**What to ask it:** "How else could I solve this?", unconventional approaches, system interactions  
**When to use:** When you're stuck, or need 2+ perspectives on a design decision

**Example Tasks:**
```
✓ "I'm implementing memory decay. What approaches would you suggest?"
✓ "Should stability decay happen on message or in background? Pros/cons?"
✓ "Event hook system: LLM generation or pre-written? Which is better?"
✓ "How would you structure the narrator system differently?"
✓ "Help me brainstorm the LinkState relationship status logic"
```

**Red Flags (Don't ask 3.1 Pro):**
```
✗ "Write me the code" (ask Sonnet)
✗ "Debug this error" (ask Sonnet)
```

**Workflow Tips:**
- Use this for **design disagreements** between Sonnet and me
- Ask "**what would you do differently?**"
- Good for **stress-testing your approach**
- Compare 3 models' answers: you pick the best

---

#### **GPT-5** — "The Enterprise Perspective"
**What it's best at:** Enterprise patterns, edge cases, comprehensive thinking, best practices  
**What to ask it:** "Will this scale?", "What am I missing?", security review, production readiness  
**When to use:** Final checkpoint before shipping, edge case discovery

**Example Tasks:**
```
✓ "Security review: Are my WebSocket connections safe?"
✓ "Will this approach scale to 1000 concurrent users?"
✓ "What edge cases might I have missed in the energy system?"
✓ "Is my error handling comprehensive enough for production?"
✓ "Spot check my database schema for future problems"
```

**Red Flags (Don't ask GPT-5):**
```
✗ "Implement this feature" (ask Sonnet)
✗ "Quick syntax question" (ask Flash)
```

**Workflow Tips:**
- Use **after** Sonnet implements something
- Ask **"Will this fail in production?"**
- Good for **security, scale, edge case thinking**
- Think of it as **the skeptical senior engineer**

---

### TIER 3: SPECIALIZED TOOLS (Use as needed)

#### **GROK** — "The Chaos Theorist"
**What it's best at:** Edge cases, absurd scenarios, "what if", stress-testing logic, finding weird bugs  
**What to ask it:** "What could go wrong?", "Break this system", unusual scenarios  
**When to use:** Before final launch, to find weird bugs humans miss

**Example Tasks:**
```
✓ "What happens if a user sends 100 messages per second?"
✓ "How would a hacker exploit my WebSocket?"
✓ "What if stability goes negative? Do I handle that?"
✓ "What weird combinations of user actions could break my system?"
✓ "Imagine the strangest possible user behavior. How does my app handle it?"
```

**Red Flags (Don't ask Grok):**
```
✗ "Write production code" (it'll joke instead)
✗ "Debug this serious issue" (might not be thorough enough)
```

**Workflow Tips:**
- Use Grok **as your chaos monkey**
- Ask it to **break your system**
- Great for finding **weird state combinations**
- Results often funny AND useful
- **Do this 2-3 days before launch**

---

#### **COPILOT (IDE)** — "Your Code Assistant"
**What it's best at:** Context-aware code completion, syntax, pattern matching  
**What to ask it:** Type `//` and let it autocomplete, suggest implementations based on context  
**When to use:** While actively coding, for boilerplate, quick implementations

**Example Tasks:**
```
✓ Auto-complete function signatures based on context
✓ Suggest full implementations of similar functions
✓ Generate test boilerplate
✓ Suggest error handling patterns
✓ Auto-format and refactor code blocks
```

**Red Flags (Don't ask Copilot):**
```
✗ "Explain database design" (ask me/Sonnet)
✗ "Help me think through this system" (ask me)
```

**Workflow Tips:**
- **Keep it passive** — it's for when you're typing
- Use keyboard shortcuts: Tab to accept suggestions
- Use it for **boilerplate and repetitive code**
- Don't let it distract from your actual coding

---

#### **GEMINI 3 PRO** — "The Backup Genius"
**What it's best at:** Anything Gemini 3.1 Pro can do, plus a backup perspective  
**What to ask it:** Same as 3.1 Pro, OR when 3.1 Pro and others disagree  
**When to use:** Tiebreaker, second opinion, fresh perspective

**Example Tasks:**
```
✓ "Gemini 3.1 Pro says X, Sonnet says Y. Which is better?"
✓ "Give me your take on the memory decay approach"
✓ "Fresh eyes: what's wrong with this design?"
```

**Red Flags (Don't ask Gemini 3 Pro):**
```
✗ "Actually just ask 3.1 Pro instead" (this is the backup)
```

**Workflow Tips:**
- Don't open unless **other models disagree**
- Acts as **tiebreaker**
- Keeps **discussion fresh**

---

## 📋 WORKFLOW BY TASK TYPE

### Task: Implementing a Feature (e.g., Memory System)

```
1. PLAN (30 min)
   Ask ME (Haiku):
   "Here's my memory system plan: [describe]
    - Should I implement store/retrieve as separate methods?
    - How should decay work?
    - Where should this integrate?"
   
2. DESIGN (15 min)
   Ask GEMINI 3.1 PRO:
   "What alternative approaches would you suggest for memory decay?"
   (Compare approaches with my suggestion)

3. IMPLEMENT (2-3 hours)
   Ask SONNET 4.6:
   "Implement backend/app/services/memory_service.py with:
    - async def store_memory()
    - async def retrieve_memories()
    - Memory decay calculation
    Production-ready code please."

4. BLOCKERS (as they happen)
   Ask GEMINI FLASH:
   "Quick: how do I format this datetime?" or similar

5. FINAL CHECK (15 min)
   Ask GPT-5:
   "Security review: will my memory implementation be safe?
    Edge cases I might have missed?"
   
   Ask ME (Haiku):
   "Does this fit the architecture? Any issues?"

6. CHAOS TEST (optional, pre-launch)
   Ask GROK:
   "What weird things could happen with my memory system?"
```

---

### Task: Debugging an Issue

```
1. QUICK FIX? (< 5 min issue)
   Ask GEMINI FLASH:
   "This error: [error message]. What does it mean?"

2. COMPLEX BUG? (30+ min issue)
   Ask SONNET 4.6:
   "I'm getting [symptom]. Here's my code: [code].
    What's wrong and how do I fix it?"
   
   If still stuck, ask ME (Haiku):
   "I've been stuck on this. Fresh perspective?"

3. ARCHITECTURAL BUG?
   Ask ME:
   "Is this a design problem or implementation problem?"
```

---

### Task: Making an Architecture Decision

```
1. PROPOSE (15 min)
   Ask ME:
   "For [system], should I do X or Y? Pros/cons?"

2. CHALLENGE (10 min)
   Ask GEMINI 3.1 PRO:
   "I'm leaning toward X. Why might Z be better?"

3. ENTERPRISE CHECK (10 min)
   Ask GPT-5:
   "Will approach X work at scale? Edge cases?"

4. FINAL DECISION
   Weigh all 3 perspectives. Go with strongest consensus.
```

---

### Task: Pre-Launch Review (Day before shipping)

```
1. Architecture Audit (30 min)
   Ask ME:
   "Full system review. What could break in production?"

2. Code Quality (30 min)
   Ask SONNET 4.6:
   "Review all my critical files. Issues?"

3. Edge Cases (20 min)
   Ask GROK:
   "Break this. What am I not handling?"

4. Enterprise Check (20 min)
   Ask GPT-5:
   "Production readiness checklist. Missing anything?"

5. Fresh Eyes (15 min)
   Ask GEMINI 3 PRO:
   "Anything these other models missed?"

Result: Professional-grade pre-launch review.
```

---

## ⚡ THE 2-WEEK SPRINT SCHEDULE

### Week 1: Implementation (Priority 1 Blockers)

**Monday-Tuesday: Memory System**
```
MON 9am:  Ask ME - "Validate my memory system plan"
MON 10am: Ask SONNET - "Implement memory_service.py"
MON 2pm:  Ask FLASH - Any quick syntax issues
TUE 10am: Ask GPT-5 - "Security review of memory queries"
TUE 2pm:  Ask ME - "Validate integration into chat.py"
```

**Wednesday: Stability Decay**
```
WED 9am:  Ask ME - "Should decay be background task or cron?"
WED 10am: Ask GEMINI 3.1 PRO - "What's the best decay algorithm?"
WED 11am: Ask SONNET - "Implement APScheduler decay job"
WED 2pm:  Ask GROK - "What happens if decay runs during a message?"
```

**Thursday: Event Hooks**
```
THU 9am:  Ask ME - "Event hook wiring architecture"
THU 10am: Ask SONNET - "Wire hooks into chat endpoint"
THU 2pm:  Ask FLASH - Any integration issues
THU 3pm:  Ask GPT-5 - "Will this handle concurrent events safely?"
```

**Friday: LinkState + Polish**
```
FRI 9am:  Ask SONNET - "Add relationship_status enum"
FRI 10am: Ask ME - "Validate all Priority 1 complete"
FRI 2pm:  Test everything
FRI 4pm:  Version bump to 1.5.7
```

### Week 2: Testing + Launch Prep (Priority 2 + Shipping)

**Monday-Tuesday: Unit Tests**
```
MON 9am:  Ask SONNET - "Generate test files for memory, decay, events"
MON 2pm:  Ask COPILOT - Auto-complete test boilerplate
TUE 10am: Run all tests
TUE 2pm:  Ask SONNET - Fix failing tests
```

**Wednesday: Load Testing**
```
WED 9am:  Ask GPT-5 - "Load testing strategy for 50 msgs/hour"
WED 10am: Ask SONNET - "Write load test script"
WED 2pm:  Run load tests
WED 3pm:  Ask SONNET - Optimize slow paths
```

**Thursday-Friday: Final Checks**
```
THU 9am:  Ask ME - Final architecture review
THU 10am: Ask GROK - "Break this system"
THU 2pm:  Ask GPT-5 - "Production readiness"
FRI 10am: Ask ME - "Ready for alpha?"
FRI 2pm:  Version bump to 1.6.0
FRI 3pm:  Deploy to closed alpha testers
```

---

## 🚨 CRITICAL RULES

### Rule 1: Don't Ask Wrong Model for Task
```
WRONG: Ask FLASH for "design my entire event system" → Shallow answer
RIGHT: Ask SONNET for implementation, ME for design

WRONG: Ask SONNET "am I overthinking this?" → It won't help
RIGHT: Ask ME for architectural perspective

WRONG: Ask ME "write the code" → Not my specialty
RIGHT: Ask ME "validate the approach", then SONNET for code
```

### Rule 2: Always Validate Between Models
```
If SONNET and I disagree:
  → Ask GEMINI 3.1 PRO for third perspective
  → Ask GPT-5 for production implications
  → Make informed decision

If all 3 agree:
  → You're confident
  
If 2/3 disagree:
  → That's a genuine design question worth more thought
```

### Rule 3: Context Matters
```
Keep models "warm" with context:
- Don't switch every 5 minutes
- Let SONNET stay on memory system for 2 hours
- Let ME review your entire plan before breaking it up

Switching context = wasted tokens and bad answers
```

### Rule 4: Close Unnecessary Tabs
```
During focused work:
  OPEN:   Sonnet 4.6, Gemini Flash, Copilot
  CLOSED: Everything else
  
During decision-making:
  OPEN:   Me (Haiku), Gemini 3.1 Pro, GPT-5
  CLOSED: Flash, implementation tools
  
Only open GROK day before launch
```

### Rule 5: Trust the Consensus
```
If 7/8 models say "this is wrong" → It's probably wrong
If 7/8 models say "this is good" → Ship it
If 4/8 say "this works", 4 say "risky" → Needs more thought

Consensus is your quality signal.
```

---

## 📊 EXPECTED OUTCOMES

### With This Workflow, You Should Get:

✅ **Speed:** Each task goes to the right model → 40% faster  
✅ **Quality:** 8 models cross-checking → Enterprise grade  
✅ **Confidence:** Consensus validates decisions → Ship faster  
✅ **Coverage:** Different perspectives catch different bugs → Fewer surprises  

### By Early March:
- v1.5.7: Memory system working ✅
- v1.5.8: Decay + Events working ✅
- v1.5.9: Tested + polished ✅
- v1.6.0: Ready to ship to 10 closed testers ✅

---

## 🎯 TL;DR CHEAT SHEET

```
QUICK QUESTION?           → GEMINI FLASH
IMPLEMENT IT?             → SONNET 4.6
BIG PICTURE?              → ME (HAIKU)
STUCK/NEED NEW ANGLE?     → GEMINI 3.1 PRO
WILL IT SCALE?            → GPT-5
FIND THE WEIRD BUGS?      → GROK
WHILE CODING?             → COPILOT
TIEBREAKER?               → GEMINI 3 PRO
```

---

## Good Luck! 🚀

You've got:
- 8 models running at peak efficiency
- Clear task assignments for each
- A proven system for consensus validation
- 2 weeks to ship v1.6.0

Time to build.

