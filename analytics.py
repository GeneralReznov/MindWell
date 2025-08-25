import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from collections import Counter, defaultdict
from sqlalchemy import func
from models import MoodEntry, JournalEntry, HabitLog, Habit
from app import db

def get_mood_analytics(days: int = 30) -> Dict[str, Any]:
    """Get comprehensive mood analytics for the specified period."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get mood entries within the period
    mood_entries = MoodEntry.query.filter(
        MoodEntry.timestamp >= start_date,
        MoodEntry.timestamp <= end_date
    ).all()
    
    if not mood_entries:
        return {}
    
    # Basic statistics
    total_entries = len(mood_entries)
    moods = [entry.mood_type for entry in mood_entries]
    intensities = [entry.intensity for entry in mood_entries]
    
    # Mood distribution
    mood_distribution = dict(Counter(moods))
    
    # Average intensity by mood
    mood_intensity = defaultdict(list)
    for entry in mood_entries:
        mood_intensity[entry.mood_type].append(entry.intensity)
    
    avg_intensity_by_mood = {
        mood: sum(intensities) / len(intensities) 
        for mood, intensities in mood_intensity.items()
    }
    
    # Daily mood pattern
    daily_patterns = defaultdict(list)
    for entry in mood_entries:
        hour = entry.timestamp.hour
        daily_patterns[entry.mood_type].append(hour)
    
    # Weekly pattern
    weekly_patterns = defaultdict(list)
    for entry in mood_entries:
        weekday = entry.timestamp.weekday()  # 0=Monday, 6=Sunday
        weekly_patterns[entry.mood_type].append(weekday)
    
    # Mood streaks
    mood_streaks = calculate_mood_streaks(mood_entries)
    
    # Mood stability (variance in intensity)
    intensity_variance = sum((i - sum(intensities)/len(intensities))**2 for i in intensities) / len(intensities)
    
    return {
        'total_entries': total_entries,
        'period_days': days,
        'mood_distribution': mood_distribution,
        'average_intensity': sum(intensities) / len(intensities),
        'avg_intensity_by_mood': avg_intensity_by_mood,
        'most_common_mood': max(mood_distribution, key=mood_distribution.get) if mood_distribution else None,
        'mood_stability': intensity_variance,
        'mood_streaks': mood_streaks,
        'daily_patterns': dict(daily_patterns),
        'weekly_patterns': dict(weekly_patterns)
    }

def calculate_mood_streaks(mood_entries: List[MoodEntry]) -> Dict[str, int]:
    """Calculate the longest streak for each mood type."""
    if not mood_entries:
        return {}
    
    # Sort by timestamp
    sorted_entries = sorted(mood_entries, key=lambda x: x.timestamp)
    
    streaks = {}
    current_streaks = {}
    
    for entry in sorted_entries:
        mood = entry.mood_type
        
        # Initialize if first occurrence
        if mood not in current_streaks:
            current_streaks[mood] = 1
            streaks[mood] = 1
        else:
            current_streaks[mood] += 1
            streaks[mood] = max(streaks[mood], current_streaks[mood])
        
        # Reset other mood streaks
        for other_mood in current_streaks:
            if other_mood != mood:
                current_streaks[other_mood] = 0
    
    return streaks

def get_habit_analytics(days: int = 30) -> Dict[str, Any]:
    """Get comprehensive habit analytics."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get habit completion data
    habit_logs = db.session.query(
        HabitLog, Habit.name.label('habit_name')
    ).join(Habit).filter(
        HabitLog.timestamp >= start_date,
        HabitLog.timestamp <= end_date
    ).all()
    
    if not habit_logs:
        return {}
    
    # Calculate completion rates
    habit_stats = defaultdict(lambda: {'completed': 0, 'total': 0, 'completion_rate': 0.0})
    
    for log, habit_name in habit_logs:
        habit_stats[habit_name]['total'] += 1
        if log.completed:
            habit_stats[habit_name]['completed'] += 1
    
    # Calculate completion rates
    for habit_name in habit_stats:
        stats = habit_stats[habit_name]
        if stats['total'] > 0:
            stats['completion_rate'] = stats['completed'] / stats['total']
    
    # Overall completion rate
    total_attempts = sum(stats['total'] for stats in habit_stats.values())
    total_completed = sum(stats['completed'] for stats in habit_stats.values())
    overall_rate = total_completed / total_attempts if total_attempts > 0 else 0
    
    # Best performing habits
    best_habits = sorted(
        habit_stats.items(), 
        key=lambda x: x[1]['completion_rate'], 
        reverse=True
    )[:5]
    
    return {
        'total_attempts': total_attempts,
        'total_completed': total_completed,
        'overall_completion_rate': overall_rate,
        'habit_stats': dict(habit_stats),
        'best_habits': best_habits,
        'period_days': days
    }

def get_journal_analytics(days: int = 30) -> Dict[str, Any]:
    """Get journal writing analytics."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    journal_entries = JournalEntry.query.filter(
        JournalEntry.timestamp >= start_date,
        JournalEntry.timestamp <= end_date
    ).all()
    
    if not journal_entries:
        return {}
    
    # Basic stats
    total_entries = len(journal_entries)
    total_words = sum(len(entry.content.split()) for entry in journal_entries)
    avg_words = total_words / total_entries if total_entries > 0 else 0
    
    # Entries by mood context
    mood_context_distribution = Counter(
        entry.mood_context for entry in journal_entries if entry.mood_context
    )
    
    # Writing frequency pattern
    daily_entries = defaultdict(int)
    for entry in journal_entries:
        date_key = entry.timestamp.strftime('%Y-%m-%d')
        daily_entries[date_key] += 1
    
    # Most productive writing days
    most_productive_day = max(daily_entries.values()) if daily_entries else 0
    
    return {
        'total_entries': total_entries,
        'total_words': total_words,
        'average_words_per_entry': avg_words,
        'mood_context_distribution': dict(mood_context_distribution),
        'daily_entries': dict(daily_entries),
        'most_entries_in_day': most_productive_day,
        'period_days': days
    }

def generate_wellness_score(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an overall wellness score based on user data."""
    score_components = {}
    
    # Mood stability component (0-25 points)
    if 'mood_analytics' in user_data and user_data['mood_analytics']:
        mood_data = user_data['mood_analytics']
        
        # Lower variance = better stability
        stability = max(0, 25 - (mood_data.get('mood_stability', 5) * 2))
        score_components['mood_stability'] = min(25, stability)
        
        # Consistency bonus for regular check-ins
        entries_bonus = min(10, mood_data.get('total_entries', 0) / 2)
        score_components['check_in_consistency'] = entries_bonus
    else:
        score_components['mood_stability'] = 0
        score_components['check_in_consistency'] = 0
    
    # Habit completion component (0-25 points)
    if 'habit_analytics' in user_data and user_data['habit_analytics']:
        habit_data = user_data['habit_analytics']
        completion_score = habit_data.get('overall_completion_rate', 0) * 25
        score_components['habit_completion'] = completion_score
    else:
        score_components['habit_completion'] = 0
    
    # Journal engagement component (0-25 points)
    if 'journal_analytics' in user_data and user_data['journal_analytics']:
        journal_data = user_data['journal_analytics']
        entry_score = min(15, journal_data.get('total_entries', 0) * 2)
        word_score = min(10, journal_data.get('average_words_per_entry', 0) / 20)
        score_components['journal_engagement'] = entry_score + word_score
    else:
        score_components['journal_engagement'] = 0
    
    # Self-awareness component (0-15 points)
    total_interactions = (
        score_components['check_in_consistency'] + 
        score_components['journal_engagement'] / 2
    )
    score_components['self_awareness'] = min(15, total_interactions)
    
    # Calculate total score
    total_score = sum(score_components.values())
    
    # Determine wellness level
    if total_score >= 80:
        level = "Thriving"
        message = "You're doing amazingly well! Your consistent self-care is paying off."
    elif total_score >= 60:
        level = "Growing"  
        message = "You're making great progress on your wellness journey!"
    elif total_score >= 40:
        level = "Building"
        message = "You're building healthy habits. Keep up the good work!"
    elif total_score >= 20:
        level = "Starting"
        message = "Every journey begins with a single step. You're on your way!"
    else:
        level = "Beginning"
        message = "Welcome to your wellness journey. Small steps lead to big changes."
    
    return {
        'total_score': total_score,
        'max_score': 100,
        'level': level,
        'message': message,
        'components': score_components,
        'percentage': (total_score / 100) * 100
    }