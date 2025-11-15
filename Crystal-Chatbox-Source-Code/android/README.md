# Android App Build Instructions

This folder contains everything you need to compile the Crystal Chatbox Dashboard into an Android APK for sideloading on Quest or Android devices.

## Prerequisites

### System Requirements
- **Linux** or **macOS** (or **Windows with WSL2**)
- Python 3.8 or higher
- At least 8GB RAM
- 10GB+ free disk space

### Required Software

1. **Install Buildozer**
   ```bash
   pip install buildozer
   ```

2. **Install Android SDK dependencies** (Linux/Ubuntu):
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   ```

3. **For macOS**:
   ```bash
   brew install autoconf automake libtool pkg-config
   brew install openssl
   ```

## Building the APK

### Step 1: Prepare the Environment

Navigate to the project root directory (parent of this `android` folder):
```bash
cd ..
```

### Step 2: Initialize Buildozer (First time only)

The `buildozer.spec` file is already configured in the root directory. If you need to customize it:
```bash
# Optional: edit buildozer.spec to change app name, version, permissions, etc.
nano buildozer.spec
```

### Step 3: Build Debug APK

```bash
buildozer android debug
```

This process will:
- Download Android SDK and NDK (first time only, ~2GB)
- Download Python-for-Android
- Compile all Python dependencies
- Package everything into an APK

**Note:** First build can take 30-60 minutes. Subsequent builds are much faster (5-10 minutes).

### Step 4: Build Release APK (For Production)

For a signed release build:

1. **Generate a keystore** (first time only):
   ```bash
   keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Build release APK**:
   ```bash
   buildozer android release
   ```

3. **Sign the APK**:
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/crystal_chatbox-*-release-unsigned.apk my-key-alias
   ```

4. **Align the APK**:
   ```bash
   zipalign -v 4 bin/crystal_chatbox-*-release-unsigned.apk bin/crystal_chatbox-release.apk
   ```

## Installing on Quest/Android Device

### Method 1: Using ADB (Command Line)

1. **Enable Developer Mode** on your Quest:
   - Open Meta Quest app on phone
   - Go to Menu → Devices → Select your headset
   - Enable Developer Mode

2. **Connect Quest via USB** and enable USB debugging when prompted

3. **Install APK**:
   ```bash
   adb install bin/crystal_chatbox-1.0.0-debug.apk
   ```

### Method 2: Using SideQuest (GUI)

1. Download and install [SideQuest](https://sidequestvr.com/)
2. Connect your Quest via USB
3. Enable Developer Mode (see Method 1)
4. Open SideQuest
5. Drag and drop the APK file onto SideQuest window
6. Follow on-screen instructions

### Method 3: Wireless ADB (Advanced)

1. Connect Quest via USB first
2. Enable wireless ADB:
   ```bash
   adb tcpip 5555
   adb connect YOUR_QUEST_IP:5555
   ```
3. Disconnect USB, install wirelessly:
   ```bash
   adb -s YOUR_QUEST_IP:5555 install bin/crystal_chatbox-1.0.0-debug.apk
   ```

## Finding Your APK

After building, your APK will be located at:
- **Debug**: `bin/crystal_chatbox-1.0.0-debug.apk`
- **Release**: `bin/crystal_chatbox-*-release.apk`

## Troubleshooting

### Build Fails with "SDK not found"
```bash
buildozer android clean
rm -rf .buildozer
buildozer android debug
```

### Build Fails with "NDK not found"
Edit `buildozer.spec` and set:
```ini
android.ndk = 25b
android.sdk = 31
```

### "Insufficient memory" errors
Increase swap space (Linux):
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Quest won't connect via ADB
- Ensure Developer Mode is enabled
- Disable and re-enable USB debugging on Quest
- Try different USB cable (must support data transfer)
- Check USB debugging authorization dialog in headset

### App crashes on launch
Check logs:
```bash
adb logcat | grep python
```

Common issues:
- Missing permissions in `buildozer.spec`
- Python dependencies not compatible with Android
- Network permissions not granted

## Customizing the Build

### Change App Name
Edit `buildozer.spec`:
```ini
title = Your App Name
```

### Change Package Name
```ini
package.name = your_app_name
package.domain = com.yourdomain
```

### Add Permissions
```ini
android.permissions = INTERNET,WAKE_LOCK,VIBRATE,ACCESS_NETWORK_STATE
```

### Change App Icon
1. Create a 512x512 PNG icon
2. Edit `buildozer.spec`:
```ini
icon.filename = %(source.dir)s/static/logo.png
```

### Enable Landscape Mode
```ini
orientation = landscape
```

## Testing on Device

1. **Launch the app** on Quest (found in "Unknown Sources" in app library)
2. **Configure VRChat OSC**:
   - Enter your Quest's IP address (find in Quest Network settings)
   - Or if running VRChat on PC, enter PC's local IP
3. **Test Spotify**: Use Quest's browser for OAuth if needed
4. **Window tracking**: Not available on Android
5. **Heart rate**: Works if you have Pulsoid/HypeRate account

## Performance Tips

- Disable window tracking (doesn't work on Android anyway)
- Use longer OSC send intervals (5-10 seconds) to save battery
- Close other apps to free memory
- Keep Quest plugged in for extended use

## File Structure

```
project-root/
├── android/                 # This folder (documentation only)
│   └── README.md           # This file
├── buildozer.spec          # Build configuration (DO NOT MOVE)
├── main.py                 # App entry point
├── routes.py               # Flask routes
├── static/                 # Web assets
├── templates/              # HTML templates
└── requirements.txt        # Python dependencies
```

**Important**: The `buildozer.spec` file must stay in the project root!

## Additional Resources

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Quest Developer Documentation](https://developer.oculus.com/documentation/native/android/mobile-intro/)

## Support

For build issues:
- Check [Buildozer GitHub Issues](https://github.com/kivy/buildozer/issues)
- Join the [Discord Community](https://discord.gg/3Qypg9vnEP)

For app-specific issues:
- Contact: Bxpq (Discord)
- Patreon: [patreon.com/Sapph1r3](https://patreon.com/Sapph1r3)
