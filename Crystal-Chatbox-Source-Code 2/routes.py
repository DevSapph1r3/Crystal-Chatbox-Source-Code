import threading
import time
import json
import os
import random
import logging
from datetime import datetime
import pytz

from flask import Flask, render_template, request, jsonify, redirect, send_file
from pythonosc.udp_client import SimpleUDPClient

from settings import SETTINGS 
import spotify
import window_tracker
import heart_rate_monitor

SETTINGS_FILE = "settings.json"
ERROR_LOG_FILE = "vrchat_errors.log"

logging.basicConfig(
    filename=ERROR_LOG_FILE,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

chatbox_visible = SETTINGS.get("chatbox_visible", False)
show_time = SETTINGS.get("show_time", True)
show_custom = SETTINGS.get("show_custom", True)
show_music = SETTINGS.get("show_music", True)
show_window = SETTINGS.get("show_window", False)
show_heartrate = SETTINGS.get("show_heartrate", False)

settings_changed = False
if SETTINGS.get("window_tracking_enabled", False) and not show_window:
    show_window = True
    SETTINGS["show_window"] = True
    settings_changed = True
if SETTINGS.get("heart_rate_enabled", False) and not show_heartrate:
    show_heartrate = True
    SETTINGS["show_heartrate"] = True
    settings_changed = True

if settings_changed:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
    except Exception as e:
        print(f"[Startup] Failed to sync settings: {e}")

auto_send_paused = False
connection_status = "disconnected"
last_successful_send = None
last_osc_send_time = 0

current_time_text = ""
current_custom_text = SETTINGS.get("custom_texts", ["Custom Message Test"])[0]
last_message_sent = ""
text_cycle_index = 0
next_custom_in = SETTINGS.get("osc_send_interval", 3)
per_message_timers = {}
message_queue = []

CUSTOM_TEXTS = SETTINGS.get("custom_texts", [])
OSC_SEND_INTERVAL = SETTINGS.get("osc_send_interval", 3)
DASHBOARD_UPDATE_INTERVAL = SETTINGS.get("dashboard_update_interval", 1)
TIMEZONE = SETTINGS.get("timezone", "local")
MUSIC_PROGRESS = SETTINGS.get("music_progress", True)
PROGRESS_STYLE = SETTINGS.get("progress_style", "bar")
LAYOUT_ORDER = SETTINGS.get("layout_order", ["time","custom","song","window","heartrate"])

current_custom_text = CUSTOM_TEXTS[0] if CUSTOM_TEXTS else "Custom Message Test"
current_time_text = datetime.now().strftime("%I:%M %p").lstrip("0")

def log_error(message, exception=None):
    if SETTINGS.get("error_log_enabled", True):
        if exception:
            logging.error(f"{message}: {str(exception)}")
        else:
            logging.error(message)

def make_client():
    ip = SETTINGS.get("quest_ip", "") or "127.0.0.1"
    port = int(SETTINGS.get("quest_port", 9000))
    return SimpleUDPClient(ip, port)

client = make_client()

def replace_variables(text):
    """Replace variable tags like {song} and {time} in messages"""
    if not text:
        return text
    
    result = text
    
    tz_setting = SETTINGS.get("timezone", "local")
    if tz_setting == "local":
        now = datetime.now()
    else:
        now = datetime.now(pytz.timezone(str(tz_setting)))
    time_str = now.strftime("%I:%M %p").lstrip("0")
    
    sstate = spotify.get_spotify_state()
    song_str = sstate.get("song_text", "No song playing")
    
    result = result.replace("{time}", time_str)
    result = result.replace("{song}", song_str)
    
    return result

def get_next_custom_message():
    """Get next custom message based on random/weighted settings"""
    global text_cycle_index, CUSTOM_TEXTS
    
    if not CUSTOM_TEXTS:
        return ""
    
    if SETTINGS.get("random_order", False):
        weighted_messages = SETTINGS.get("weighted_messages", {})
        
        if weighted_messages:
            weights = []
            for idx in range(len(CUSTOM_TEXTS)):
                weight = weighted_messages.get(str(idx), 1)
                weights.append(weight)
            
            text_cycle_index = random.choices(range(len(CUSTOM_TEXTS)), weights=weights, k=1)[0]
        else:
            text_cycle_index = random.randint(0, len(CUSTOM_TEXTS) - 1)
    else:
        text_cycle_index = (text_cycle_index + 1) % len(CUSTOM_TEXTS)
    
    return CUSTOM_TEXTS[text_cycle_index]

def update_message_queue():
    """Update the preview of next messages to be sent"""
    global message_queue, CUSTOM_TEXTS
    
    queue_count = SETTINGS.get("message_queue_preview_count", 3)
    message_queue = []
    
    if not CUSTOM_TEXTS:
        return
    
    temp_index = text_cycle_index
    for i in range(queue_count):
        if SETTINGS.get("random_order", False):
            message_queue.append("Random")
        else:
            next_idx = (temp_index + i) % len(CUSTOM_TEXTS)
            msg = CUSTOM_TEXTS[next_idx]
            message_queue.append(msg[:30] + "..." if len(msg) > 30 else msg)

def get_current_preview():
    global current_time_text, current_custom_text
    
    if show_time:
        tz_setting = SETTINGS.get("timezone", "local")
        if tz_setting == "local":
            now = datetime.now()
        else:
            now = datetime.now(pytz.timezone(str(tz_setting)))
        current_time_text = now.strftime("%I:%M %p").lstrip("0")
    else:
        current_time_text = ""

    sstate = spotify.get_spotify_state()
    song_line = ""
    if show_music and sstate.get("song_text"):
        pos = int(sstate.get("song_pos", 0))
        dur = int(sstate.get("song_dur", 0))
        elapsed_min, elapsed_sec = divmod(pos, 60)
        total_min, total_sec = divmod(dur, 60)
        show_icons = SETTINGS.get("show_module_icons", True)
        song_emoji = SETTINGS.get("song_emoji", "🎶")
        icon = f"{song_emoji} " if show_icons and song_emoji else ""
        song_line = f"{icon}{sstate['song_text']} [{elapsed_min}:{elapsed_sec:02d} / {total_min}:{total_sec:02d}]"

    wstate = window_tracker.get_window_state()
    window_line = ""
    if show_window and wstate.get("app_name"):
        show_icons = SETTINGS.get("show_module_icons", True)
        window_emoji = SETTINGS.get("window_emoji", "💻")
        icon = f"{window_emoji} " if show_icons and window_emoji else ""
        window_line = f"{icon}{wstate['app_name']}"

    hrstate = heart_rate_monitor.get_heart_rate_state()
    heartrate_line = ""
    if show_heartrate and hrstate.get("is_connected") and hrstate.get("bpm", 0) > 0:
        show_icons = SETTINGS.get("show_module_icons", True)
        heartrate_emoji = SETTINGS.get("heartrate_emoji", "❤️")
        icon = f"{heartrate_emoji} " if show_icons and heartrate_emoji else ""
        heartrate_line = f"{icon}{hrstate['bpm']} BPM"

    show_icons = SETTINGS.get("show_module_icons", True)
    lines = []
    layout = SETTINGS.get("layout_order", ["time","custom","song","window","heartrate"])
    for part in layout:
        if part == "time" and current_time_text:
            time_emoji = SETTINGS.get("time_emoji", "⏰")
            icon = f"{time_emoji} " if show_icons and time_emoji else ""
            lines.append(f"{icon}{current_time_text}")
        elif part == "custom" and current_custom_text:
            processed_text = replace_variables(current_custom_text)
            lines.append(processed_text)
        elif part == "song" and song_line:
            lines.append(song_line)
        
            if SETTINGS.get("music_progress", True):
                style = SETTINGS.get("progress_style", "bar")
                progress_percent = 0
                dur = int(sstate.get("song_dur", 0))
                pos = int(sstate.get("song_pos", 0))
                if dur > 0:
                    progress_percent = int((pos / dur) * 100)
                progress_str = ""
                if style == "bar":
                    filled = int(progress_percent / 10)
                    empty = 10 - filled
                    progress_str = "█" * filled + "░" * empty
                elif style == "dots":
                    filled = int(progress_percent / 10)
                    empty = 10 - filled
                    progress_str = "●" * filled + "○" * empty
                elif style == "percentage":
                    progress_str = f"{progress_percent}%"
                if progress_str:
                    lines.append(progress_str)
        elif part == "window" and window_line:
            lines.append(window_line)
        elif part == "heartrate" and heartrate_line:
            lines.append(heartrate_line)

    result = "\n".join(lines).strip()
    return result

def send_to_vrchat(message):
    global last_message_sent, connection_status, last_successful_send, last_osc_send_time
    
    current_time = time.time()
    if current_time - last_osc_send_time < 0.5:
        return False
    
    last_osc_send_time = current_time
    
    if message:
        try:
            client.send_message("/chatbox/input", [message, True])
            last_message_sent = message
            connection_status = "connected"
            last_successful_send = datetime.now()
            print(f"[VRChat OSC SENT]\n{message}\n------------------")
            return True
        except Exception as e:
            connection_status = "disconnected"
            log_error("Failed to send OSC message", e)
            print("[VRChat OSC ERROR]", e)
            return False
    return False

def test_osc_connection():
    """Test OSC connection by sending a ping message"""
    global connection_status
    try:
        client.send_message("/chatbox/visible", 1)
        time.sleep(0.1)
        client.send_message("/chatbox/input", ["🔔 Connection Test", True])
        connection_status = "connected"
        return True
    except Exception as e:
        connection_status = "disconnected"
        log_error("OSC connection test failed", e)
        return False

def start_vrc_updater():
    def updater():
        global current_time_text, current_custom_text, last_message_sent
        global text_cycle_index, next_custom_in, per_message_timers, client
        print("[VRChat Updater] Thread started")

        osc_interval = max(1, int(SETTINGS.get("osc_send_interval", 3)))
        next_osc_send = osc_interval
        
        per_message_intervals = SETTINGS.get("per_message_intervals", {})
        for idx in range(len(CUSTOM_TEXTS)):
            key = str(idx)
            if key not in per_message_timers:
                per_message_timers[key] = per_message_intervals.get(key, osc_interval)

        last_quest_ip = SETTINGS.get("quest_ip", "")

        while True:
            try:
                time.sleep(1)
                
                current_quest_ip = SETTINGS.get("quest_ip", "")
                if current_quest_ip != last_quest_ip:
                    print(f"[Auto-Reconnect] Quest or Desktop IP changed from {last_quest_ip} to {current_quest_ip}")
                    client = make_client()
                    last_quest_ip = current_quest_ip
                
                next_osc_send -= 1
                next_custom_in = next_osc_send

                if next_osc_send <= 0:
                    if show_custom and CUSTOM_TEXTS:
                        current_idx = str(text_cycle_index)
                        per_msg_interval = SETTINGS.get("per_message_intervals", {}).get(current_idx, osc_interval)
                        
                        current_custom_text = get_next_custom_message()
                        update_message_queue()
                        
                        next_idx = str(text_cycle_index)
                        next_osc_send = SETTINGS.get("per_message_intervals", {}).get(next_idx, osc_interval)
                    else:
                        current_custom_text = ""
                        osc_interval = max(1, int(SETTINGS.get("osc_send_interval", 3)))
                        next_osc_send = osc_interval

                    preview_msg = get_current_preview()

                    if chatbox_visible and not auto_send_paused and preview_msg:
                        send_to_vrchat(preview_msg)
                    elif chatbox_visible:
                        try:
                            client.send_message("/chatbox/visible", 1)
                        except:
                            pass
                    else:
                        try:
                            client.send_message("/chatbox/visible", 0)
                        except:
                            pass

            except Exception as e:
                log_error("VRC Updater error", e)
                print("[VRC Updater ERROR]", e)
                time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    spotify.start_spotify_tracker(interval=1)
    window_tracker.start_window_tracker(interval=SETTINGS.get("window_tracking_interval", 2))
    heart_rate_monitor.start_heart_rate_tracker(interval=SETTINGS.get("heart_rate_update_interval", 5))
    start_vrc_updater()

    @app.route("/")
    def index():
        COMMON_TIMEZONES = [
            "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai",
            "Australia/Sydney"
        ]
        
        redirect_uri = f"{request.host_url}spotify-callback"
        
        return render_template(
            "dashboard.html",
            quest_ip=SETTINGS.get("quest_ip",""),
            quest_port=SETTINGS.get("quest_port",9000),
            spotify_client_id=SETTINGS.get("spotify_client_id",""),
            spotify_client_secret=SETTINGS.get("spotify_client_secret",""),
            spotify_redirect_uri=redirect_uri,
            customs_text="\n".join(SETTINGS.get("custom_texts", [])),
            osc_send_interval=SETTINGS.get("osc_send_interval", 3),
            dashboard_update_interval=SETTINGS.get("dashboard_update_interval", 1),
            music_progress=SETTINGS.get("music_progress", True),
            progress_style=SETTINGS.get("progress_style", "bar"),
            timezone=SETTINGS.get("timezone", "local"),
            timezones=COMMON_TIMEZONES,
            layout_order=SETTINGS.get("layout_order", ["time","custom","song","window","heartrate"]),
            per_message_intervals=SETTINGS.get("per_message_intervals", {}),
            theme=SETTINGS.get("theme", "dark"),
            random_order=SETTINGS.get("random_order", False),
            weighted_messages=SETTINGS.get("weighted_messages", {}),
            show_module_icons=SETTINGS.get("show_module_icons", True),
            streamer_mode=SETTINGS.get("streamer_mode", False),
            compact_mode=SETTINGS.get("compact_mode", False),
            window_tracking_enabled=SETTINGS.get("window_tracking_enabled", False),
            window_tracking_interval=SETTINGS.get("window_tracking_interval", 2),
            window_tracking_mode=SETTINGS.get("window_tracking_mode", "both"),
            heart_rate_enabled=SETTINGS.get("heart_rate_enabled", False),
            heart_rate_source=SETTINGS.get("heart_rate_source", "pulsoid"),
            heart_rate_pulsoid_token=SETTINGS.get("heart_rate_pulsoid_token", ""),
            heart_rate_hyperate_id=SETTINGS.get("heart_rate_hyperate_id", ""),
            heart_rate_custom_api=SETTINGS.get("heart_rate_custom_api", ""),
            heart_rate_update_interval=SETTINGS.get("heart_rate_update_interval", 5),
            time_emoji=SETTINGS.get("time_emoji", "⏰"),
            song_emoji=SETTINGS.get("song_emoji", "🎶"),
            window_emoji=SETTINGS.get("window_emoji", "💻"),
            heartrate_emoji=SETTINGS.get("heartrate_emoji", "❤️"),
            patreon_supporter=SETTINGS.get("patreon_supporter", False),
            custom_background=SETTINGS.get("custom_background", ""),
            custom_button_color=SETTINGS.get("custom_button_color", "")
        )

    @app.route("/status")
    def status():
        global current_time_text, current_custom_text, last_message_sent
        global show_time, show_custom, show_music, show_window, show_heartrate, auto_send_paused
        global connection_status, last_successful_send, message_queue

        time_text = current_time_text if show_time else "OFF"
        custom_text = current_custom_text if show_custom else "OFF"
        
        wstate = window_tracker.get_window_state()
        window_text = wstate.get("app_name", "No window detected") if show_window else "OFF"
        
        hrstate = heart_rate_monitor.get_heart_rate_state()
        heartrate_text = "Not connected"
        if show_heartrate:
            if hrstate.get("is_connected") and hrstate.get("bpm", 0) > 0:
                heartrate_text = f"{hrstate['bpm']} BPM"
            else:
                heartrate_text = "Waiting for data..."

        sstate = spotify.get_spotify_state()
        song_text = "No song playing"
        progress_percent = 0
        album_art = ""

        if show_music and sstate.get("song_text"):
            try:
                pos = int(sstate.get("song_pos", 0))
                dur = int(sstate.get("song_dur", 0))
                elapsed_min, elapsed_sec = divmod(pos, 60)
                total_min, total_sec = divmod(dur, 60)
                song_text = f"{sstate['song_text']} [{elapsed_min}:{elapsed_sec:02d} / {total_min}:{total_sec:02d}]"
                if dur > 0:
                    progress_percent = int((pos / dur) * 100)
                album_art = sstate.get("album_art", "")
            except Exception:
                song_text = sstate.get("song_text", "No song playing")
                progress_percent = 0

        progress_str = ""
        if SETTINGS.get("music_progress", True) and show_music and sstate.get("song_text"):
            style = SETTINGS.get("progress_style", "bar")
            if style == "bar":
                filled = int(progress_percent / 10)
                empty = 10 - filled
                progress_str = "█" * filled + "░" * empty
            elif style == "dots":
                filled = int(progress_percent / 10)
                empty = 10 - filled
                progress_str = "●" * filled + "○" * empty
            elif style == "percentage":
                progress_str = f"{progress_percent}%"

        preview_msg = get_current_preview()

        return jsonify({
            "chatbox": chatbox_visible,
            "auto_send_paused": auto_send_paused,
            "time": time_text,
            "time_on": show_time,
            "custom": custom_text,
            "custom_on": show_custom,
            "song": song_text,
            "music_on": show_music,
            "music_progress": SETTINGS.get("music_progress", True),
            "progress_style": SETTINGS.get("progress_style", "bar"),
            "progress_percent": progress_percent,
            "progress_string": progress_str,
            "last_message": last_message_sent,
            "preview": preview_msg,
            "album_art": album_art,
            "next_custom": next_custom_in,
            "connection_status": connection_status,
            "last_successful_send": last_successful_send.strftime("%I:%M:%S %p") if last_successful_send else "Never",
            "message_queue": message_queue,
            "theme": SETTINGS.get("theme", "dark"),
            "streamer_mode": SETTINGS.get("streamer_mode", False),
            "compact_mode": SETTINGS.get("compact_mode", False),
            "custom_texts": SETTINGS.get("custom_texts", []),
            "per_message_intervals": SETTINGS.get("per_message_intervals", {}),
            "weighted_messages": SETTINGS.get("weighted_messages", {}),
            "random_order": SETTINGS.get("random_order", False),
            "show_module_icons": SETTINGS.get("show_module_icons", True),
            "window": window_text,
            "window_on": show_window,
            "window_tracking_enabled": SETTINGS.get("window_tracking_enabled", False),
            "heartrate": heartrate_text,
            "heartrate_on": show_heartrate,
            "heart_rate_enabled": SETTINGS.get("heart_rate_enabled", False),
            "patreon_supporter": SETTINGS.get("patreon_supporter", False)
        })

    @app.route("/send", methods=["POST"])
    def send():
        global last_message_sent
        if request.is_json:
            data = request.get_json(force=True)
            msg = data.get("message", "").strip()
        else:
            msg = request.form.get("message", "").strip()
        if msg:
            if send_to_vrchat(msg):
                return jsonify({"ok": True}), 200
            else:
                return jsonify({"ok": False, "error": "OSC send failed"}), 500
        return jsonify({"ok": False, "error": "empty"}), 400

    @app.route("/send_now", methods=["POST"])
    def send_now():
        preview_msg = get_current_preview()
        if preview_msg and send_to_vrchat(preview_msg):
            return jsonify({"ok": True}), 200
        return jsonify({"ok": False}), 400

    @app.route("/test_connection", methods=["POST"])
    def test_connection():
        if test_osc_connection():
            return jsonify({"ok": True, "status": "connected"}), 200
        return jsonify({"ok": False, "status": "disconnected"}), 500

    @app.route("/ping_quest", methods=["POST"])
    def ping_quest():
        try:
            client.send_message("/chatbox/visible", 1)
            return jsonify({"ok": True}), 200
        except Exception as e:
            log_error("Ping Quest failed", e)
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/toggle_chatbox", methods=["POST"])
    def toggle_chatbox():
        global chatbox_visible
        chatbox_visible = not chatbox_visible
        SETTINGS["chatbox_visible"] = chatbox_visible
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        if chatbox_visible:
            try:
                client.send_message("/chatbox/visible", 1)
            except:
                pass
        else:
            try:
                client.send_message("/chatbox/visible", 0)
            except:
                pass
        return ("", 204)

    @app.route("/toggle_auto_send", methods=["POST"])
    def toggle_auto_send():
        global auto_send_paused
        auto_send_paused = not auto_send_paused
        return ("", 204)

    @app.route("/toggle_time", methods=["POST"])
    def toggle_time():
        global show_time
        show_time = not show_time
        SETTINGS["show_time"] = show_time
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)

    @app.route("/toggle_custom", methods=["POST"])
    def toggle_custom():
        global show_custom
        show_custom = not show_custom
        SETTINGS["show_custom"] = show_custom
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)

    @app.route("/toggle_music", methods=["POST"])
    def toggle_music():
        global show_music
        show_music = not show_music
        SETTINGS["show_music"] = show_music
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)

    @app.route("/toggle_music_progress", methods=["POST"])
    def toggle_music_progress():
        SETTINGS["music_progress"] = not SETTINGS.get("music_progress", True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)

    @app.route("/toggle_theme", methods=["POST"])
    def toggle_theme():
        current = SETTINGS.get("theme", "dark")
        SETTINGS["theme"] = "light" if current == "dark" else "dark"
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"theme": SETTINGS["theme"]}), 200

    @app.route("/toggle_random_order", methods=["POST"])
    def toggle_random_order():
        SETTINGS["random_order"] = not SETTINGS.get("random_order", False)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)

    @app.route("/toggle_module_icons", methods=["POST"])
    def toggle_module_icons():
        SETTINGS["show_module_icons"] = not SETTINGS.get("show_module_icons", True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)

    @app.route("/toggle_streamer_mode", methods=["POST"])
    def toggle_streamer_mode():
        SETTINGS["streamer_mode"] = not SETTINGS.get("streamer_mode", False)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"streamer_mode": SETTINGS["streamer_mode"]}), 200

    @app.route("/toggle_compact_mode", methods=["POST"])
    def toggle_compact_mode():
        SETTINGS["compact_mode"] = not SETTINGS.get("compact_mode", False)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"compact_mode": SETTINGS["compact_mode"]}), 200

    @app.route("/set_progress_style", methods=["POST"])
    def set_progress_style():
        data = request.get_json(force=True)
        style = data.get("style", "bar")
        if style in ["bar", "dots", "percentage"]:
            SETTINGS["progress_style"] = style
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f, indent=4)
        return ("", 204)
    
    @app.route("/toggle_window", methods=["POST"])
    def toggle_window():
        global show_window
        show_window = not show_window
        SETTINGS["show_window"] = show_window
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)
    
    @app.route("/toggle_window_tracking", methods=["POST"])
    def toggle_window_tracking():
        global show_window
        SETTINGS["window_tracking_enabled"] = not SETTINGS.get("window_tracking_enabled", False)
        show_window = SETTINGS["window_tracking_enabled"]
        SETTINGS["show_window"] = show_window
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"window_tracking_enabled": SETTINGS["window_tracking_enabled"]}), 200
    
    @app.route("/save_window_tracking_mode", methods=["POST"])
    def save_window_tracking_mode():
        data = request.get_json(force=True)
        mode = data.get("mode", "both")
        if mode in ["app", "browser", "both"]:
            SETTINGS["window_tracking_mode"] = mode
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200
    
    @app.route("/toggle_heartrate", methods=["POST"])
    def toggle_heartrate():
        global show_heartrate
        show_heartrate = not show_heartrate
        SETTINGS["show_heartrate"] = show_heartrate
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return ("", 204)
    
    @app.route("/toggle_heart_rate_enabled", methods=["POST"])
    def toggle_heart_rate_enabled():
        global show_heartrate
        SETTINGS["heart_rate_enabled"] = not SETTINGS.get("heart_rate_enabled", False)
        show_heartrate = SETTINGS["heart_rate_enabled"]
        SETTINGS["show_heartrate"] = show_heartrate
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"heart_rate_enabled": SETTINGS["heart_rate_enabled"]}), 200
    
    @app.route("/save_heart_rate_settings", methods=["POST"])
    def save_heart_rate_settings():
        data = request.get_json(force=True)
        SETTINGS["heart_rate_source"] = data.get("source", "pulsoid")
        SETTINGS["heart_rate_pulsoid_token"] = data.get("pulsoid_token", "")
        SETTINGS["heart_rate_hyperate_id"] = data.get("hyperate_id", "")
        SETTINGS["heart_rate_custom_api"] = data.get("custom_api", "")
        SETTINGS["heart_rate_update_interval"] = int(data.get("update_interval", 5))
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200
    
    @app.route("/save_emoji_settings", methods=["POST"])
    def save_emoji_settings():
        data = request.get_json(force=True)
        time_emoji = data.get("time_emoji", "⏰")
        song_emoji = data.get("song_emoji", "🎶")
        window_emoji = data.get("window_emoji", "💻")
        heartrate_emoji = data.get("heartrate_emoji", "❤️")
        
        SETTINGS["time_emoji"] = time_emoji[:5] if time_emoji else "⏰"
        SETTINGS["song_emoji"] = song_emoji[:5] if song_emoji else "🎶"
        SETTINGS["window_emoji"] = window_emoji[:5] if window_emoji else "💻"
        SETTINGS["heartrate_emoji"] = heartrate_emoji[:5] if heartrate_emoji else "❤️"
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200
    
    @app.route("/verify_patreon_supporter", methods=["POST"])
    def verify_patreon_supporter():
        import hashlib
        
        data = request.get_json(force=True)
        supporter_code = data.get("code", "").strip()
        
        if not supporter_code or len(supporter_code) < 10:
            return jsonify({"ok": False, "patreon_supporter": False, "message": "Invalid supporter code"}), 403
        
        try:
            parts = supporter_code.split('-')
            if len(parts) != 2:
                return jsonify({"ok": False, "patreon_supporter": False, "message": "Invalid code format"}), 403
            
            email_hash = parts[0]
            provided_signature = parts[1]
            
            secret_salt = "VRC_CHATBOX_2025_PATREON_SALT_v1"
            expected_signature = hashlib.sha256(f"{email_hash}{secret_salt}".encode()).hexdigest()[:16].upper()
            
            if provided_signature.upper() == expected_signature:
                SETTINGS["patreon_supporter"] = True
                SETTINGS["supporter_email_hash"] = email_hash
                with open(SETTINGS_FILE, "w") as f:
                    json.dump(SETTINGS, f, indent=4)
                return jsonify({"ok": True, "patreon_supporter": True, "message": "Supporter status activated!"}), 200
            else:
                return jsonify({"ok": False, "patreon_supporter": False, "message": "Invalid supporter code"}), 403
        except Exception:
            return jsonify({"ok": False, "patreon_supporter": False, "message": "Invalid code format"}), 403
    
    @app.route("/remove_patreon_supporter", methods=["POST"])
    def remove_patreon_supporter():
        SETTINGS["patreon_supporter"] = False
        if "supporter_code" in SETTINGS:
            del SETTINGS["supporter_code"]
        if "supporter_email_hash" in SETTINGS:
            del SETTINGS["supporter_email_hash"]
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"patreon_supporter": False}), 200
    
    @app.route("/save_premium_styling", methods=["POST"])
    def save_premium_styling():
        if not SETTINGS.get("patreon_supporter", False):
            return jsonify({"ok": False, "error": "Patreon supporter feature only"}), 403
        
        data = request.get_json(force=True)
        custom_background = data.get("custom_background", "")
        custom_button_color = data.get("custom_button_color", "")
        
        SETTINGS["custom_background"] = custom_background[:200] if custom_background else ""
        SETTINGS["custom_button_color"] = custom_button_color[:50] if custom_button_color else ""
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200

    @app.route("/save_settings", methods=["POST"])
    def save_settings():
        global client
        ip = request.form.get("quest_ip", SETTINGS.get("quest_ip"))
        port = int(request.form.get("quest_port", SETTINGS.get("quest_port")))
        osc_send_interval = int(request.form.get("osc_send_interval", SETTINGS.get("osc_send_interval", 3)))
        dashboard_update_interval = int(request.form.get("dashboard_update_interval", SETTINGS.get("dashboard_update_interval", 1)))
        timezone = request.form.get("timezone", SETTINGS.get("timezone"))
        spotify_id = request.form.get("spotify_client_id", SETTINGS.get("spotify_client_id"))
        spotify_secret = request.form.get("spotify_client_secret", SETTINGS.get("spotify_client_secret"))
        
        redirect_uri = f"{request.host_url}spotify-callback"

        SETTINGS.update({
            "quest_ip": ip,
            "quest_port": port,
            "osc_send_interval": osc_send_interval,
            "dashboard_update_interval": dashboard_update_interval,
            "timezone": timezone,
            "spotify_client_id": spotify_id,
            "spotify_client_secret": spotify_secret,
            "spotify_redirect_uri": redirect_uri
        })
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        client = make_client()
        spotify.init_spotify_web()
        return redirect("/")

    @app.route("/save_customs", methods=["POST"])
    def save_customs():
        text = request.form.get("customs", "").strip()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            lines = ["Custom Message Test"]
        SETTINGS["custom_texts"] = lines
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        nonlocal_vars_update_customs(lines)
        return redirect("/")

    @app.route("/update_custom_inline", methods=["POST"])
    def update_custom_inline():
        data = request.get_json(force=True)
        index = int(data.get("index", 0))
        new_text = data.get("text", "").strip()
        
        if 0 <= index < len(SETTINGS["custom_texts"]):
            SETTINGS["custom_texts"][index] = new_text
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f, indent=4)
            nonlocal_vars_update_customs(SETTINGS["custom_texts"])
            return jsonify({"ok": True}), 200
        return jsonify({"ok": False}), 400

    @app.route("/add_custom_message", methods=["POST"])
    def add_custom_message():
        data = request.get_json(force=True)
        new_text = data.get("text", "").strip()
        
        if new_text:
            SETTINGS["custom_texts"].append(new_text)
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f, indent=4)
            nonlocal_vars_update_customs(SETTINGS["custom_texts"])
            return jsonify({"ok": True}), 200
        return jsonify({"ok": False}), 400

    @app.route("/delete_custom_message", methods=["POST"])
    def delete_custom_message():
        data = request.get_json(force=True)
        index = int(data.get("index", 0))
        
        if 0 <= index < len(SETTINGS["custom_texts"]):
            SETTINGS["custom_texts"].pop(index)
            if not SETTINGS["custom_texts"]:
                SETTINGS["custom_texts"] = ["Custom Message Test"]
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f, indent=4)
            nonlocal_vars_update_customs(SETTINGS["custom_texts"])
            return jsonify({"ok": True}), 200
        return jsonify({"ok": False}), 400

    @app.route("/move_custom_message", methods=["POST"])
    def move_custom_message():
        data = request.get_json(force=True)
        index = int(data.get("index", 0))
        direction = data.get("direction", "up")
        
        messages = SETTINGS["custom_texts"]
        if direction == "up" and index > 0:
            messages[index], messages[index - 1] = messages[index - 1], messages[index]
        elif direction == "down" and index < len(messages) - 1:
            messages[index], messages[index + 1] = messages[index + 1], messages[index]
        else:
            return jsonify({"ok": False}), 400
        
        SETTINGS["custom_texts"] = messages
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        nonlocal_vars_update_customs(SETTINGS["custom_texts"])
        return jsonify({"ok": True}), 200

    @app.route("/set_message_weight", methods=["POST"])
    def set_message_weight():
        data = request.get_json(force=True)
        index = str(data.get("index", 0))
        weight = int(data.get("weight", 1))
        
        if "weighted_messages" not in SETTINGS:
            SETTINGS["weighted_messages"] = {}
        
        SETTINGS["weighted_messages"][index] = max(1, weight)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200

    def nonlocal_vars_update_customs(lines):
        global CUSTOM_TEXTS, current_custom_text, text_cycle_index
        CUSTOM_TEXTS = lines
        text_cycle_index = 0
        current_custom_text = CUSTOM_TEXTS[0] if CUSTOM_TEXTS else ""

    @app.route("/save_per_message_intervals", methods=["POST"])
    def save_per_message_intervals():
        data = request.get_json(force=True)
        intervals = data.get("intervals", {})
        SETTINGS["per_message_intervals"] = intervals
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200

    @app.route("/save_layout", methods=["POST"])
    def save_layout():
        data = request.get_json(force=True)
        layout = data.get("layout_order") or data.get("layout", SETTINGS.get("layout_order", ["time","custom","song","window","heartrate"]))
        allowed = {"time", "custom", "song", "window", "heartrate"}
        filtered = [p for p in layout if p in allowed]
        if not filtered:
            filtered = ["time", "custom", "song", "window", "heartrate"]
        SETTINGS["layout_order"] = filtered
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        return jsonify({"ok": True}), 200

    @app.route("/reset_settings", methods=["POST"])
    def reset_settings():
        global client, CUSTOM_TEXTS, current_custom_text, text_cycle_index
        
        from settings import DEFAULTS
        
        SETTINGS.clear()
        SETTINGS.update(DEFAULTS)
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=4)
        
        CUSTOM_TEXTS = DEFAULTS["custom_texts"]
        text_cycle_index = 0
        current_custom_text = CUSTOM_TEXTS[0]
        client = make_client()
        
        return jsonify({"ok": True}), 200

    @app.route("/download_settings", methods=["GET"])
    def download_settings():
        try:
            import os
            abs_path = os.path.abspath(SETTINGS_FILE)
            return send_file(
                abs_path,
                as_attachment=True,
                download_name=f"vrchat_chatbox_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mimetype='application/json'
            )
        except Exception as e:
            log_error("Failed to download settings", e)
            return jsonify({"error": str(e)}), 500

    @app.route("/upload_settings", methods=["POST"])
    def upload_settings():
        try:
            data = request.get_json(force=True)
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            from settings import DEFAULTS
            validated_settings = {}
            for key, default_value in DEFAULTS.items():
                if key in data:
                    validated_settings[key] = data[key]
                else:
                    validated_settings[key] = default_value
            
            SETTINGS.clear()
            SETTINGS.update(validated_settings)
            
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f, indent=4)
            
            global client, CUSTOM_TEXTS, current_custom_text, text_cycle_index
            CUSTOM_TEXTS = SETTINGS.get("custom_texts", [])
            text_cycle_index = 0
            current_custom_text = CUSTOM_TEXTS[0] if CUSTOM_TEXTS else "Custom Message Test"
            client = make_client()
            
            return jsonify({"ok": True}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/download_log", methods=["GET"])
    def download_log():
        if os.path.exists(ERROR_LOG_FILE):
            return send_file(ERROR_LOG_FILE, as_attachment=True, download_name=f"vrchat_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        return jsonify({"error": "No error log found"}), 404

    @app.route("/spotify-auth", methods=["GET"])
    def spotify_auth():
        if spotify.sp is None:
            spotify.init_spotify_web()
        
        if spotify.sp is None:
            return jsonify({"error": "Spotify not configured. Please add your Client ID and Secret in Settings."}), 400
        
        auth_manager = spotify.sp.auth_manager
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    @app.route("/spotify-callback")
    def spotify_callback():
        if spotify.sp is None:
            spotify.init_spotify_web()
        
        if spotify.sp is None:
            return "Spotify not configured. Please add your Client ID and Secret in Settings.", 400
        
        code = request.args.get('code')
        if code:
            auth_manager = spotify.sp.auth_manager
            auth_manager.get_access_token(code)
            return redirect("/?spotify=connected")
        
        return "Authorization failed", 400

    return app
