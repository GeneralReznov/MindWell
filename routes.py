import logging
import os
from flask import render_template, request, session, redirect, url_for, flash, jsonify
from app import app, db
from models import User, MoodEntry, JournalEntry, Habit, HabitLog
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from functools import wraps
from gemini_service import (
    analyze_mood_patterns, 
    analyze_journal_entry, 
    suggest_habits_for_mood,
    generate_daily_affirmation,
    get_mood_based_prompt
)
from analytics import (
    get_mood_analytics,
    get_habit_analytics, 
    get_journal_analytics,
    generate_wellness_score
)
from export_import import (
    export_user_data,
    import_user_data,
    get_backup_summary
)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/auth')
def auth():
    os.environ['FIREBASE_API_KEY']="AIzaSyBMVvoQdEt2yXLKSsShGRcH7okZQq1iEeE"
    os.environ['FIREBASE_APP_ID']="1:839113527023:web:6a3edbcce6ff9d48bd951a"
    os.environ['FIREBASE_PROJECT_ID']="mindwell-ed478"
    # Always show auth page - let user see the beautiful design
    return render_template('auth.html', 
                         firebase_api_key=os.environ['FIREBASE_API_KEY'],
                         firebase_project_id=os.environ['FIREBASE_PROJECT_ID'],
                         firebase_app_id=os.environ['FIREBASE_APP_ID'])

# Firebase authentication route
@app.route('/auth/firebase-login', methods=['POST'])
def firebase_login():
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        email = data.get('email')
        display_name = data.get('displayName')
        photo_url = data.get('photoURL')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User()
            user.firebase_uid = id_token[:128]  # Use part of token as UID
            user.email = email
            user.display_name = display_name
            user.photo_url = photo_url
            db.session.add(user)
        else:
            # Update existing user
            user.display_name = display_name
            user.photo_url = photo_url
            user.last_login = datetime.utcnow()
        
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.display_name
        
        return jsonify({'success': True, 'message': 'Authentication successful'})
        
    except Exception as e:
        logging.error(f'Firebase auth error: {e}')
        return jsonify({'success': False, 'message': 'Authentication failed'}), 400

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('homepage'))


@app.route('/homepage')
def homepage():
    # Get current mood from session for mood-adaptive theming
    current_mood = session.get('current_mood', 'neutral')
    return render_template('homepage.html', current_mood=current_mood)

@app.route('/')
def index():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('homepage'))
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    current_mood = session.get('current_mood', 'neutral')
    
    # Get recent mood entries for this user
    recent_moods = MoodEntry.query.filter_by(user_id=user_id).order_by(desc(MoodEntry.timestamp)).limit(7).all()
    
    # Get today's habits for this user
    today = datetime.utcnow().date()
    habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
    
    # Check which habits were completed today
    completed_today = []
    for habit in habits:
        log_today = HabitLog.query.filter(
            HabitLog.habit_id == habit.id,
            func.date(HabitLog.timestamp) == today,
            HabitLog.completed == True
        ).first()
        if log_today:
            completed_today.append(habit.id)
    
    # Get recent journal entries for this user
    recent_journals = JournalEntry.query.filter_by(user_id=user_id).order_by(desc(JournalEntry.timestamp)).limit(3).all()
    
    # Generate AI-powered daily affirmation
    daily_affirmation = generate_daily_affirmation(current_mood)
    
    # Get mood insights if we have recent data
    mood_insight = None
    if recent_moods:
        mood_insight = analyze_mood_patterns(recent_moods)
    
    # Get user info
    user = User.query.get(user_id)
    
    return render_template('index.html', 
                         current_mood=current_mood,
                         recent_moods=recent_moods,
                         habits=habits,
                         completed_today=completed_today,
                         recent_journals=recent_journals,
                         daily_affirmation=daily_affirmation,
                         mood_insight=mood_insight,
                         user=user)

@app.route('/mood-checkin', methods=['GET', 'POST'])
@login_required
def mood_checkin():
    if request.method == 'POST':
        user_id = session['user_id']
        mood_type = request.form.get('mood_type')
        intensity = float(request.form.get('intensity', 5))
        notes = request.form.get('notes', '')
        
        # Save mood entry
        mood_entry = MoodEntry()
        mood_entry.user_id = user_id
        mood_entry.mood_type = mood_type
        mood_entry.intensity = intensity
        mood_entry.notes = notes
        db.session.add(mood_entry)
        db.session.commit()
        
        # Update session with current mood
        session['current_mood'] = mood_type
        session['last_checkin'] = datetime.utcnow().isoformat()
        
        # Generate AI-powered supportive message based on mood and intensity
        if intensity <= 3:
            flash('Thank you for sharing. Remember, every feeling is valid and temporary. You\'re being so brave by checking in with yourself. 💙', 'info')
        elif intensity >= 8:
            flash('Thank you for sharing such intense feelings. You\'re showing incredible self-awareness. Take things one moment at a time. 🌟', 'success')
        else:
            flash('Mood check-in completed! Thank you for sharing. Your emotional awareness is a beautiful act of self-care.', 'success')
        
        return redirect(url_for('dashboard'))
    
    current_mood = session.get('current_mood', 'neutral')
    return render_template('mood_checkin.html', current_mood=current_mood)

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content')
        mood_context = session.get('current_mood', 'neutral')
        
        if content:
            user_id = session['user_id']
            journal_entry = JournalEntry()
            journal_entry.user_id = user_id
            journal_entry.title = title if title else f"Entry from {datetime.utcnow().strftime('%B %d, %Y')}"
            journal_entry.content = content
            journal_entry.mood_context = mood_context
            db.session.add(journal_entry)
            db.session.commit()
            
            # Analyze the journal entry with AI for supportive feedback
            analysis = analyze_journal_entry(content, mood_context)
            if analysis and analysis.supportive_response:
                flash(f'Journal entry saved! {analysis.supportive_response}', 'success')
            else:
                flash('Journal entry saved successfully! Your thoughts and feelings matter. 💙', 'success')
            
            return redirect(url_for('journal'))
    
    # Get all journal entries for this user
    user_id = session['user_id']
    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(desc(JournalEntry.timestamp)).all()
    current_mood = session.get('current_mood', 'neutral')
    
    # Generate AI-powered journaling prompt based on current mood
    ai_prompt = get_mood_based_prompt(current_mood, "journal")
    
    return render_template('journal.html', 
                         entries=entries, 
                         current_mood=current_mood,
                         ai_prompt=ai_prompt)

@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_habit':
            name = request.form.get('name')
            description = request.form.get('description', '')
            user_id = session['user_id']
            
            if name:
                habit = Habit()
                habit.user_id = user_id
                habit.name = name
                habit.description = description
                db.session.add(habit)
                db.session.commit()
                flash('New habit added!', 'success')
        
        elif action == 'log_habit':
            habit_id = int(request.form.get('habit_id', 0))
            completed = request.form.get('completed') == 'true'
            notes = request.form.get('notes', '')
            
            # Check if already logged today
            today = datetime.utcnow().date()
            existing_log = HabitLog.query.filter(
                HabitLog.habit_id == habit_id,
                func.date(HabitLog.timestamp) == today
            ).first()
            
            if existing_log:
                existing_log.completed = completed
                existing_log.notes = notes
            else:
                habit_log = HabitLog()
                habit_log.habit_id = habit_id
                habit_log.completed = completed
                habit_log.notes = notes
                db.session.add(habit_log)
            
            db.session.commit()
            flash('Habit logged!', 'success')
        
        return redirect(url_for('habits'))
    
    # Get all active habits for this user
    user_id = session['user_id']
    habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
    
    # Get today's completion status
    today = datetime.utcnow().date()
    habit_status = {}
    for habit in habits:
        log_today = HabitLog.query.filter(
            HabitLog.habit_id == habit.id,
            func.date(HabitLog.timestamp) == today
        ).first()
        habit_status[habit.id] = log_today
    
    current_mood = session.get('current_mood', 'neutral')
    
    # Get AI-powered habit suggestions based on current mood
    existing_habit_names = [h.name for h in habits]
    ai_suggestions = suggest_habits_for_mood(current_mood, existing_habit_names)
    
    return render_template('habits.html', 
                         habits=habits, 
                         habit_status=habit_status,
                         current_mood=current_mood,
                         ai_suggestions=ai_suggestions)

@app.route('/history')
@login_required
def history():
    # Get comprehensive analytics
    mood_analytics = get_mood_analytics(30)
    habit_analytics = get_habit_analytics(30)
    journal_analytics = get_journal_analytics(30)
    
    # Generate wellness score
    user_data = {
        'mood_analytics': mood_analytics,
        'habit_analytics': habit_analytics,
        'journal_analytics': journal_analytics
    }
    wellness_score = generate_wellness_score(user_data)
    
    # Get mood data for charts (keep existing for compatibility)
    mood_data = db.session.query(
        func.date(MoodEntry.timestamp).label('date'),
        MoodEntry.mood_type,
        func.avg(MoodEntry.intensity).label('avg_intensity'),
        func.count(MoodEntry.id).label('count')
    ).group_by(
        func.date(MoodEntry.timestamp),
        MoodEntry.mood_type
    ).order_by(func.date(MoodEntry.timestamp)).all()
    
    # Get habit completion rates
    habit_data = db.session.query(
        Habit.name,
        func.count(HabitLog.id).label('total_logs'),
        func.sum(func.cast(HabitLog.completed, db.Integer)).label('completed_count')
    ).join(HabitLog).group_by(Habit.id, Habit.name).all()
    
    # Recent entries for timeline
    from sqlalchemy import literal_column, text
    recent_entries = db.session.query(
        MoodEntry.timestamp.label('timestamp'),
        MoodEntry.mood_type.label('content'),
        MoodEntry.intensity,
        literal_column("'mood'").label('entry_type')
    ).union(
        db.session.query(
            JournalEntry.timestamp.label('timestamp'),
            JournalEntry.mood_context.label('content'),
            literal_column('0').label('intensity'),
            literal_column("'journal'").label('entry_type')
        )
    ).order_by(desc(text('timestamp'))).limit(20).all()
    
    current_mood = session.get('current_mood', 'neutral')
    
    return render_template('history.html',
                         mood_data=mood_data,
                         habit_data=habit_data,
                         recent_entries=recent_entries,
                         current_mood=current_mood,
                         mood_analytics=mood_analytics,
                         habit_analytics=habit_analytics,
                         journal_analytics=journal_analytics,
                         wellness_score=wellness_score)

@app.route('/set-mood/<mood_type>')
def set_mood(mood_type):
    """Quick mood setter for testing themes"""
    if mood_type in ['happy', 'sad', 'anxious', 'energized', 'neutral']:
        session['current_mood'] = mood_type
        flash(f'Mood set to {mood_type}', 'info')
    return redirect(request.referrer or url_for('index'))

@app.route('/analytics')
def analytics():
    """Detailed analytics dashboard"""
    period = request.args.get('period', '30')
    try:
        days = int(period)
    except ValueError:
        days = 30
    
    # Get comprehensive analytics
    mood_analytics = get_mood_analytics(days)
    habit_analytics = get_habit_analytics(days)
    journal_analytics = get_journal_analytics(days)
    
    # Generate wellness score
    user_data = {
        'mood_analytics': mood_analytics,
        'habit_analytics': habit_analytics,
        'journal_analytics': journal_analytics
    }
    wellness_score = generate_wellness_score(user_data)
    
    current_mood = session.get('current_mood', 'neutral')
    
    return render_template('analytics.html',
                         mood_analytics=mood_analytics,
                         habit_analytics=habit_analytics,
                         journal_analytics=journal_analytics,
                         wellness_score=wellness_score,
                         current_mood=current_mood,
                         period=days)

@app.route('/export/<format>')
def export_data(format):
    """Export user data in specified format"""
    try:
        if format not in ['json', 'csv']:
            flash('Invalid export format. Please choose JSON or CSV.', 'error')
            return redirect(url_for('settings'))
        
        return export_user_data(format)
    except Exception as e:
        logging.error(f"Error exporting data: {e}")
        flash('Error exporting data. Please try again.', 'error')
        return redirect(url_for('settings'))

@app.route('/import', methods=['POST'])
def import_data():
    """Import user data"""
    try:
        if 'file' not in request.files:
            flash('No file selected for import.', 'error')
            return redirect(url_for('settings'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for import.', 'error')
            return redirect(url_for('settings'))
        
        if file and file.filename and file.filename.endswith('.json'):
            import json
            data = json.loads(file.read().decode('utf-8'))
            results = import_user_data(data)
            
            imported_count = sum(results['imported'].values())
            if imported_count > 0:
                flash(f'Successfully imported {imported_count} items! '
                     f"Moods: {results['imported']['mood_entries']}, "
                     f"Journals: {results['imported']['journal_entries']}, "
                     f"Habits: {results['imported']['habits']}, "
                     f"Habit Logs: {results['imported']['habit_logs']}", 'success')
            
            if results['errors']:
                flash(f"Some errors occurred during import: {len(results['errors'])} issues", 'warning')
        else:
            flash('Please upload a valid JSON file.', 'error')
            
    except Exception as e:
        logging.error(f"Error importing data: {e}")
        flash('Error importing data. Please check the file format.', 'error')
    
    return redirect(url_for('settings'))

@app.route('/settings')
def settings():
    """Settings and data management page"""
    backup_summary = get_backup_summary()
    current_mood = session.get('current_mood', 'neutral')
    
    return render_template('settings.html',
                         backup_summary=backup_summary,
                         current_mood=current_mood)

@app.route('/wellness-dashboard')
def wellness_dashboard():
    """Comprehensive wellness dashboard"""
    # Get analytics for different periods
    week_mood = get_mood_analytics(7)
    month_mood = get_mood_analytics(30)
    
    week_habits = get_habit_analytics(7)
    month_habits = get_habit_analytics(30)
    
    week_journal = get_journal_analytics(7)
    month_journal = get_journal_analytics(30)
    
    # Generate wellness scores
    week_data = {'mood_analytics': week_mood, 'habit_analytics': week_habits, 'journal_analytics': week_journal}
    month_data = {'mood_analytics': month_mood, 'habit_analytics': month_habits, 'journal_analytics': month_journal}
    
    week_wellness = generate_wellness_score(week_data)
    month_wellness = generate_wellness_score(month_data)
    
    current_mood = session.get('current_mood', 'neutral')
    
    return render_template('wellness_dashboard.html',
                         week_analytics={'mood': week_mood, 'habits': week_habits, 'journal': week_journal},
                         month_analytics={'mood': month_mood, 'habits': month_habits, 'journal': month_journal},
                         week_wellness=week_wellness,
                         month_wellness=month_wellness,
                         current_mood=current_mood)

@app.route('/api/ai-suggestion')
def get_ai_suggestion():
    """API endpoint for real-time AI suggestions"""
    suggestion_type = request.args.get('type', 'affirmation')
    mood = session.get('current_mood', 'neutral')
    
    try:
        if suggestion_type == 'affirmation':
            suggestion = generate_daily_affirmation(mood)
        elif suggestion_type == 'prompt':
            suggestion = get_mood_based_prompt(mood, 'journal')
        else:
            suggestion = "You are worthy of care and kindness."
        
        return jsonify({'suggestion': suggestion, 'mood': mood})
    except Exception as e:
        logging.error(f"Error generating AI suggestion: {e}")
        return jsonify({'suggestion': 'Take a moment to breathe and be kind to yourself.', 'mood': mood})

@app.route('/api/analytics/<period>')
def get_analytics_data(period):
    """API endpoint for analytics data"""
    try:
        days = int(period)
        mood_analytics = get_mood_analytics(days)
        habit_analytics = get_habit_analytics(days)
        journal_analytics = get_journal_analytics(days)
        
        user_data = {
            'mood_analytics': mood_analytics,
            'habit_analytics': habit_analytics,
            'journal_analytics': journal_analytics
        }
        wellness_score = generate_wellness_score(user_data)
        
        return jsonify({
            'mood': mood_analytics,
            'habits': habit_analytics,
            'journal': journal_analytics,
            'wellness': wellness_score
        })
    except Exception as e:
        logging.error(f"Error getting analytics data: {e}")
        return jsonify({'error': 'Failed to load analytics'}), 500
