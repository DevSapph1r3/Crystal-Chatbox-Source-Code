from routes import create_app
from threading import Thread
import webbrowser

def open_browser():
    webbrowser.open("http://127.0.0.1:50555")

if __name__ == "__main__":
    app = create_app()

    Thread(target=open_browser).start()

    app.run(host="127.0.0.1", port=50555, debug=False)
