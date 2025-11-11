import threading
import time
import subprocess
from settings import SETTINGS

window_state = {
    "window_title": "",
    "app_name": ""
}
window_lock = threading.Lock()


def get_window_state():
    with window_lock:
        return window_state.copy()

def get_chrome_tab():
    try:
        title = subprocess.check_output([
            "osascript",
            "-e",
            'tell application "Google Chrome" to get title of active tab of front window'
        ]).decode("utf-8").strip()
        return title
    except subprocess.CalledProcessError:
        return None


def get_safari_tab():
    try:
        title = subprocess.check_output([
            "osascript",
            "-e",
            'tell application "Safari" to get name of front document'
        ]).decode("utf-8").strip()
        return title
    except subprocess.CalledProcessError:
        return None


def get_firefox_tab():
    try:
        title = subprocess.check_output([
            "osascript",
            "-e",
            'tell application "Firefox" to get name of front window'
        ]).decode("utf-8").strip()
        return title
    except subprocess.CalledProcessError:
        return None


def get_active_app():
    try:
        name = subprocess.check_output([
            "osascript",
            "-e",
            'tell application "System Events" to get name of first application process whose frontmost is true'
        ]).decode("utf-8").strip()
        return name
    except subprocess.CalledProcessError:
        return None


def start_window_tracker(interval=2):
    def tracker():
        global window_state
        print("[Window Tracker] Thread started (macOS Quartz/AppleScript)")
        last_error_time = 0

        while True:
            try:
                if not SETTINGS.get("window_tracking_enabled", False):
                    time.sleep(interval)
                    continue

                active_app = get_active_app()
                active_tab = None

                if active_app == "Google Chrome":
                    active_tab = get_chrome_tab()
                elif active_app == "Safari":
                    active_tab = get_safari_tab()
                elif active_app == "Firefox":
                    active_tab = get_firefox_tab()

                with window_lock:
                    if active_app:
                        if active_tab:
                            window_state["window_title"] = active_tab
                            window_state["app_name"] = f"{active_app}: {active_tab}"
                        else:
                            window_state["window_title"] = active_app
                            window_state["app_name"] = active_app
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

def debug_print():
    while True:
        state = get_window_state()
        print(f"[Debug] Active Window → title: '{state['window_title']}', app: '{state['app_name']}'")
        time.sleep(2)
