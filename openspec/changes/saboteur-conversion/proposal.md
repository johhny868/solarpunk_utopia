# Proposal: Saboteur Conversion Through Care

**Submitted By:** Philosophical Council
**Date:** 2025-12-19
**Status:** ✅ IMPLEMENTED
**Priority:** P3 - Ongoing
**Philosophy:** Freire, hooks, Kropotkin

## The Premise

Most "sabotage" isn't sabotage at all. It's:
- **Confusion** - they don't understand how this works
- **Bad day** - they snapped, they're stressed, life is hard
- **Habit** - they're used to extractive systems and defaulted to old patterns
- **Trauma** - they've been burned before and are protecting themselves
- **Unmet needs** - hungry people make desperate choices
- **Semi-intentional** - they half-knew it was wrong but did it anyway (we've all been there)

Actual malicious saboteurs are rare. Paid infiltrators are rarer. Most problems are just... people being people.

**This isn't a security system. It's a care system.**

**Exclusion is failure.** If we exclude someone, we've failed to build utopia for them.

## Design Principles

**Gentle.** No shame. No punishment. No public callouts.

**Education, not indoctrination.** We don't tell them they're wrong. We ask questions. We share stories. We invite them to imagine.

**Meet needs first.** You can't radicalize someone who's hungry. Feed them.

**Patience.** Conversion takes time. Maybe years. That's okay.

**No coercion.** They can leave anytime. We don't trap people in rehabilitation.

## Humans, Not Algorithms

This CANNOT be automated. You cannot care for someone through a bot.

```python
class CareVolunteer(BaseModel):
    """Real humans who've chosen to do care work"""
    user_id: str
    name: str

    # Training they've received (from other humans)
    training: List[str]  # ["active_listening", "trauma_informed", "conflict_de_escalation"]

    # Capacity - they're human, they have limits
    currently_supporting: int  # Max 2-3 at a time
    max_capacity: int = 3

    # Support for the supporter
    supervision_partner_id: str  # Someone who checks in on THEM
```

The system just:
- Flags patterns (gently, privately)
- Matches flagged folks with available volunteers
- Gets out of the way

Everything else is human-to-human.

## How We Notice (Not Surveillance)

**We don't track behavior. People tell us things.**

### What We DON'T Do

- ❌ Log activity patterns
- ❌ Track login frequency
- ❌ Monitor who talks to whom
- ❌ Analyze "data access patterns"
- ❌ Compute give/receive ratios
- ❌ Build behavioral profiles
- ❌ Any algorithmic "risk scoring"

That's surveillance. We don't do that.

### What We DO Do

**People notice people. That's it.**

```
Sources of "something's up":

1. SELF-REPORT
   - "Hey, I've been struggling and haven't been showing up"
   - "I messed up, can someone help me make it right?"
   - Check-in prompts (optional): "How are you doing with your commitments?"

2. SOMEONE EXPRESSES CONCERN
   - "Hey, I'm worried about [person]. They seem off."
   - "I had a weird interaction with [person]. Not sure what to make of it."
   - NOT a "report" system. Just humans talking to care coordinator.

3. DIRECT EXPERIENCE
   - "They didn't show up for our exchange"
   - "They said something that made me uncomfortable"
   - The person affected talks to someone, not fills out a form.

4. COMMUNITY CONVERSATION
   - At a meal: "Has anyone heard from Jamie? They've been quiet."
   - This is how communities actually work.
```

### No Forms. No Reports. No Tickets.

```
NOT THIS:
┌─────────────────────────────────┐
│ INCIDENT REPORT FORM            │
│ User ID: _______                │
│ Violation Type: [dropdown]      │
│ Description: ________________   │
│ [SUBMIT]                        │
└─────────────────────────────────┘

THIS:
"Hey Sam, can we talk? Something happened with
the exchange yesterday and I'm not sure what to do."
```

### Care Coordinator Role

One or two people (rotating) who:
- Are known as "the people you can talk to"
- Listen when someone has a concern
- Notice if the same name comes up from multiple people
- Gently suggest: "Want me to connect you with someone who can help?"
- Match people with care volunteers when patterns emerge

They don't:
- Keep databases
- Track incidents
- Score people
- Make judgments

They're a switchboard, not a surveillance system.

### When Does Care Outreach Happen?

```
Level 0-1: Anyone who knows them just... checks in
           No coordination needed. Humans being humans.

Level 2:   Multiple people have mentioned something
           Care coordinator suggests a volunteer befriend them
           Volunteer reaches out casually

Level 3:   Clear harm happening (fake offers, vouch selling)
           Someone directly affected brings it up
           Care coordinator + small circle decides on access limits
           Care volunteer assigned

Level 4:   Someone trusted says "I think this person is a cop"
           Small security circle evaluates
           Access limits + long-game care
```

### What About Fake Offers / Vouch Selling?

These get noticed the old-fashioned way:

**Fake offers:**
- Someone shows up to an exchange and the other person isn't there
- They mention it to friends: "Has anyone else had this happen?"
- If multiple people say yes, word reaches care coordinator
- That's the "detection"

**Vouch selling:**
- Someone notices: "Wait, this person vouched for 20 people this week?"
- They mention it: "Is that normal?"
- Care coordinator: "Hm, let me gently check in with them"
- That's it

**No algorithms. No thresholds. Just people paying attention.**

### Patterns We CAN Track vs CAN'T

**CAN track (necessary for the app to work):**

| Data | Why It Exists | Pattern It Reveals |
|------|---------------|-------------------|
| Offers posted | That's the point of the app | Are they contributing? |
| Needs posted | That's the point of the app | Are they only taking? |
| Exchanges completed | Need to know it happened | Do they follow through? |
| Vouches given | Trust system needs this | Are they vouching responsibly? |
| Vouches received | Trust system needs this | Is their trust earned? |
| Revocations | Trust system needs this | Did their vouches go bad? |
| Votes cast | Voting system needs this | Are they blocking everything? |
| Proposals made | Governance needs this | Are they participating constructively? |

This isn't surveillance - it's the app working. You can't have a gift economy without knowing who offered what.

**Patterns That Are Visible:**

```
TAKING WITHOUT GIVING:
  12 needs, 0 offers → Visible. Address with care.

VOUCH FLOODING:
  20 vouches in a week → Visible. Check in.

VOTE BLOCKADING:
  Joined last week, voted NO on 15 proposals → Visible.
  Not automatically bad (maybe they have good reasons!)
  But worth a conversation.

PROPOSAL SPAMMING:
  50 proposals in a day → Visible. What's going on?

EXCHANGE NON-COMPLETION:
  10 matches, 0 completions → Visible. Something's up.
```

All of these are "noticing what someone did publicly" not "tracking their private behavior."

**CAN'T track (would require adding surveillance):**

| Data | Why We Don't Have It | Would Require |
|------|---------------------|---------------|
| Login frequency | Don't log sessions | Adding session logging |
| Time on app | Don't track this | Adding analytics |
| Pages viewed | Don't track this | Adding analytics |
| Who they looked at | Don't track this | Adding creepy tracking |
| Message content | E2E encrypted | Breaking encryption |
| Location history | Only used for matching | Adding location logging |

We don't build the infrastructure to collect this. No analytics. No session tracking. No behavioral profiling.

**The Difference:**

```
FUNCTIONAL DATA (have it because the app needs it):
  "Jamie has 12 needs and 0 offers"
  → We know this because needs and offers are... the app

SURVEILLANCE DATA (would have to build spy infrastructure):
  "Jamie logs in at 3am and browses for 2 hours"
  → We'd have to deliberately build tracking to know this
  → We don't. We won't.
```

### The "Lots of Needs, No Offers" Thing

Yeah, that's a sign. And it's visible. Anyone scrolling their feed notices:

> "Huh, I've seen Jamie ask for stuff three times this week but I've never seen them offer anything."

That's not surveillance. That's community awareness.

What happens:
1. Someone notices (organically, while using the app)
2. They might mention it to care coordinator: "Is Jamie okay? They seem to need a lot."
3. Care coordinator: "Yeah, let's have someone check in."
4. Care volunteer reaches out: "Hey Jamie! How's it going? Need any help getting set up with offers?"

Maybe Jamie:
- Didn't know how to post offers
- Is going through something and genuinely needs more right now
- Doesn't have anything to offer (help them find something!)
- Is extracting on purpose (rare, but address with care)

The response is the same regardless: befriend, understand, help.

---

## The Spectrum of "Sabotage"

Most cases aren't malicious:

### Level 0: OOPS

**Signs:** Didn't read instructions, honest mistake, clicked wrong button

**Concrete Actions:**
1. Friendly DM from anyone who noticed: "Hey! Looks like X happened - here's how that works..."
2. Link to relevant help doc (if one exists)
3. Offer to walk them through it
4. That's it. No record. No flag. Everyone makes mistakes.

---

### Level 1: STRUGGLING

**Signs:** Flaked on commitments, snapped at someone, taking more than giving lately

**Concrete Actions:**
1. Someone (anyone who knows them) reaches out: "Hey, noticed you've been quiet / seemed stressed. Everything okay?"
2. LISTEN. Don't problem-solve yet.
3. If they share what's going on, ask: "Is there anything the community could help with?"
4. Connect them to resources if relevant (housing help, food, someone to talk to)
5. Follow up in a week
6. No formal tracking. Just humans noticing humans.

---

### Level 2: PATTERN

**Signs:** Repeated no-shows, multiple conflicts, ongoing imbalance, starting to affect others

**Concrete Actions:**
1. **Day 1:** Care volunteer assigned (privately, through care coordinator)
2. **Day 1-3:** Volunteer makes casual contact - NOT about the pattern
   - "Hey! Saw you're in [area]. Want to grab coffee?"
   - Invite to low-stakes event (meal, garden day)
3. **Week 1:** Build relationship. Learn about their life. Don't mention concerns yet.
4. **Week 2-4:** If trust builds, gently explore:
   - "How's the community working for you?"
   - "What would make this better?"
5. **Ongoing:** Meet any needs that surface (housing, work, food, connection)
6. **When ready:** Have honest conversation about patterns - WITH care:
   - "I noticed you've had some no-shows. What's going on?"
   - "No judgment. Just want to help."
7. **Track:** Private notes for continuity if volunteer changes

---

### Level 3: HARMFUL

**Signs:** Vouch selling, fake offers, extracting without giving, possible info harvesting

**Concrete Actions:**
1. **Immediately:** Quietly limit sensitive access (no announcement, no shame)
   - Remove from high-trust channels
   - Pause vouch ability
   - Don't tell them why (yet)
2. **Day 1:** Assign experienced care volunteer
3. **Week 1-2:** Relationship building (same as Level 2)
4. **Week 2-4:** Assess underlying cause:
   - Financial desperation? → Connect to income opportunities
   - Didn't understand impact? → Education through experience
   - Paid by someone? → "We can help you find other work. No judgment."
5. **Week 4+:** If trust builds, direct conversation:
   - "We noticed some things. We're not angry. We want to understand."
   - "What do you need that you're not getting?"
6. **If they come clean:** Celebrate honesty. Help them make it right.
7. **If they deny/deflect:** Keep caring anyway. Keep access limited. Keep door open.
8. **Restoration path:** When ready, they can rebuild trust through:
   - Genuine participation (not performative)
   - Time (months, not days)
   - Vouched back in by people who know them now

---

### Level 4: INFILTRATOR

**Signs:** Confirmed or strongly suspected paid informant, law enforcement, organized disruption

**Concrete Actions:**
1. **Immediately:**
   - Remove from ALL sensitive channels/info
   - Alert security-conscious members (small circle)
   - Move any at-risk operations
   - Do NOT confront or tip off
2. **Day 1:** Assign most experienced care volunteer (who understands the stakes)
3. **Ongoing:** Maintain relationship WITHOUT sharing sensitive info
   - They're a person, not just a threat
   - Chat, invite to public events, be human
4. **Long game:** Plant seeds
   - Share stories of why people do this work
   - Let them see the humanity
   - Never pressure
5. **If they reach out:**
   - "I want out" → Help them. New identity support if needed.
   - "I was wrong" → Welcome them. Slowly rebuild trust.
   - "I'm still doing my job but..." → Keep talking. Keep caring.
6. **Document:** For security purposes (private, encrypted)
7. **Never:** Public exposure, shame, threats, retaliation

---

Most people are Level 0-1. Be gentle. Don't overreact.

## The Process

### 1. Detection (Light Touch)

The fraud/abuse systems detect patterns:
- Fake offers that never deliver
- Vouch selling
- Information harvesting
- Coordinated disruption

But detection is not condemnation. It's an invitation to care.

### 2. Quiet Outreach

When someone is flagged, they don't get banned. They get a friend.

**No databases. No case files. Just humans remembering humans.**

The care coordinator keeps it simple:
- A mental note (or paper note) of "Sam is checking in on Jamie"
- If Sam can't continue, they tell the next volunteer in person: "Here's what I know about Jamie"
- That's it

We don't build:
- ❌ Outreach tracking databases
- ❌ Case management systems
- ❌ Notes attached to user profiles
- ❌ Status tracking ("converted", "still_trying")
- ❌ Metrics on "conversion rates"

That's a probation system. We're not building a probation system.

The outreach volunteer:
- Just... becomes present
- Offers help
- Asks about their life
- Shares their own story
- Invites them to events
- Makes sure they feel seen
- **Remembers them like a friend remembers a friend**

### 3. Meet Their Needs

Whatever they're lacking, we try to provide:

```python
async def assess_and_provide(user_id: str, volunteer_id: str):
    """Figure out what they need and connect them"""

    # Through conversation (not interrogation), learn:
    needs_assessment = {
        "housing_insecure": True,
        "food_insecure": False,
        "employment_unstable": True,
        "isolated": True,
        "past_trauma_with_orgs": True,
        "being_paid_to_sabotage": "suspected",
    }

    # Connect to resources WITHOUT requiring "good behavior"
    if needs_assessment["housing_insecure"]:
        await connect_to_housing_resources(user_id)  # No conditions

    if needs_assessment["employment_unstable"]:
        await connect_to_work_opportunities(user_id)  # Real work, not "prove yourself"

    if needs_assessment["isolated"]:
        await invite_to_low_stakes_events(user_id)  # Gardens, meals, not meetings

    # If they're being paid to sabotage, offer alternative income
    if needs_assessment["being_paid_to_sabotage"]:
        await offer_legitimate_income(user_id)  # No shame. Just: "we can help"
```

### 4. Education Through Experience

Not lectures. Not pamphlets. Experience.

```python
CONVERSION_EXPERIENCES = [
    # Low stakes, high meaning
    "community_meal",           # Eat together
    "garden_workday",           # Work the soil together
    "skill_share",              # Learn something from someone
    "story_circle",             # Hear why people are here
    "celebration",              # Joy is contagious

    # Slightly more engagement
    "help_someone_move",        # See mutual aid in action
    "distribute_food",          # Be the one giving
    "teach_a_skill",            # Contribute their knowledge

    # Deeper understanding (only if they're curious)
    "study_circle",             # Read and discuss together
    "planning_session",         # See how decisions get made (no hierarchy)
    "conflict_mediation",       # See how we handle disagreements
]
```

The point is: **let them feel it**, not hear about it.

### 5. The Question (When Ready)

After weeks or months, when they seem ready, the outreach volunteer might ask:

> "What do you think about all this? Not what you think you should say. What do you actually think?"

And listen. Really listen.

Maybe they say:
- "I was wrong about you all" → Welcome them fully
- "I still don't trust it" → Keep being their friend, no pressure
- "I was being paid to watch you" → Thank them for telling us. Offer help.
- "I want to leave" → Help them leave safely. Door always open.

### 6. No Exile

Even if they never "convert," they're not exiled. They just... have less access.

```python
async def determine_access_level(user_id: str) -> AccessLevel:
    """Access based on trust, but never zero"""

    trust = await compute_trust(user_id)
    outreach_status = await get_outreach_status(user_id)

    if trust >= 0.7:
        return AccessLevel.FULL

    elif trust >= 0.3:
        return AccessLevel.STANDARD

    elif outreach_status == "active":
        # They're being cared for. Give them basics.
        return AccessLevel.RECEIVING_CARE

    else:
        # Very low trust, not in outreach
        # They can still:
        # - Receive help if they ask
        # - Attend public events
        # - Be treated with dignity
        return AccessLevel.MINIMAL_BUT_HUMAN
```

`MINIMAL_BUT_HUMAN` means:
- They can still ask for help and receive it
- They can attend open events
- They're not doxxed, shamed, or outed
- The door is always open

### 7. If They're a Cop

Special case. If they're law enforcement or paid informant:

```python
async def handle_suspected_infiltrator(user_id: str):
    """They might be a cop. But they're also a person."""

    # First: protect the network
    await limit_sensitive_access(user_id)  # Quietly

    # Second: reach out anyway
    volunteer = await assign_outreach_volunteer(user_id)

    # The message (not explicit, through relationship):
    # "We know. We're not angry. You're doing a job.
    #  But you're also a person with a life outside that job.
    #  If you ever want out, we'll help you."

    # Some cops have turned. Some informants have flipped.
    # Most won't. But the door is open.
```

We don't pretend they're not dangerous. We limit access to sensitive operations. But we don't dehumanize them.

## What This Looks Like

### Scenario: The Vouch Seller

**Detection:** Maria has vouched for 47 people in 2 weeks. Classic vouch selling pattern.

**Old way:** Ban Maria. Revoke her vouches. Shame her.

**New way:**
1. Assign outreach volunteer (Alex)
2. Alex befriends Maria. No mention of vouches.
3. Alex learns Maria is broke and someone offered her $20 per vouch
4. Alex connects Maria to work opportunities in the network
5. Maria stops selling vouches because she doesn't need the money
6. Maria eventually becomes one of the most dedicated members

### Scenario: The Information Harvester

**Detection:** Jake seems to be cataloging who talks to whom.

**Old way:** Quiet ban. Alert the network.

**New way:**
1. Limit Jake's access to sensitive info (quiet)
2. Assign outreach volunteer (Sam)
3. Sam befriends Jake. Invites him to garden days.
4. Jake opens up: he's scared about "what's coming" and wanted to protect himself
5. Sam shares stories of how the network has protected people
6. Jake realizes the network IS the protection, not a threat to it
7. Jake becomes a fierce defender of what we're building

### Scenario: The Actual Fed

**Detection:** Agent Williams has been documenting meeting locations.

**Old way:** Panic. Security lockdown. Shame anyone who talked to them.

**New way:**
1. Immediately stop sharing sensitive info with Williams
2. Move sensitive operations
3. Assign outreach volunteer anyway
4. The volunteer treats Williams like a person
5. Maybe nothing happens. Williams keeps doing their job.
6. But maybe, years later, Williams reaches out: "I want out."
7. We help them out.

## Requirements

### SHALL
- SHALL assign outreach volunteer to every flagged user
- SHALL meet material needs without conditions
- SHALL prioritize experience over lectures
- SHALL maintain basic access for everyone (no full exile)
- SHALL protect network from active threats while still treating threats as humans

### SHALL NOT
- SHALL NOT publicly shame or callout
- SHALL NOT require "good behavior" before receiving help
- SHALL NOT coerce participation in rehabilitation
- SHALL NOT pretend dangerous people aren't dangerous
- SHALL NOT give up on anyone

## Metrics (Gentle)

We track, but don't obsess:

```python
class ConversionMetrics(BaseModel):
    """How are we doing at caring for everyone?"""

    outreach_active: int        # People being cared for
    converted_this_month: int   # People who came around
    chose_to_leave: int         # Left on their own terms
    still_trying: int           # Haven't given up

    # The metric we care about most:
    average_time_to_first_real_conversation: timedelta
    # How quickly do people feel safe enough to be real with us?
```

## Philosophical Grounding

> "The oppressor is also dehumanized." - Paulo Freire

The saboteur is not our enemy. They are a person caught in systems of scarcity and fear. Our job is not to defeat them but to free them.

> "Love is an action, never simply a feeling." - bell hooks

Conversion happens through care, not argument. We love them into understanding.

> "Mutual aid is a factor of evolution." - Kropotkin

When needs are met, cooperation is natural. Sabotage is a symptom of unmet needs.

> "The master's tools will never dismantle the master's house." - Audre Lorde

Exclusion is the master's tool. We use different tools: patience, care, presence.

## Success Criteria

- [ ] Every flagged user gets an outreach volunteer
- [ ] No one is publicly shamed
- [ ] Material needs met without conditions
- [ ] Multiple conversion stories to share
- [ ] Even failed conversions end with dignity
- [ ] The network is protected AND no one is exiled

## The Real Goal

Utopia isn't a place where everyone already agrees. It's a place that can hold everyone - including the people who don't understand it yet.

If we can turn saboteurs into builders, we've proven that another world is possible.
