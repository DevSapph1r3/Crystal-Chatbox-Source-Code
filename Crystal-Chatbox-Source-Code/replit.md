# Crystal Chatbox Dashboard

## Overview
Crystal Chatbox is a Flask-based web dashboard for VRChat OSC (Open Sound Control) integration. It allows users to display customizable chatbox messages in VRChat that can include:
- Current time (with timezone support)
- Custom rotating messages with text effects (rainbow, sparkle, fire, ice, etc.)
- Spotify currently playing music with progress bar
- Active window tracking (desktop only, not available on Replit)
- Heart rate monitoring (via Pulsoid, HypeRate, or custom API)
- Weather information (via wttr.in)
- AI-generated messages (via OpenAI)
- Discord Rich Presence (desktop only)
- GitHub auto-updates with one-click update system
- Message profiles/presets for quick configuration switching

## Project Structure
- `main.py` - Application entry point with Replit detection
- `routes.py` - Flask routes and main application logic
- `settings.py` - Settings loader with default configuration
- `settings.json` - User configuration file (auto-generated on first run)
- `spotify.py` - Spotify integration module
- `window_tracker.py` - Active window tracking (desktop only)
- `heart_rate_monitor.py` - Heart rate monitoring integration
- `weather_service.py` - Weather integration via wttr.in
- `openai_client.py` - AI message generator using OpenAI API
- `profiles_manager.py` - Profile/preset management system
- `text_effects.py` - Custom text effects (rainbow, sparkle, fire, etc.)
- `discord_rpc.py` - Discord Rich Presence integration (desktop only)
- `github_updater.py` - Auto-update system with GitHub releases
- `version.txt` - Current application version
- `templates/` - HTML templates for the web interface
- `static/` - CSS, JavaScript, and static assets

## Current State
The application has been successfully set up to run in the Replit environment with:
- Flask web server running on port 5000 with host 0.0.0.0
- Python 3.12 installed (via Replit modules)
- All dependencies installed via pip (Flask 3.0.0, python-osc 1.8.3, spotipy, gunicorn, requests, pytz, setproctitle, pywinctl)
- Workflow configured for automatic startup with `--nogui` flag
- Deployment configured using Gunicorn for production autoscaling
- Module-level `app` variable exported in routes.py for Gunicorn compatibility
- All features tested and working correctly

## Recent Changes (November 12, 2025 - Major Feature Update)
### Initial Setup
- **Fresh GitHub Import** - Project imported and reorganized from subdirectory to root
- **Python .gitignore created** - Excludes cache files, virtual environments, settings.json, and logs
- **All dependencies installed** - Flask, python-osc, spotipy, gunicorn, requests, pytz, setproctitle, pywinctl, openai, pypresence
- **Workflow configured** - Runs `python main.py --nogui` on port 5000 with webview output
- **Deployment configured** - Uses Gunicorn with 2 workers for production autoscaling
- **Module-level app export** - Added `app = create_app()` to routes.py for Gunicorn compatibility

### New Features Added
1. **GitHub Auto-Update System** - One-click updates from GitHub releases with semantic version comparison
2. **AI Message Generator** - OpenAI integration for creative, context-aware message generation
3. **Weather Integration** - Real-time weather display using wttr.in (no API key needed)
4. **Profiles/Presets** - Save and load complete chatbox configurations
5. **Text Effects** - Rainbow, sparkle, fire, ice, hearts, stars, neon, wave, bounce, and more
6. **Discord Rich Presence** - Display Discord activity (desktop only)

### Bug Fixes & Improvements
- Fixed JSON serialization errors in /status endpoint (datetime to ISO string)
- Added proper thread management (only start threads when features are enabled)
- Fixed semantic version comparison using packaging.version.parse()
- Added comprehensive error handling throughout all new features
- Reorganized UI with professional section headers (removed excessive emojis)
- Added visual separation between settings sections

## Configuration

### VRChat OSC Settings
Users need to configure their Quest or Desktop IP and port in the dashboard settings:
- **Default OSC Port**: 9000
- **Quest or Desktop IP**: Must be set to the VRChat device's IP address
  - For Quest: Use the Quest's network IP address (find in Quest Settings > Wi-Fi)
  - For Desktop VRChat: Use `127.0.0.1` (localhost)

### Spotify Integration (Optional)
To enable Spotify integration:
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy your **Client ID** and **Client Secret**
4. Set the **Redirect URI** to your Replit URL + `/spotify-callback`
   - Example: `https://your-repl-name.your-username.repl.co/spotify-callback`
5. Enter credentials in the dashboard Settings tab
6. Click the Spotify authorization button to connect your account

**Note**: Use the full Replit domain URL for the redirect URI, not `127.0.0.1` or `localhost`

### Window Tracking
✅ **Now Cross-Platform** - Window tracking now uses the pywinctl library for Windows, macOS, and Linux support. It shows your currently active application and browser tab titles.

**Note:** On Replit (cloud environment), this feature will show "Unknown" since there's no graphical desktop. On local installations (Windows/Mac/Linux), it works perfectly!

### Heart Rate Monitoring (Optional)
Supports three sources:
- **Pulsoid**: Get API token from [pulsoid.net/ui/keys](https://pulsoid.net/ui/keys)
- **HypeRate.io**: Get session ID from [hyperate.io](https://hyperate.io)
- **Custom API**: Any REST API that returns `bpm`, `heart_rate`, or `hr` field

Configure in the Advanced tab of the dashboard.

### Weather Integration (Optional)
Display current weather in your chatbox:
- Uses wttr.in API (no API key required)
- Supports location by name or "auto" for automatic detection
- Shows temperature and weather emoji
- Configure location in Advanced tab

### AI Message Generator (Optional)
Generate creative messages using OpenAI:
- Requires OPENAI_API_KEY environment variable
- Multiple moods: funny, wholesome, mysterious, energetic, chill, chaotic, philosophical, sarcastic
- Custom theme support
- Configurable max length
- Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)

### Text Effects
Apply visual effects to your chatbox messages:
- **Rainbow** 🌈 - Rotating rainbow emoji
- **Sparkle** ✨ - Twinkling stars
- **Fire** 🔥 - Animated flames
- **Ice** ❄️ - Frozen snowflakes
- **Hearts** 💖 - Pulsing hearts
- **Stars** ⭐ - Shooting stars
- **Neon** 💡 - Glowing effect
- **Wave** 🌊 - Wave animation
- **Bounce** ⬆️⬇️ - Bouncing text
- **None** - No effect (default)

### Profiles/Presets
Save and load complete chatbox configurations:
- Save current settings as named profiles
- Load profiles to instantly switch configurations
- Includes all module states, emojis, layout order, and custom messages
- Perfect for different moods or occasions

### GitHub Auto-Update
Keep your app up to date automatically:
- Check for updates with one click
- View release notes before updating
- Semantic version comparison (1.10.0 > 1.2.0 works correctly)
- Update info shown in Advanced tab

### Discord Integration (Desktop Only)
Display Discord Rich Presence information:
- Shows current Discord activity
- Includes status and custom status messages
- Only works on local installations with Discord running
- Not available in Replit cloud environment

## Usage

### Getting Started
1. **Open the web preview** - The application is automatically running on port 5000
2. **Configure VRChat connection** - Set your Quest or Desktop IP in Settings
3. **Enable desired modules** - Toggle on Time, Custom Messages, Music, etc.
4. **Toggle Chatbox ON** - Start sending messages to VRChat
5. **Test connection** - Use the "Test Connection" button to verify OSC is working

### Custom Messages
- Add multiple rotating messages in the Settings tab
- Messages rotate at configurable intervals (default: 3 seconds)
- Supports variables: `{time}` and `{song}`
- Can set individual timing per message
- Supports weighted randomization for message frequency

### Layout Customization
- Drag and drop to reorder chatbox elements
- Customize emojis for each module (time, music, window, heart rate)
- Choose between dark/light themes
- Enable compact mode for minimal UI
- Enable streamer mode to hide sensitive information

## Security & Best Practices

### Secret Management
⚠️ **Important**: The `settings.json` file stores configuration including Spotify tokens in plaintext. For better security:
- Consider using Replit Secrets for sensitive API keys
- The `.gitignore` file excludes `settings.json` to prevent committing secrets
- Spotify tokens are cached in `.spotify_cache` (also gitignored)

### Production Deployment
When publishing to production:
- The app uses Gunicorn for production-grade serving
- Configured for autoscaling (scales down when idle)
- Binds to 0.0.0.0:5000 for proper Replit routing

## Architecture

### Multi-Threaded Design
The application uses background threads for async operations:
- **Main Thread**: Flask web server handling HTTP requests
- **Spotify Tracker Thread**: Polls Spotify API every 1 second for currently playing track
- **Window Tracker Thread**: Monitors active window (desktop only)
- **Heart Rate Tracker Thread**: Polls heart rate API at configured interval
- **VRChat Updater Thread**: Sends OSC messages to VRChat at configured intervals (default: 3 seconds)

### Request Flow
1. User configures settings via web dashboard
2. Settings saved to `settings.json`
3. Background threads read settings and gather data (time, music, etc.)
4. VRChat Updater thread composes messages based on layout order
5. OSC messages sent to VRChat using python-osc library

## Dependencies
Core packages (installed):
- **Flask 3.0.0** - Web framework
- **python-osc 1.8.3** - OSC protocol implementation for VRChat
- **spotipy** - Spotify Web API wrapper with OAuth support
- **gunicorn** - Production WSGI server
- **requests** - HTTP library for API calls (heart rate, etc.)
- **pytz** - Timezone support for clock feature

Cross-platform packages (installed):
- **pywinctl** - Window tracking library (Windows/macOS/Linux support)
- **setproctitle** - Sets process title in Activity Monitor/Task Manager
- **openai** - OpenAI API client for AI message generation
- **pypresence** - Discord Rich Presence integration
- **packaging** - Semantic version parsing for GitHub updater

Desktop-only packages (removed for Replit):
- **pywebview** - Desktop GUI wrapper (not needed with `--nogui` flag)

## Troubleshooting

### VRChat Not Receiving Messages
- Verify VRChat OSC is enabled in VRChat settings (Settings > OSC)
- Check that the IP address is correct
- For Quest: Use Quest's network IP, not 127.0.0.1
- For Desktop: Use 127.0.0.1
- Test connection with the "Test Connection" button
- Ensure port 9000 is not blocked by firewall

### Spotify Not Working
- Ensure redirect URI matches your Replit domain exactly
- Include `/spotify-callback` at the end
- Use HTTPS for production Replit URLs
- Check that Client ID and Secret are entered correctly
- Click the Spotify authorization button after saving credentials

### Settings Not Saving
- Check browser console for errors
- Ensure you have write permissions (should work by default)
- Settings are stored in `settings.json` in the root directory
- The file is auto-created on first run

## Platform Limitations on Replit
- **Window Tracking**: Does not work (requires desktop environment)
- **Discord Rich Presence**: Does not work (requires Discord desktop app)
- **GUI Mode**: Not available (runs in `--nogui` mode automatically)
- **Local File Access**: Limited to Replit workspace

## Features That Work on Replit
- ✅ Time display with timezone support
- ✅ Custom rotating messages
- ✅ Spotify music integration
- ✅ Heart rate monitoring
- ✅ Weather integration
- ✅ AI message generator (requires OpenAI API key)
- ✅ Text effects
- ✅ Profiles/presets
- ✅ GitHub auto-updates
- ✅ Music progress bar
- ❌ Window tracking (desktop only)
- ❌ Discord Rich Presence (desktop only)

## User Preferences
None currently documented. Settings are managed through the web dashboard and persist in `settings.json`.

## Notes
- Designed for VRChat users who want dynamic chatbox messages
- OSC must be enabled in VRChat for the integration to work
- Main.py automatically detects Replit environment and disables GUI mode
- Some features are platform-specific and may not work in cloud environments
- The app is cross-platform compatible for core features (time, custom messages, Spotify, heart rate)
