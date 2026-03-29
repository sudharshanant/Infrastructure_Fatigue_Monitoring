from __future__ import annotations

import time
from urllib.error import URLError
from urllib.request import urlopen
from threading import Thread

import webview
from waitress import serve

from app import app

HOST = "127.0.0.1"
PORT = 5050
WINDOW_TITLE = "Infrastructure Fatigue Monitoring"
WINDOW_URL = f"http://{HOST}:{PORT}"

SPLASH_HTML = """
<!doctype html>
<html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Loading</title>
        <style>
            body {
                margin: 0;
                min-height: 100vh;
                display: grid;
                place-items: center;
                background: radial-gradient(circle at 20% 20%, #1f3f61 0%, #0f2235 60%, #091521 100%);
                color: #ecf3fb;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            }
            .card {
                width: min(520px, 88vw);
                border-radius: 18px;
                padding: 28px 30px;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.14);
                box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
            }
            h1 {
                margin: 0 0 10px 0;
                font-size: 1.3rem;
                font-weight: 700;
            }
            p {
                margin: 0 0 16px 0;
                opacity: 0.95;
            }
            .bar {
                width: 100%;
                height: 8px;
                border-radius: 999px;
                overflow: hidden;
                background: rgba(255, 255, 255, 0.16);
            }
            .bar > span {
                display: block;
                width: 35%;
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, #4ab0ff, #7ee9c7);
                animation: move 1.2s infinite ease-in-out;
            }
            @keyframes move {
                0% { transform: translateX(-120%); }
                100% { transform: translateX(320%); }
            }
        </style>
    </head>
    <body>
        <div class=\"card\">
            <h1>Infrastructure Fatigue Monitoring</h1>
            <p>Starting analytics engine and loading dashboard...</p>
            <div class=\"bar\"><span></span></div>
        </div>
    </body>
</html>
"""


def run_server() -> None:
    # Waitress is stable for embedding Flask inside a desktop host.
    serve(app, host=HOST, port=PORT, threads=6)


def wait_for_server(timeout_seconds: float = 20.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(WINDOW_URL, timeout=1.5) as response:
                if response.status < 500:
                    return True
        except (URLError, TimeoutError, OSError):
            pass
        time.sleep(0.2)
    return False


def open_dashboard() -> None:
    window = webview.windows[0]
    if wait_for_server():
        window.load_url(WINDOW_URL)
    else:
        window.load_html(
            "<h2 style='font-family:Segoe UI,sans-serif;padding:24px'>"
            "Unable to start local server. Please restart the app.</h2>"
        )


def main() -> None:
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    webview.create_window(
        WINDOW_TITLE,
        html=SPLASH_HTML,
        width=1280,
        height=840,
        min_size=(960, 640),
    )
    webview.start(open_dashboard)


if __name__ == "__main__":
    main()
