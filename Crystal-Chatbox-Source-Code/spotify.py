import threading
import time
import os
from settings import SETTINGS

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIFY_AVAILABLE = True
except ImportError:
    SPOTIFY_AVAILABLE = False

spotify_state = {
    "song_text": "",
    "song_pos": 0,
    "song_dur": 0,
    "album_art": ""
}

spotify_lock = threading.Lock()
sp = None

def get_spotify_state():
    with spotify_lock:
        return spotify_state.copy()

def init_spotify_web():
    global sp
    if not SPOTIFY_AVAILABLE:
        print("[Spotify] spotipy library not available")
        return
    
    client_id = SETTINGS.get("spotify_client_id", "").strip()
    client_secret = SETTINGS.get("spotify_client_secret", "").strip()
    redirect_uri = SETTINGS.get("spotify_redirect_uri", "")
    
    if not client_id or not client_secret:
        print("[Spotify] Missing client ID or secret, Spotify integration disabled")
        sp = None
        return
    
    try:
        scope = "user-read-currently-playing user-read-playback-state"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=".spotify_cache",
            open_browser=False
        ))
        print("[Spotify] OAuth setup complete. Please visit the auth URL if needed.")
    except Exception as e:
        print(f"[Spotify Init Error] {e}")
        sp = None

def start_spotify_tracker(interval=1):
    def tracker():
        global spotify_state
        print("[Spotify Tracker] Thread started")
        last_error_time = 0
        
        while True:
            try:
                if sp is None:
                    time.sleep(interval)
                    continue
                
                try:
                    current = sp.current_playback()
                except spotipy.exceptions.SpotifyException as e:
                    if e.http_status == 401:
                        current_time = time.time()
                        if current_time - last_error_time > 60:
                            print("[Spotify] Not authenticated or token expired. Please connect to Spotify via the dashboard.")
                            last_error_time = current_time
                        time.sleep(5)
                        continue
                    else:
                        raise
                
                with spotify_lock:
                    if current and current.get("is_playing") and current.get("item"):
                        item = current["item"]
                        artists = ", ".join([artist["name"] for artist in item.get("artists", [])])
                        track_name = item.get("name", "Unknown")
                        spotify_state["song_text"] = f"{track_name} - {artists}"
                        spotify_state["song_pos"] = current.get("progress_ms", 0) // 1000
                        spotify_state["song_dur"] = item.get("duration_ms", 0) // 1000
                        
                        images = item.get("album", {}).get("images", [])
                        if images:
                            spotify_state["album_art"] = images[0].get("url", "")
                        else:
                            spotify_state["album_art"] = ""
                    else:
                        spotify_state["song_text"] = ""
                        spotify_state["song_pos"] = 0
                        spotify_state["song_dur"] = 0
                        spotify_state["album_art"] = ""
                
                time.sleep(interval)
            except Exception as e:
                current_time = time.time()
                if current_time - last_error_time > 60:
                    print(f"[Spotify Tracker ERROR] {e}")
                    last_error_time = current_time
                time.sleep(interval)
    
    threading.Thread(target=tracker, daemon=True).start()
