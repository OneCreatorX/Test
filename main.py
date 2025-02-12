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
        page.wait_for_selector("canvas", timeout=60000)
        page.locator("canvas").screenshot(path=qr_path)
        time.sleep(60)
        session_active = True
        browser.close()

@app.route("/")
def index():
    if not session_active:
        content = '<h1>Escanea el QR para iniciar sesión en WhatsApp Web</h1>'
        if os.path.exists(qr_path):
            content += '<img src="/static/qr.png" alt="QR Code">'
        else:
            content += '<p>Generando QR...</p>'
    else:
        content = '<h1>Sesión activa en WhatsApp Web</h1>'
    return render_template_string(content)

if __name__ == "__main__":
    threading.Thread(target=whatsapp_automation, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
