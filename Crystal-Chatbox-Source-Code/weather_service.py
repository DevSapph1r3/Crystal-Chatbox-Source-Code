"""
Weather Integration Service
Displays current weather in VRChat chatbox
"""
import requests
import logging
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger(__name__)

# Weather state
weather_state = {
    "temperature": None,
    "condition": None,
    "location": None,
    "last_updated": None,
    "enabled": False,
    "emoji": "🌤️"
}

weather_lock = threading.Lock()
weather_thread = None

# Free weather service (no API key needed)
# Using wttr.in which provides weather data in JSON format
WEATHER_API_URL = "https://wttr.in/{location}?format=j1"

def get_weather_state():
    """Get current weather state"""
    with weather_lock:
        state = weather_state.copy()
        if state.get('last_updated') and isinstance(state['last_updated'], datetime):
            state['last_updated'] = state['last_updated'].isoformat()
        return state

def update_weather(location="auto"):
    """
    Fetch weather from API
    Using wttr.in free service
    """
    try:
        # Clean location
        if not location or location.lower() == "auto":
            location = ""  # Auto-detect from IP
        
        url = WEATHER_API_URL.format(location=location or "")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract weather data
            current = data.get('current_condition', [{}])[0]
            nearest_area = data.get('nearest_area', [{}])[0]
            
            temp_c = current.get('temp_C', 'N/A')
            temp_f = current.get('temp_F', 'N/A')
            condition = current.get('weatherDesc', [{}])[0].get('value', 'Unknown')
            location_name = nearest_area.get('areaName', [{}])[0].get('value', 'Unknown')
            
            # Pick emoji based on condition
            emoji = "🌤️"
            condition_lower = condition.lower()
            if "sun" in condition_lower or "clear" in condition_lower:
                emoji = "☀️"
            elif "cloud" in condition_lower:
                emoji = "☁️"
            elif "rain" in condition_lower:
                emoji = "🌧️"
            elif "storm" in condition_lower:
                emoji = "⛈️"
            elif "snow" in condition_lower:
                emoji = "❄️"
            elif "fog" in condition_lower or "mist" in condition_lower:
                emoji = "🌫️"
            
            with weather_lock:
                weather_state['temperature'] = f"{temp_f}°F"
                weather_state['condition'] = condition
                weather_state['location'] = location_name
                weather_state['last_updated'] = datetime.now()
                weather_state['emoji'] = emoji
            
            logger.info(f"Weather updated: {temp_f}°F, {condition} in {location_name}")
            return True
            
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
    
    return False

def weather_updater_thread(interval=600, location="auto"):
    """Background thread to update weather periodically"""
    global weather_state
    
    logger.info(f"[Weather] Thread started (interval: {interval}s)")
    
    while True:
        try:
            with weather_lock:
                enabled = weather_state.get('enabled', False)
            
            if enabled:
                update_weather(location)
            
            time.sleep(interval)
            
        except Exception as e:
            logger.error(f"Weather updater error: {e}")
            time.sleep(60)

def start_weather_tracker(interval=600, location="auto", enabled=False):
    """Start the weather tracking thread"""
    global weather_thread, weather_state
    
    with weather_lock:
        weather_state['enabled'] = enabled
    
    # Only start thread if enabled
    if enabled and (weather_thread is None or not weather_thread.is_alive()):
        weather_thread = threading.Thread(
            target=weather_updater_thread,
            args=(interval, location),
            daemon=True
        )
        weather_thread.start()
        
        # Initial update
        threading.Thread(target=update_weather, args=(location,), daemon=True).start()

def enable_weather(location="auto"):
    """Enable weather tracking"""
    with weather_lock:
        weather_state['enabled'] = True
    update_weather(location)

def disable_weather():
    """Disable weather tracking"""
    with weather_lock:
        weather_state['enabled'] = False

def get_weather_text():
    """Get formatted weather text for chatbox"""
    state = get_weather_state()
    
    if not state.get('enabled') or not state.get('temperature'):
        return None
    
    emoji = state.get('emoji', '🌤️')
    temp = state.get('temperature', '?')
    condition = state.get('condition', 'Unknown')
    
    return f"{emoji} {temp} {condition}"
