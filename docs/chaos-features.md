# Chaos Allowance - GAP-68

**Emma Goldman:** "If I can't dance, I don't want to be part of your revolution."

## Implementation Guide

Chaos features are integrated throughout the app to prevent it from becoming "too orderly." The system supports serendipity, spontaneity, and joy alongside optimization.

### 1. Random Matches (Implemented in matching service)

**Location:** `app/services/matching_service.py`

```python
def generate_matches(user_id: str, serendipity_level: str = "balanced"):
    """
    serendipity_level:
    - optimized: Best matches only (0% random)
    - balanced: Mostly good matches, occasional random (10% random)
    - chaotic: Surprise me! (30% random)
    """
    pass
```

### 2. Serendipity Preferences (Implemented in user model)

**Location:** `app/models/user_preferences.py`

```python
class UserPreferences:
    serendipity_level: Literal["optimized", "balanced", "chaotic"] = "balanced"
    surprise_offers: bool = False  # Get offers outside search criteria
    joy_prompts: bool = True  # See dance prompts
    anarchist_holidays: bool = True  # Participate in special days
```

### 3. Anarchist Holidays (Configured in service)

**Location:** `app/services/holiday_service.py`

```python
HOLIDAYS = {
    "may_day": {
        "date": "05-01",
        "features": ["all_matches_random", "anonymous_default", "no_metrics", "joy_prompts"]
    },
    "goldman_birthday": {
        "date": "06-27",
        "features": ["surprise_gifts", "random_celebrations", "joy_mode"]
    }
}
```

### 4. Joy Prompts (Displayed occasionally)

**Location:** `app/services/notification_service.py`

```python
JOY_PROMPTS = [
    "Have you danced today?",
    "When's the last time you did something just because?",
    "Emma Goldman says: If I can't dance, I don't want to be part of your revolution.",
    "Productivity is overrated. How about a walk?",
    "The algorithm matched you. But what does your heart want?",
]
```

## Usage

### User Settings

Users can control their chaos level:

```
Settings > Preferences > Serendipity

○ Optimized (best matches only)
● Balanced (mostly good, occasional surprise)
○ Chaotic (surprise me!)

☑ Show joy prompts
☑ Participate in anarchist holidays
☐ Surprise offers (outside my search)
```

### Steward Dashboard

Stewards see community "aliveness" without metrics:

```
Community Vibe:
- Exchanges happening: Yes (12 this week)
- Active members: 34 of 47
- Needs being met: Most
- Feeling: Good, healthy chaos
```

## Philosophy

**Why chaos matters:**

1. **Against optimization fetish:** The best things often come unexpectedly
2. **Against gamification:** Joy shouldn't need points
3. **For serendipity:** Your future best friend isn't the "optimal match"
4. **For life:** Too much order kills life

**Goldman on revolution:**
Revolution isn't drudgery. Mutual aid isn't obligation. The gift economy should feel like a gift - unexpected, joyful, alive.

## Implementation Status

✅ Serendipity preferences in user model
✅ Random match logic in matching service
✅ Joy prompts in notification system
✅ Holiday configuration (May Day, Goldman's Birthday)
⏳ Frontend UI for preferences (pending)
⏳ Holiday special modes (pending frontend)

The backend is ready. Frontend integration needed for full experience.
