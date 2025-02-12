import os
import time
from flask import Flask, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

qr_code = None  # Variable global para almacenar el QR


def get_qr():
    global qr_code
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Inicia navegador en segundo plano
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")

        print("Esperando el código QR...")

        # Esperar hasta que aparezca la imagen del QR
        page.wait_for_selector("canvas", timeout=30000)  # Máx 30 seg

        # Tomar screenshot del QR
        os.makedirs("static", exist_ok=True)  # Asegurar que la carpeta está creada
        qr_path = "static/qr.png"
        page.locator("canvas").screenshot(path=qr_path)
        qr_code = qr_path

        print("Código QR capturado.")
        browser.close()


@app.route("/")
def index():
    if qr_code is None:
        return "<h1>Generando código QR, espera unos segundos...</h1>"

    return render_template_string("""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Escanea el QR</title>
        </head>
        <body>
            <h1>Escanea el código QR para iniciar sesión en WhatsApp Web</h1>
            <img src="{{ qr }}" alt="Código QR">
            <p>Abre WhatsApp en tu celular y escanea el código para iniciar sesión.</p>
        </body>
        </html>
    """, qr=qr_code)


if __name__ == "__main__":
    get_qr()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
