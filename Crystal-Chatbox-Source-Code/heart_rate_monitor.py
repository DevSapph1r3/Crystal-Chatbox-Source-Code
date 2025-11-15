import threading
import time
import requests
from settings import SETTINGS

heart_rate_state = {
    "bpm": 0,
    "is_connected": False,
    "last_update": None
}

heart_rate_lock = threading.Lock()

def get_heart_rate_state():
    with heart_rate_lock:
        return heart_rate_state.copy()

def fetch_from_pulsoid():
    """Fetch heart rate from Pulsoid API"""
    token = SETTINGS.get("heart_rate_pulsoid_token", "").strip()
    if not token:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://dev.pulsoid.net/api/v1/data/heart_rate/latest",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("heart_rate", 0)
        else:
            print(f"[Heart Rate] Pulsoid API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Heart Rate] Pulsoid fetch error: {e}")
        return None

def fetch_from_hyperate():
    """Fetch heart rate from HypeRate.io websocket (simplified polling)"""
    session_id = SETTINGS.get("heart_rate_hyperate_id", "").strip()
    if not session_id:
        return None
    
    try:
        response = requests.get(
            f"https://app.hyperate.io/api/v2/live/{session_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("hr", 0)
        else:
            print(f"[Heart Rate] HypeRate API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Heart Rate] HypeRate fetch error: {e}")
        return None

def fetch_from_custom_api():
    """Fetch heart rate from custom API endpoint"""
    api_url = SETTINGS.get("heart_rate_custom_api", "").strip()
    if not api_url:
        return None
    
    try:
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("bpm") or data.get("heart_rate") or data.get("hr", 0)
        else:
            print(f"[Heart Rate] Custom API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Heart Rate] Custom API fetch error: {e}")
        return None

def start_heart_rate_tracker(interval=5):
    """Start heart rate tracking thread"""
    def tracker():
        global heart_rate_state
        print("[Heart Rate Tracker] Thread started")
        last_error_time = 0
        
        while True:
            try:
                if not SETTINGS.get("heart_rate_enabled", False):
                    time.sleep(interval)
                    continue
                
                bpm = None
                source = SETTINGS.get("heart_rate_source", "pulsoid")
                
                if source == "pulsoid":
                    bpm = fetch_from_pulsoid()
                elif source == "hyperate":
                    bpm = fetch_from_hyperate()
                elif source == "custom":
                    bpm = fetch_from_custom_api()
                
                with heart_rate_lock:
                    if bpm is not None and bpm > 0:
                        heart_rate_state["bpm"] = int(bpm)
                        heart_rate_state["is_connected"] = True
                        heart_rate_state["last_update"] = time.time()
                    else:
                        if heart_rate_state["last_update"] and (time.time() - heart_rate_state["last_update"]) > 30:
                            heart_rate_state["is_connected"] = False
                            heart_rate_state["bpm"] = 0
                
                time.sleep(interval)
            except Exception as e:
                current_time = time.time()
                if current_time - last_error_time > 60:
                    print(f"[Heart Rate Tracker ERROR] {e}")
                    last_error_time = current_time
                time.sleep(interval)
    
    threading.Thread(target=tracker, daemon=True).start()
