#!/usr/bin/env python3
"""
Crystal Chatbox Launcher
Runs Flask app and optionally launches a PyWebview GUI.
"""
import threading
import time
import sys
import os
import argparse
import webview
from routes import create_app

def start_server(app, host="127.0.0.1", port=5000):
    """Start Flask server"""
    print(f"[Server] Starting Flask server at http://{host}:{port} ...")
    app.run(host=host, port=port, debug=False, use_reloader=False)

def start_gui(app, host="127.0.0.1", port=5000):
    """Start PyWebview GUI"""
    # Start server in a background thread
    server_thread = threading.Thread(target=start_server, args=(app, host, port), daemon=True)
    server_thread.start()

    # Wait a moment for server to start
    print("[GUI] Waiting for server to start...")
    time.sleep(2)

    # Create GUI window
    print("[GUI] Launching PyWebview window...")
    window = webview.create_window(
        title="Crystal Chatbox Dashboard",
        url=f"http://{host}:{port}",
        width=1200,
        height=800,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        background_color="#0d0d0d"
    )

    webview.start(debug=False)
    print("[GUI] Application closed.")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Launch Crystal Chatbox.")
    parser.add_argument("--nogui", action="store_true", help="Run server only, without GUI.")
    args = parser.parse_args()

    # Create Flask app
    app = create_app()
    port = int(os.environ.get("PORT", 5000))

    if args.nogui:
        # Just run Flask server
        start_server(app, port=port)
    else:
        # Launch GUI + server
        start_gui(app, port=port)

if __name__ == "__main__":
    main()
