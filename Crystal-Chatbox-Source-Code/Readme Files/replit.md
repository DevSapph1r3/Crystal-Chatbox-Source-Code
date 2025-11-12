# Crystal Chatbox Dashboard

## Overview
Crystal Chatbox is a Flask-based web dashboard for VRChat OSC (Open Sound Control) integration. It allows users to display customizable chatbox messages in VRChat that can include:
- Current time (with timezone support)
- Custom rotating messages
- Spotify currently playing music
- Active window tracking (macOS feature)
- Heart rate monitoring (via Pulsoid, HypeRate, or custom API)

## Project Structure
- `main.py` - Application entry point
- `routes.py` - Flask routes and main application logic
- `settings.py` - Settings loader
- `settings.json` - User configuration file
- `spotify.py` - Spotify integration module
- `window_tracker.py` - Active window tracking (macOS only)
- `heart_rate_monitor.py` - Heart rate monitoring integration
- `templates/` - HTML templates for the web interface
- `static/` - CSS, JavaScript, and static assets

## Current State
The application has been successfully set up to run in the Replit environment with:
- Flask web server running on port 5000
- Dependencies installed via pip
- Workflow configured for automatic startup
- Deployment configured using Gunicorn for production

## Recent Changes (November 11, 2025)
- Moved all files from `Crystal-Chatbox-Source-Code/` subdirectory to root
- Updated `main.py` to run on `0.0.0.0:5000` (Replit compatible)
- Added automatic Replit environment detection
- Made PyWebview optional with graceful fallback
- Configured workflow for Flask application
- Configured deployment with Gunicorn for production
- **Removed ALL Windows-specific Spotify warnings** - Made cross-platform compatible (README + dashboard)
- **Added Spotify authorization button** - One-click OAuth flow next to Save Settings
- **Removed DEBUG print statements** - Cleaned up console spam (9 instances removed)
- **Created Android build folder** - Complete instructions in `android/README.md`
- **Added Ad integration guide** - Full setup documentation in `ADS_AND_PATREON_SETUP.md`
- **Verified ad-ready code** - A-Ads integration with Patreon supporter gating
- Updated README and dashboard with platform-agnostic Spotify instructions

## Configuration

### VRChat OSC Settings
Users need to configure their Quest or Desktop IP and port in the dashboard settings:
- Default OSC Port: 9000
- Quest or Desktop IP: Must be set to the VRChat device's IP address
  - For Quest: Use the Quest's network IP address
  - For Desktop VRChat: Use `127.0.0.1` (localhost)

### Spotify Integration (Optional)
To enable Spotify integration:
1. Create a Spotify Developer application at https://developer.spotify.com/dashboard
2. Add your Client ID and Client Secret in the Settings tab
3. Set the Redirect URI to match your Replit URL + `/spotify-callback`

### Window Tracking (macOS Only)
The window tracking feature uses AppleScript and is only available on macOS. On Replit (Linux), this feature will show "Unknown" as the window name.

### Heart Rate Monitoring (Optional)
Supports three sources:
- **Pulsoid**: Requires API token from https://pulsoid.net
- **HypeRate.io**: Requires session ID from https://hyperate.io
- **Custom API**: Any REST API that returns BPM data

## User Preferences
Settings are stored in `settings.json` and can be modified through the web dashboard. Key settings include:
- Custom messages list
- OSC send interval
- Layout order for chatbox elements
- Theme (dark/light)
- Module toggles (time, custom, music, window, heart rate)
- Emoji icons for each module

## Architecture
The application uses a multi-threaded architecture:
- **Main Thread**: Flask web server
- **Spotify Tracker Thread**: Polls Spotify API for currently playing track
- **Window Tracker Thread**: Monitors active window (macOS only)
- **Heart Rate Tracker Thread**: Polls heart rate API
- **VRChat Updater Thread**: Sends OSC messages to VRChat at configured intervals

## Dependencies
- Flask 3.0.0 - Web framework
- python-osc 1.8.3 - OSC protocol implementation
- spotipy - Spotify Web API wrapper
- gunicorn - Production WSGI server
- requests - HTTP library for API calls
- pytz - Timezone support
- pywinctl - Window tracking (Linux/macOS compatible library)

## Notes
- The application is designed for VRChat users who want dynamic chatbox messages
- OSC must be enabled in VRChat settings for the integration to work
- Some features (window tracking via AppleScript) are platform-specific and may not work in all environments
