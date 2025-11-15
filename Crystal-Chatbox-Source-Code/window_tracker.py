import threading
import time
import sys
from settings import SETTINGS

window_state = {
    "window_title": "",
    "app_name": ""
}
window_lock = threading.Lock()

def get_window_state():
    with window_lock:
        return window_state.copy()

def get_active_window_cross_platform():
    """
    Get active window using cross-platform pywinctl library.
    Falls back to platform-specific methods if needed.
    """
    try:
        import pywinctl as pwc
        active_window = pwc.getActiveWindow()
        
        if active_window:
            title = active_window.title
            app_name = title
            
            if hasattr(active_window, 'app'):
                app_info = active_window.app
                if app_info and hasattr(app_info, 'name'):
                    app_name = f"{app_info.name}: {title}" if title else app_info.name
            
            return {
                "title": title or "",
                "app": app_name or title or ""
            }
        return None
    except Exception as e:
        return None

def get_active_window_macos_fallback():
    """
    macOS-specific fallback using AppleScript.
    Only used if pywinctl fails on macOS.
    """
    try:
        import subprocess
        
        app_name = subprocess.check_output([
            "osascript",
            "-e",
            'tell application "System Events" to get name of first application process whose frontmost is true'
        ]).decode("utf-8").strip()
        
        title = None
        if app_name == "Google Chrome":
            try:
                title = subprocess.check_output([
                    "osascript",
                    "-e",
                    'tell application "Google Chrome" to get title of active tab of front window'
                ]).decode("utf-8").strip()
            except:
                pass
        elif app_name == "Safari":
            try:
                title = subprocess.check_output([
                    "osascript",
                    "-e",
                    'tell application "Safari" to get name of front document'
                ]).decode("utf-8").strip()
            except:
                pass
        elif app_name == "Firefox":
            try:
                title = subprocess.check_output([
                    "osascript",
                    "-e",
                    'tell application "Firefox" to get name of front window'
                ]).decode("utf-8").strip()
            except:
                pass
        
        if title:
            return {"title": title, "app": f"{app_name}: {title}"}
        else:
            return {"title": app_name, "app": app_name}
    except Exception:
        return None

def start_window_tracker(interval=2):
    def tracker():
        global window_state
        
        platform = sys.platform
        print(f"[Window Tracker] Thread started (Platform: {platform})")
        last_error_time = 0
        use_fallback = False

        while True:
            try:
                if not SETTINGS.get("window_tracking_enabled", False):
                    time.sleep(interval)
                    continue

                window_info = None
                
                if not use_fallback:
                    window_info = get_active_window_cross_platform()
                
                if window_info is None and platform == "darwin":
                    window_info = get_active_window_macos_fallback()
                    if window_info:
                        use_fallback = True

                with window_lock:
                    if window_info:
                        window_state["window_title"] = window_info.get("title", "")
                        window_state["app_name"] = window_info.get("app", "Unknown")
                    else:
                        window_state["window_title"] = ""
                        window_state["app_name"] = "Unknown"

            except Exception as e:
                current_time = time.time()
                if current_time - last_error_time > 60:
                    print(f"[Window Tracker ERROR] {e}")
                    last_error_time = current_time
                with window_lock:
                    window_state["window_title"] = ""
                    window_state["app_name"] = "Unknown"

            time.sleep(interval)

    threading.Thread(target=tracker, daemon=True).start()
