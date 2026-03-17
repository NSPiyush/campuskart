from waitress import serve
from product.wsgi import application
import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

threading.Timer(2, open_browser).start()

serve(application, host="127.0.0.1", port=8000)