"""
AI Message Generator using OpenAI
Generates creative custom messages for VRChat chatbox
"""
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Will be set when OpenAI API key is available
openai_available = False
try:
    import openai
    openai_available = True
except ImportError:
    logger.warning("OpenAI not available - install with: pip install openai")

MOODS = {
    "funny": "Generate a funny, lighthearted message",
    "wholesome": "Generate a warm, wholesome, friendly message",
    "mysterious": "Generate a mysterious, intriguing message",
    "energetic": "Generate an energetic, excited message",
    "chill": "Generate a calm, relaxed, chill message",
    "chaotic": "Generate a chaotic, random, unpredictable message",
    "professional": "Generate a professional, polite message",
    "gamer": "Generate a gaming-related message with gamer slang"
}

def is_configured():
    """Check if OpenAI is configured"""
    api_key = os.environ.get("OPENAI_API_KEY")
    return openai_available and api_key is not None and api_key != ""

def generate_message(mood="funny", theme="", max_length=30):
    """
    Generate a custom message using AI
    
    Args:
        mood: The mood/style of the message
        theme: Optional theme or topic
        max_length: Maximum character length (VRChat OSC limit is ~140 chars)
    
    Returns:
        Generated message string or None if failed
    """
    if not is_configured():
        return None
    
    try:
        mood_prompt = MOODS.get(mood, MOODS["funny"])
        theme_part = f" about {theme}" if theme else ""
        
        prompt = f"""{mood_prompt}{theme_part}. 
        
Requirements:
- Maximum {max_length} characters
- Suitable for VRChat chatbox
- Creative and unique
- No emojis (will be added separately)
- Just the message text, nothing else

Message:"""
        
        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative message generator for VRChat. Generate short, fun messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.9,
            n=1
        )
        
        message = response.choices[0].message.content.strip()
        
        # Clean up the message
        message = message.replace('"', '').replace("'", "").strip()
        
        # Truncate if needed
        if len(message) > max_length:
            message = message[:max_length-3] + "..."
        
        return message
        
    except Exception as e:
        logger.error(f"Error generating AI message: {e}")
        return None

def generate_batch_messages(count=5, mood="funny", theme=""):
    """Generate multiple messages at once"""
    if not is_configured():
        return []
    
    messages = []
    for _ in range(count):
        msg = generate_message(mood, theme)
        if msg:
            messages.append(msg)
    
    return messages
