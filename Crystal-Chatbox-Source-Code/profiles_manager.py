"""
Profiles/Presets Manager
Save and load different chatbox configurations
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

PROFILES_FILE = "profiles.json"

# Default profile structure
DEFAULT_PROFILE = {
    "name": "Default",
    "created_at": None,
    "settings": {
        "show_time": True,
        "show_custom": True,
        "show_music": True,
        "show_window": False,
        "show_heartrate": False,
        "custom_texts": ["Custom Message Test"],
        "time_emoji": "⏰",
        "song_emoji": "🎶",
        "window_emoji": "💻",
        "heartrate_emoji": "❤️",
        "layout_order": ["time", "custom", "song", "window", "heartrate"],
        "osc_send_interval": 3,
        "music_progress": True,
        "progress_style": "bar"
    }
}

def load_profiles() -> List[Dict]:
    """Load all saved profiles"""
    try:
        if os.path.exists(PROFILES_FILE):
            with open(PROFILES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading profiles: {e}")
    
    return []

def save_profiles(profiles: List[Dict]) -> bool:
    """Save profiles to file"""
    try:
        with open(PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving profiles: {e}")
        return False

def get_profile(profile_name: str) -> Optional[Dict]:
    """Get a specific profile by name"""
    profiles = load_profiles()
    for profile in profiles:
        if profile.get('name') == profile_name:
            return profile
    return None

def create_profile(name: str, settings: Dict) -> bool:
    """Create a new profile"""
    profiles = load_profiles()
    
    # Check if profile already exists
    for profile in profiles:
        if profile.get('name') == name:
            return False  # Profile already exists
    
    new_profile = {
        "name": name,
        "created_at": datetime.now().isoformat(),
        "settings": settings
    }
    
    profiles.append(new_profile)
    return save_profiles(profiles)

def update_profile(name: str, settings: Dict) -> bool:
    """Update an existing profile"""
    profiles = load_profiles()
    
    for profile in profiles:
        if profile.get('name') == name:
            profile['settings'] = settings
            profile['updated_at'] = datetime.now().isoformat()
            return save_profiles(profiles)
    
    return False

def delete_profile(name: str) -> bool:
    """Delete a profile"""
    profiles = load_profiles()
    
    # Don't allow deleting the default profile
    if name.lower() == "default":
        return False
    
    profiles = [p for p in profiles if p.get('name') != name]
    return save_profiles(profiles)

def list_profiles() -> List[str]:
    """Get list of profile names"""
    profiles = load_profiles()
    return [p.get('name', 'Unnamed') for p in profiles]

def export_profile(name: str) -> Optional[str]:
    """Export a profile as JSON string"""
    profile = get_profile(name)
    if profile:
        return json.dumps(profile, indent=2)
    return None

def import_profile(profile_json: str) -> bool:
    """Import a profile from JSON string"""
    try:
        profile_data = json.loads(profile_json)
        
        # Validate structure
        if 'name' not in profile_data or 'settings' not in profile_data:
            return False
        
        profiles = load_profiles()
        
        # Check for duplicate names
        name = profile_data['name']
        for i, profile in enumerate(profiles):
            if profile.get('name') == name:
                # Replace existing
                profiles[i] = profile_data
                return save_profiles(profiles)
        
        # Add new profile
        profiles.append(profile_data)
        return save_profiles(profiles)
        
    except Exception as e:
        logger.error(f"Error importing profile: {e}")
        return False
