from flask import Flask, send_file
from playwright.sync_api import sync_playwright
import time

app = Flask(__name__)

@app.route('/')
def generate_qr():
    qr_path = "qr.png"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        try:
            page.wait_for_selector("canvas", timeout=60000)
            page.locator("canvas").screenshot(path=qr_path)
        except Exception as e:
            browser.close()
            return "Error al capturar el QR"

        browser.close()
    
    return send_file(qr_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
