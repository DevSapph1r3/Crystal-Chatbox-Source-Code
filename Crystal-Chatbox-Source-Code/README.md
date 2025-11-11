# Crystal Chatbox Dashboard

A powerful VRChat OSC integration dashboard for displaying dynamic chatbox messages with Spotify, time, custom messages, window tracking, and heart rate monitoring.

## Features

- 🕐 **Real-time Clock** with timezone support
- 💬 **Custom Rotating Messages** with weighted randomization
- 🎵 **Spotify Integration** - Show currently playing music
- 💻 **Window Tracking** - Display your active application (Windows/macOS/Linux)
- ❤️ **Heart Rate Monitoring** - Via Pulsoid, HypeRate, or custom API
- 🎨 **Customizable** - Themes, emojis, layouts, and more
- 📱 **Cross-Platform** - Desktop (Windows/Mac/Linux) and Android

## Installation

### Desktop (Windows, macOS, Linux)

1. **Install Python 3.11 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   
   **GUI Mode (Recommended):**
   ```bash
   python gui_launcher.py
   ```
   
   **Web Browser Mode:**
   ```bash
   python main.py
   ```
   Then open `http://127.0.0.1:5000` in your browser

### Android (Quest Sideloading)

1. **Install Buildozer** (Linux/macOS or WSL on Windows)
   ```bash
   pip install buildozer
   ```

2. **Build APK**
   ```bash
   buildozer android debug
   ```

3. **Install on Quest**
   - Connect Quest via USB
   - Enable Developer Mode on Quest
   - Install APK using SideQuest or adb:
   ```bash
   adb install bin/crystal_chatbox-1.0.0-debug.apk
   ```

## Configuration

### VRChat OSC Settings

1. Open the dashboard
2. Go to **Settings** tab
3. Enter your **Quest or Desktop IP address**
   - For Quest: Find IP in Quest Network settings
   - For Desktop VRChat: Use `127.0.0.1` (localhost)
4. Default port is `9000` (VRChat OSC port)

### Spotify Integration (Optional)

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy **Client ID** and **Client Secret**
4. Add redirect URI:
   - Desktop: `http://127.0.0.1:5000/spotify-callback`
   - Or match your app's URL
5. Paste credentials in the dashboard **Settings** tab

**⚠️ Important for Windows:** Always use `127.0.0.1` instead of `localhost` in your Spotify app settings.

### Window Tracking

- **Windows/Mac/Linux:** Automatically tracks active window and browser tabs
- Works in desktop mode only
- Enable in the **Advanced** tab

### Heart Rate Monitoring

Supports three sources:
- **Pulsoid:** Get API token from [pulsoid.net](https://pulsoid.net/ui/keys)
- **HypeRate.io:** Get session ID from [hyperate.io](https://hyperate.io)
- **Custom API:** Any REST API returning `bpm`, `heart_rate`, or `hr` field

Configure in the **Advanced** tab.

## Usage

1. **Launch the application** (GUI or web mode)
2. **Configure your settings** (IP, port, Spotify, etc.)
3. **Enable modules** you want to display (Time, Custom, Music, etc.)
4. **Toggle Chatbox ON** to start sending to VRChat
5. **Customize layout** by dragging items in the layout list

## Advanced Features

### Custom Messages
- Add multiple rotating messages
- Set individual timing per message
- Weighted randomization for message frequency
- Variable support: `{time}`, `{song}`

### Layout Customization
- Drag and drop to reorder elements
- Per-module emoji customization
- Dark/Light theme support
- Compact mode for minimal UI

### Patreon Supporters
- Ad-free experience
- Premium customization options
- Custom backgrounds and button colors
- Support development: [patreon.com/Sapph1r3](https://patreon.com/Sapph1r3)

## Troubleshooting

### Spotify Not Working on Windows
- Use `http://127.0.0.1:5000/spotify-callback` as redirect URI
- Never use `localhost` in Spotify settings
- Ensure credentials are correct in dashboard

### Download Settings Not Working
- Make sure popup blockers are disabled
- Try right-click → Save As
- Check file permissions

### VRChat Not Receiving Messages
- Verify VRChat OSC is enabled in settings
- Check IP address is correct (Quest IP or `127.0.0.1`)
- Test connection with "Test Connection" button
- Ensure port 9000 is not blocked by firewall

### Window Tracking Shows "Unknown"
- Only works in desktop mode (not on Replit)
- Requires local machine installation
- May need permissions on macOS/Linux

## Development

### Running from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py

# Run GUI mode
python gui_launcher.py
```

### Building for Android
```bash
# Initialize buildozer
buildozer init

# Build debug APK
buildozer android debug

# Build release APK (requires signing)
buildozer android release
```

## Credits

**Developer:** Sapph1r3
- VRChat: [Sapph1r3](https://vrchat.com/home/user/usr_d5b25d37-63ff-45b8-9a4a-9a0a1f6e05b0)
- Discord: Bxpq
- Patreon: [patreon.com/Sapph1r3](https://patreon.com/Sapph1r3)

## License

This project is provided as-is for personal use.

## Support

- 🌐 [Community Discord Server](https://discord.gg/3Qypg9vnEP)
- ❤️ [Support on Patreon](https://patreon.com/Sapph1r3)
