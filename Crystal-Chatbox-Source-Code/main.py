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

try:
    import setproctitle
    setproctitle.setproctitle("Crystal Chatbox Dashboard")
except ImportError:
    pass

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

from routes import create_app

def start_server(app, host=None, port=5000):
    """Start Flask server"""
    if host is None:
        host = os.environ.get("HOST", "0.0.0.0")
    print(f"[Server] Starting Flask server at http://{host}:{port} ...")
    app.run(host=host, port=port, debug=False, use_reloader=False)

def start_gui(app, host="127.0.0.1", port=5000):
    """Start PyWebview GUI"""
    if not WEBVIEW_AVAILABLE:
        print("[GUI] PyWebview not available, falling back to server mode...")
        start_server(app, host=host, port=port)
        return
    
    server_thread = threading.Thread(target=start_server, args=(app, host, port), daemon=True)
    server_thread.start()

    print("[GUI] Waiting for server to start...")
    time.sleep(2)

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

    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    
    is_replit = os.environ.get("REPL_ID") or os.environ.get("REPLIT_DB_URL")
    
    if args.nogui or is_replit:
        start_server(app, port=port)
    else:
        start_gui(app, port=port)

if __name__ == "__main__":
    main()
