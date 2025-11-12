"""
Discord Rich Presence Integration
Shows Discord activity in VRChat chatbox
"""
import logging
import threading
import time

logger = logging.getLogger(__name__)

# Discord state
discord_state = {
    "activity": None,
    "status": None,
    "connected": False,
    "enabled": False,
    "emoji": "🎮"
}

discord_lock = threading.Lock()
discord_thread = None

# Try to import pypresence
try:
    from pypresence import Presence, InvalidID
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False
    logger.warning("pypresence not available - Discord integration disabled")

def get_discord_state():
    """Get current Discord state"""
    with discord_lock:
        return discord_state.copy()

def update_discord_status():
    """
    Try to get Discord status via local RPC
    NOTE: This only works if Discord is running locally
    """
    if not PYPRESENCE_AVAILABLE:
        return False
    
    try:
        # For Replit/cloud environments, this won't work
        # Discord RPC requires local Discord client
        # This is here for completeness but will fail on Replit
        
        with discord_lock:
            discord_state['connected'] = False
            discord_state['activity'] = "Not available (cloud environment)"
        
        return False
        
    except Exception as e:
        logger.debug(f"Discord RPC not available: {e}")
        with discord_lock:
            discord_state['connected'] = False
        return False

def discord_updater_thread(interval=10):
    """Background thread to update Discord status"""
    logger.info(f"[Discord] Thread started (interval: {interval}s)")
    
    while True:
        try:
            with discord_lock:
                enabled = discord_state.get('enabled', False)
            
            if enabled:
                update_discord_status()
            
            time.sleep(interval)
            
        except Exception as e:
            logger.error(f"Discord updater error: {e}")
            time.sleep(60)

def start_discord_tracker(interval=10, enabled=False):
    """Start the Discord tracking thread"""
    global discord_thread, discord_state
    
    with discord_lock:
        discord_state['enabled'] = enabled
    
    # Only start thread if enabled
    if enabled and (discord_thread is None or not discord_thread.is_alive()):
        discord_thread = threading.Thread(
            target=discord_updater_thread,
            args=(interval,),
            daemon=True
        )
        discord_thread.start()

def enable_discord():
    """Enable Discord tracking"""
    with discord_lock:
        discord_state['enabled'] = True

def disable_discord():
    """Disable Discord tracking"""
    with discord_lock:
        discord_state['enabled'] = False

def get_discord_text():
    """Get formatted Discord text for chatbox"""
    state = get_discord_state()
    
    if not state.get('enabled'):
        return None
    
    if not state.get('connected'):
        return None  # Don't show anything if not connected
    
    activity = state.get('activity')
    if activity:
        emoji = state.get('emoji', '🎮')
        return f"{emoji} {activity}"
    
    return None

def is_available():
    """Check if Discord RPC is available"""
    return PYPRESENCE_AVAILABLE
