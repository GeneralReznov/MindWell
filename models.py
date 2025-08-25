from app import db
from datetime import datetime
from sqlalchemy import DateTime, String, Text, Integer, Float, Boolean

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(String(128), unique=True, nullable=False)
    email = db.Column(String(120), unique=True, nullable=False)
    display_name = db.Column(String(100))
    photo_url = db.Column(String(500))
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(DateTime)
    is_active = db.Column(Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    mood_type = db.Column(String(50), nullable=False)  # happy, sad, anxious, energized
    intensity = db.Column(Float, nullable=False)  # 1-10 scale
    notes = db.Column(Text)
    
    user = db.relationship('User', backref=db.backref('mood_entries', lazy=True))
    
    def __repr__(self):
        return f'<MoodEntry {self.mood_type} - {self.intensity}>'

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    title = db.Column(String(200))
    content = db.Column(Text, nullable=False)
    mood_context = db.Column(String(50))  # Associated mood when written
    
    user = db.relationship('User', backref=db.backref('journal_entries', lazy=True))
    
    def __repr__(self):
        return f'<JournalEntry {self.title}>'

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('habits', lazy=True))
    
    def __repr__(self):
        return f'<Habit {self.name}>'

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    completed = db.Column(db.Boolean, default=True)
    notes = db.Column(Text)
    
    habit = db.relationship('Habit', backref=db.backref('logs', lazy=True))
    
    def __repr__(self):
        return f'<HabitLog {self.habit_id} - {self.completed}>'
