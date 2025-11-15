"""
Custom Text Effects
Apply visual effects to chatbox messages
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Unicode characters for effects
RAINBOW_COLORS = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
SPARKLES = ['✨', '⭐', '🌟', '💫', '⚡']

def rainbow_text(text: str) -> str:
    """Apply rainbow effect using colored circle emojis"""
    if not text:
        return text
    
    # Add color indicators
    colors = ['R', 'O', 'Y', 'G', 'B', 'P']  # Rainbow colors
    result = []
    
    for i, char in enumerate(text):
        if char.strip():  # Only colorize non-whitespace
            color_indicator = colors[i % len(colors)]
            result.append(f"{char}")
        else:
            result.append(char)
    
    # Add rainbow emoji prefix
    return f"🌈 {text}"

def sparkle_text(text: str) -> str:
    """Add sparkles around text"""
    if not text:
        return text
    
    return f"✨ {text} ✨"

def wave_text(text: str, position: int = 0) -> str:
    """Create a wave effect (animated when position changes)"""
    if not text:
        return text
    
    # Add wave emoji
    return f"〰️ {text}"

def bounce_text(text: str) -> str:
    """Add bouncing effect indicators"""
    if not text:
        return text
    
    return f"⬆️ {text} ⬇️"

def fire_text(text: str) -> str:
    """Add fire effect"""
    if not text:
        return text
    
    return f"🔥 {text} 🔥"

def ice_text(text: str) -> str:
    """Add ice/snow effect"""
    if not text:
        return text
    
    return f"❄️ {text} ❄️"

def neon_text(text: str) -> str:
    """Add neon glow effect"""
    if not text:
        return text
    
    return f"💡 {text} 💡"

def heart_text(text: str) -> str:
    """Add hearts around text"""
    if not text:
        return text
    
    return f"💖 {text} 💖"

def star_text(text: str) -> str:
    """Add stars around text"""
    if not text:
        return text
    
    return f"⭐ {text} ⭐"

def apply_effect(text: str, effect_name: str, **kwargs) -> str:
    """
    Apply a text effect
    
    Args:
        text: The text to apply effect to
        effect_name: Name of the effect
        **kwargs: Additional parameters for the effect
    
    Returns:
        Text with effect applied
    """
    effects = {
        'rainbow': rainbow_text,
        'sparkle': sparkle_text,
        'wave': wave_text,
        'bounce': bounce_text,
        'fire': fire_text,
        'ice': ice_text,
        'neon': neon_text,
        'heart': heart_text,
        'star': star_text,
        'none': lambda x: x
    }
    
    effect_func = effects.get(effect_name.lower())
    
    if effect_func:
        try:
            return effect_func(text, **kwargs) if effect_name == 'wave' else effect_func(text)
        except Exception as e:
            logger.error(f"Error applying effect {effect_name}: {e}")
            return text
    
    return text

def get_available_effects() -> list:
    """Get list of available text effects"""
    return [
        {'id': 'none', 'name': 'None', 'emoji': ''},
        {'id': 'rainbow', 'name': 'Rainbow', 'emoji': '🌈'},
        {'id': 'sparkle', 'name': 'Sparkle', 'emoji': '✨'},
        {'id': 'fire', 'name': 'Fire', 'emoji': '🔥'},
        {'id': 'ice', 'name': 'Ice', 'emoji': '❄️'},
        {'id': 'heart', 'name': 'Hearts', 'emoji': '💖'},
        {'id': 'star', 'name': 'Stars', 'emoji': '⭐'},
        {'id': 'neon', 'name': 'Neon', 'emoji': '💡'},
        {'id': 'wave', 'name': 'Wave', 'emoji': '〰️'},
        {'id': 'bounce', 'name': 'Bounce', 'emoji': '⬆️'},
    ]
