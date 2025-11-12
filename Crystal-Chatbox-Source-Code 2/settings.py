import json
import os

SETTINGS_FILE = "settings.json"

DEFAULTS = {
    "quest_ip": "",
    "quest_port": 9000,
    "spotify_client_id": "",
    "spotify_client_secret": "",
    "spotify_redirect_uri": "",
    "custom_texts": ["Custom Message Test"],
    "refresh_interval": 3,
    "osc_send_interval": 3,
    "dashboard_update_interval": 1,
    "per_message_intervals": {},
    "music_progress": True,
    "progress_style": "bar",
    "timezone": "local",
    "layout_order": ["time", "custom", "song", "window", "heartrate"],
    "theme": "dark",
    "random_order": False,
    "weighted_messages": {},
    "show_module_icons": True,
    "streamer_mode": False,
    "compact_mode": False,
    "error_log_enabled": True,
    "message_queue_preview_count": 3,
    "chatbox_visible": False,
    "show_time": True,
    "show_custom": True,
    "show_music": True,
    "show_window": False,
    "show_heartrate": False,
    "window_tracking_enabled": False,
    "window_tracking_interval": 2,
    "window_tracking_mode": "both",
    "heart_rate_enabled": False,
    "heart_rate_source": "pulsoid",
    "heart_rate_pulsoid_token": "",
    "heart_rate_hyperate_id": "",
    "heart_rate_custom_api": "",
    "heart_rate_update_interval": 5,
    "time_emoji": "⏰",
    "song_emoji": "🎶",
    "window_emoji": "💻",
    "heartrate_emoji": "❤️",
    "patreon_supporter": False,
    "custom_background": "",
    "custom_button_color": ""
}

if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, "r") as f:
            SETTINGS = json.load(f)
    except:
        SETTINGS = DEFAULTS.copy()
else:
    SETTINGS = DEFAULTS.copy()

for k, v in DEFAULTS.items():
    if k not in SETTINGS:
        SETTINGS[k] = v

with open(SETTINGS_FILE, "w") as f:
    json.dump(SETTINGS, f, indent=4)
