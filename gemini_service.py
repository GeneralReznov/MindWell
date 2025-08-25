import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from google import genai
from google.genai import types
from pydantic import BaseModel
from models import MoodEntry, JournalEntry, HabitLog

# Initialize Gemini client
os.environ['GEMINI_API_KEY']="AIzaSyChpIrLMzJc42ETm0jS4KiKC_ra9Gv1_vE"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

class MoodInsight(BaseModel):
    insight: str
    recommendation: str
    supportive_message: str
    confidence: float

class JournalAnalysis(BaseModel):
    emotional_themes: List[str]
    sentiment_score: float
    key_insights: List[str]
    supportive_response: str

class HabitSuggestion(BaseModel):
    habit_name: str
    description: str
    why_helpful: str
    difficulty_level: str

def analyze_mood_patterns(mood_entries: List[MoodEntry]) -> Optional[MoodInsight]:
    """Analyze mood patterns and provide insights using Gemini."""
    if not mood_entries:
        return None
    
    try:
        # Prepare mood data for analysis
        mood_data = []
        for entry in mood_entries[-14:]:  # Last 2 weeks
            mood_data.append({
                "date": entry.timestamp.strftime("%Y-%m-%d"),
                "mood": entry.mood_type,
                "intensity": entry.intensity,
                "notes": entry.notes or ""
            })
        
        system_prompt = """You are a compassionate mental health companion AI. 
        Analyze the user's mood patterns and provide gentle, supportive insights. 
        Focus on patterns, trends, and actionable recommendations.
        Be empathetic and encouraging while maintaining professional boundaries.
        Respond in JSON format with insight, recommendation, supportive_message, and confidence (0-1)."""
        
        prompt = f"""Based on this mood tracking data from the past 2 weeks:
        {json.dumps(mood_data, indent=2)}
        
        Please provide:
        1. A gentle insight about their emotional patterns
        2. A practical recommendation for their wellbeing
        3. A supportive, encouraging message
        4. Your confidence level in this analysis (0-1)
        
        Remember to be compassionate and focus on growth and self-care."""
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=MoodInsight,
                temperature=0.7
            )
        )
        
        if response.text:
            data = json.loads(response.text)
            return MoodInsight(**data)
            
    except Exception as e:
        logging.error(f"Error analyzing mood patterns: {e}")
        return None

def analyze_journal_entry(content: str, mood_context: str = None) -> Optional[JournalAnalysis]:
    """Analyze a journal entry and provide supportive insights."""
    if not content:
        return None
        
    try:
        system_prompt = """You are a compassionate mental health companion AI.
        Analyze journal entries with empathy and provide supportive insights.
        Focus on emotional themes, sentiment, and encouraging responses.
        Be gentle, non-judgmental, and supportive."""
        
        prompt = f"""Please analyze this journal entry:
        
        Content: "{content}"
        Context mood: {mood_context or "unknown"}
        
        Provide:
        1. Key emotional themes present (3-5 themes)
        2. Overall sentiment score (-1 to 1, where -1 is very negative, 1 is very positive)
        3. 2-3 key insights about their emotional state
        4. A supportive, encouraging response that validates their feelings
        
        Be compassionate and focus on their strength and growth."""
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=JournalAnalysis,
                temperature=0.7
            )
        )
        
        if response.text:
            data = json.loads(response.text)
            return JournalAnalysis(**data)
            
    except Exception as e:
        logging.error(f"Error analyzing journal entry: {e}")
        return None

def suggest_habits_for_mood(current_mood: str, existing_habits: Optional[List[str]] = None) -> List[HabitSuggestion]:
    """Suggest personalized habits based on current mood and existing habits."""
    if existing_habits is None:
        existing_habits = []
        
    try:
        mood_context = {
            "happy": "feeling joyful and positive",
            "sad": "feeling down or melancholy", 
            "anxious": "feeling worried or restless",
            "energized": "feeling motivated and energetic",
            "neutral": "in a neutral or balanced state"
        }
        
        system_prompt = """You are a mental health companion AI specializing in habit formation.
        Suggest 3-4 helpful, achievable habits based on the user's current emotional state.
        Focus on evidence-based wellness practices that are gentle and sustainable."""
        
        prompt = f"""The user is currently {mood_context.get(current_mood, 'in an unknown state')}.
        
        They already have these habits: {existing_habits or []}
        
        Please suggest 3-4 new habits that would be helpful for someone in their current emotional state.
        Each suggestion should include:
        1. A clear, actionable habit name
        2. A brief description of how to do it
        3. Why it would be helpful for their current mood
        4. Difficulty level (easy, moderate, challenging)
        
        Focus on small, achievable habits that support mental wellness."""
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema={"type": "array", "items": HabitSuggestion.model_json_schema()},
                temperature=0.8
            )
        )
        
        if response.text:
            data = json.loads(response.text)
            return [HabitSuggestion(**item) for item in data]
        else:
            return []
            
    except Exception as e:
        logging.error(f"Error suggesting habits: {e}")
        return []

def generate_daily_affirmation(mood: str = "neutral") -> str:
    """Generate a personalized daily affirmation based on mood."""
    try:
        mood_prompts = {
            "happy": "celebrating joy and positivity",
            "sad": "needing comfort and gentle encouragement",
            "anxious": "seeking calm and reassurance", 
            "energized": "channeling motivation and energy",
            "neutral": "maintaining balance and centeredness"
        }
        
        prompt = f"""Create a gentle, personalized affirmation for someone who is {mood_prompts.get(mood, 'in a neutral state')}.
        The affirmation should be:
        - 1-2 sentences
        - Encouraging and supportive
        - Focused on their inner strength
        - Appropriate for their current emotional state
        
        Just return the affirmation text, nothing else."""
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.8)
        )
        
        return response.text.strip() if response.text else "You are worthy of love and care, especially from yourself."
        
    except Exception as e:
        logging.error(f"Error generating affirmation: {e}")
        return "You are doing your best, and that is enough."

def get_mood_based_prompt(mood: str, entry_type: str = "journal") -> str:
    """Get AI-generated prompts based on current mood."""
    try:
        prompt_types = {
            "journal": "journaling prompt that encourages reflection",
            "checkin": "check-in prompt for mood assessment"
        }
        
        system_prompt = """You are a compassionate mental health companion.
        Create gentle, thoughtful prompts that encourage self-reflection and emotional awareness."""
        
        prompt = f"""Create a supportive {prompt_types.get(entry_type, 'journaling prompt')} for someone feeling {mood}.
        
        The prompt should:
        - Be one thoughtful question or invitation
        - Be appropriate for their emotional state
        - Encourage gentle self-reflection
        - Not be overwhelming or intense
        
        Just return the prompt question, nothing else."""
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        
        return response.text.strip() if response.text else "What's one thing you'd like to acknowledge about how you're feeling right now?"
        
    except Exception as e:
        logging.error(f"Error generating prompt: {e}")
        return "How are you taking care of yourself today?"