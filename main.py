import os
import threading
import time
from flask import Flask, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)
qr_path = "static/qr.png"
session_active = False

def whatsapp_automation():
    global session_active
    if not os.path.exists("static"):
        os.makedirs("static")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        try:
            page.wait_for_selector("canvas", timeout=60000)
            page.locator("canvas").screenshot(path=qr_path)
        except Exception as e:
            browser.close()
            return
        time.sleep(60)
        session_active = True
        browser.close()

@app.route("/")
def index():
    if not session_active:
        msg = "Escanea el código QR para iniciar sesión en WhatsApp Web."
        qr_html = f'<img src="/static/qr.png" alt="QR Code">' if os.path.exists(qr_path) else "<p>Generando QR...</p>"
    else:
        msg = "Sesión activa en WhatsApp Web."
        qr_html = ""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Autenticación WhatsApp Web</title>
    </head>
    <body>
        <h1>{{ msg }}</h1>
        {{ qr_html|safe }}
    </body>
    </html>
    """, msg=msg, qr_html=qr_html)

if __name__ == "__main__":
    threading.Thread(target=whatsapp_automation, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
