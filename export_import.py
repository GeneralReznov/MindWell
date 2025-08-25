import json
import csv
from datetime import datetime
from io import StringIO
from flask import Response
from typing import Dict, List, Any
from models import MoodEntry, JournalEntry, Habit, HabitLog
from app import db

def export_user_data(format: str = 'json') -> Response:
    """Export all user data in specified format."""
    
    # Get all user data
    mood_entries = MoodEntry.query.order_by(MoodEntry.timestamp).all()
    journal_entries = JournalEntry.query.order_by(JournalEntry.timestamp).all()  
    habits = Habit.query.all()
    habit_logs = HabitLog.query.order_by(HabitLog.timestamp).all()
    
    data = {
        'export_date': datetime.utcnow().isoformat(),
        'mood_entries': [
            {
                'id': entry.id,
                'timestamp': entry.timestamp.isoformat(),
                'mood_type': entry.mood_type,
                'intensity': entry.intensity,
                'notes': entry.notes
            }
            for entry in mood_entries
        ],
        'journal_entries': [
            {
                'id': entry.id,
                'timestamp': entry.timestamp.isoformat(),
                'title': entry.title,
                'content': entry.content,
                'mood_context': entry.mood_context
            }
            for entry in journal_entries
        ],
        'habits': [
            {
                'id': habit.id,
                'name': habit.name,
                'description': habit.description,
                'created_at': habit.created_at.isoformat(),
                'is_active': habit.is_active
            }
            for habit in habits
        ],
        'habit_logs': [
            {
                'id': log.id,
                'habit_id': log.habit_id,
                'timestamp': log.timestamp.isoformat(),
                'completed': log.completed,
                'notes': log.notes
            }
            for log in habit_logs
        ]
    }
    
    if format.lower() == 'json':
        return Response(
            json.dumps(data, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=mindful_data_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            }
        )
    
    elif format.lower() == 'csv':
        # Create CSV with multiple sheets (combined file)
        output = StringIO()
        
        # Mood entries CSV
        output.write("=== MOOD ENTRIES ===\\n")
        output.write("timestamp,mood_type,intensity,notes\\n")
        for entry in mood_entries:
            output.write(f'"{entry.timestamp.isoformat()}","{entry.mood_type}",{entry.intensity},"{entry.notes or ""}"\\n')
        
        output.write("\\n=== JOURNAL ENTRIES ===\\n") 
        output.write("timestamp,title,content,mood_context\\n")
        for entry in journal_entries:
            # Clean content for CSV
            content = entry.content.replace('"', '""').replace('\\n', ' ') if entry.content else ""
            title = entry.title.replace('"', '""') if entry.title else ""
            output.write(f'"{entry.timestamp.isoformat()}","{title}","{content}","{entry.mood_context or ""}"\\n')
        
        output.write("\\n=== HABITS ===\\n")
        output.write("name,description,created_at,is_active\\n")
        for habit in habits:
            desc = habit.description.replace('"', '""') if habit.description else ""
            output.write(f'"{habit.name}","{desc}","{habit.created_at.isoformat()}",{habit.is_active}\\n')
        
        output.write("\\n=== HABIT LOGS ===\\n")
        output.write("habit_id,timestamp,completed,notes\\n")
        for log in habit_logs:
            notes = log.notes.replace('"', '""') if log.notes else ""
            output.write(f'{log.habit_id},"{log.timestamp.isoformat()}",{log.completed},"{notes}"\\n')
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=mindful_data_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
    
    else:
        raise ValueError(f"Unsupported format: {format}")

def import_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Import user data from exported format."""
    
    results = {
        'imported': {
            'mood_entries': 0,
            'journal_entries': 0, 
            'habits': 0,
            'habit_logs': 0
        },
        'errors': []
    }
    
    try:
        # Import mood entries
        if 'mood_entries' in data:
            for entry_data in data['mood_entries']:
                try:
                    # Check if already exists (by timestamp and mood)
                    existing = MoodEntry.query.filter(
                        MoodEntry.timestamp == datetime.fromisoformat(entry_data['timestamp']),
                        MoodEntry.mood_type == entry_data['mood_type']
                    ).first()
                    
                    if not existing:
                        mood_entry = MoodEntry()
                        mood_entry.timestamp = datetime.fromisoformat(entry_data['timestamp'])
                        mood_entry.mood_type = entry_data['mood_type']
                        mood_entry.intensity = entry_data['intensity']
                        mood_entry.notes = entry_data.get('notes')
                        
                        db.session.add(mood_entry)
                        results['imported']['mood_entries'] += 1
                        
                except Exception as e:
                    results['errors'].append(f"Error importing mood entry: {str(e)}")
        
        # Import journal entries
        if 'journal_entries' in data:
            for entry_data in data['journal_entries']:
                try:
                    # Check if already exists (by timestamp and title)
                    existing = JournalEntry.query.filter(
                        JournalEntry.timestamp == datetime.fromisoformat(entry_data['timestamp']),
                        JournalEntry.title == entry_data.get('title', '')
                    ).first()
                    
                    if not existing:
                        journal_entry = JournalEntry()
                        journal_entry.timestamp = datetime.fromisoformat(entry_data['timestamp'])
                        journal_entry.title = entry_data.get('title')
                        journal_entry.content = entry_data['content']
                        journal_entry.mood_context = entry_data.get('mood_context')
                        
                        db.session.add(journal_entry)
                        results['imported']['journal_entries'] += 1
                        
                except Exception as e:
                    results['errors'].append(f"Error importing journal entry: {str(e)}")
        
        # Import habits
        if 'habits' in data:
            for habit_data in data['habits']:
                try:
                    # Check if already exists (by name)
                    existing = Habit.query.filter(Habit.name == habit_data['name']).first()
                    
                    if not existing:
                        habit = Habit()
                        habit.name = habit_data['name']
                        habit.description = habit_data.get('description')
                        habit.created_at = datetime.fromisoformat(habit_data['created_at'])
                        habit.is_active = habit_data.get('is_active', True)
                        
                        db.session.add(habit)
                        db.session.flush()  # To get the ID
                        results['imported']['habits'] += 1
                        
                except Exception as e:
                    results['errors'].append(f"Error importing habit: {str(e)}")
        
        # Commit habit changes first so we have IDs for habit logs
        db.session.commit()
        
        # Import habit logs
        if 'habit_logs' in data:
            for log_data in data['habit_logs']:
                try:
                    # Find the habit by the original ID mapping or name
                    habit = Habit.query.filter(Habit.id == log_data['habit_id']).first()
                    
                    if habit:
                        # Check if already exists
                        existing = HabitLog.query.filter(
                            HabitLog.habit_id == habit.id,
                            HabitLog.timestamp == datetime.fromisoformat(log_data['timestamp'])
                        ).first()
                        
                        if not existing:
                            habit_log = HabitLog()
                            habit_log.habit_id = habit.id
                            habit_log.timestamp = datetime.fromisoformat(log_data['timestamp'])
                            habit_log.completed = log_data['completed']
                            habit_log.notes = log_data.get('notes')
                            
                            db.session.add(habit_log)
                            results['imported']['habit_logs'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Error importing habit log: {str(e)}")
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        results['errors'].append(f"General import error: {str(e)}")
    
    return results

def get_backup_summary() -> Dict[str, Any]:
    """Get a summary of current data for backup purposes."""
    
    mood_count = MoodEntry.query.count()
    journal_count = JournalEntry.query.count()
    habit_count = Habit.query.filter_by(is_active=True).count()
    habit_log_count = HabitLog.query.count()
    
    # Get date range
    first_mood = MoodEntry.query.order_by(MoodEntry.timestamp.asc()).first()
    last_mood = MoodEntry.query.order_by(MoodEntry.timestamp.desc()).first()
    
    first_journal = JournalEntry.query.order_by(JournalEntry.timestamp.asc()).first()
    last_journal = JournalEntry.query.order_by(JournalEntry.timestamp.desc()).first()
    
    date_range = {}
    if first_mood and last_mood:
        date_range['mood_entries'] = {
            'first': first_mood.timestamp.isoformat(),
            'last': last_mood.timestamp.isoformat()
        }
    
    if first_journal and last_journal:
        date_range['journal_entries'] = {
            'first': first_journal.timestamp.isoformat(),
            'last': last_journal.timestamp.isoformat()
        }
    
    return {
        'summary': {
            'mood_entries': mood_count,
            'journal_entries': journal_count,
            'active_habits': habit_count,
            'habit_logs': habit_log_count
        },
        'date_ranges': date_range,
        'last_updated': datetime.utcnow().isoformat()
    }