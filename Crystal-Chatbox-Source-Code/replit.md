# Crystal Chatbox Dashboard

## Overview
Crystal Chatbox is a Flask-based web dashboard for VRChat OSC (Open Sound Control) integration. It allows users to display customizable chatbox messages in VRChat that can include:
- Current time (with timezone support)
- Custom rotating messages
- Spotify currently playing music
- Active window tracking (desktop only, not available on Replit)
- Heart rate monitoring (via Pulsoid, HypeRate, or custom API)

## Project Structure
- `main.py` - Application entry point with Replit detection
- `routes.py` - Flask routes and main application logic
- `settings.py` - Settings loader with default configuration
- `settings.json` - User configuration file (auto-generated on first run)
- `spotify.py` - Spotify integration module
- `window_tracker.py` - Active window tracking (desktop only)
- `heart_rate_monitor.py` - Heart rate monitoring integration
- `templates/` - HTML templates for the web interface
- `static/` - CSS, JavaScript, and static assets

## Current State
The application has been successfully set up to run in the Replit environment with:
- Flask web server running on port 5000 with host 0.0.0.0
- Python 3.11 installed
- Dependencies installed via pip (Flask, python-osc, spotipy, gunicorn, requests, pytz)
- Workflow configured for automatic startup with `--nogui` flag
- Deployment configured using Gunicorn for production
- Platform-specific packages (pywinctl, pywebview) removed for cloud compatibility

## Recent Changes (November 12, 2025)
- **Imported from GitHub** - Fresh project setup in Replit environment
- **Files reorganized** - Moved all files from subdirectory to root
- **Requirements cleaned** - Removed duplicate entries and desktop-only packages (pywebview)
- **Python .gitignore added** - Excludes cache files, virtual environments, settings.json, and logs
- **Workflow configured** - Runs `python main.py --nogui` on port 5000
- **Deployment configured** - Uses Gunicorn for production autoscaling
- **Dependencies installed** - All core packages ready to use

### Cross-Platform Improvements (November 12, 2025)
- **Process Title Fixed** - Added setproctitle library so Activity Monitor/Task Manager shows "Crystal Chatbox Dashboard" instead of "Python"
- **Window Tracker Made Cross-Platform** - Replaced Mac-only AppleScript with pywinctl library for Windows/macOS/Linux support
- **Download Buttons Fixed** - Improved file download functionality with better headers for Windows compatibility
- **Spotify OAuth Clarified** - Dashboard now displays exact redirect URI to copy to Spotify Developer settings
- **Heart Rate Monitor Verified** - Confirmed Pulsoid, HypeRate, and custom API support working correctly

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
- **GUI Mode**: Not available (runs in `--nogui` mode automatically)
- **Local File Access**: Limited to Replit workspace

## User Preferences
None currently documented. Settings are managed through the web dashboard and persist in `settings.json`.

## Notes
- Designed for VRChat users who want dynamic chatbox messages
- OSC must be enabled in VRChat for the integration to work
- Main.py automatically detects Replit environment and disables GUI mode
- Some features are platform-specific and may not work in cloud environments
- The app is cross-platform compatible for core features (time, custom messages, Spotify, heart rate)
