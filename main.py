import os
import asyncio
import base64
from flask import Flask, render_template_string
from playwright.async_api import async_playwright

app = Flask(__name__)

# Plantilla HTML para mostrar el QR
HTML_TEMPLATE = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>WhatsApp Web - Escanea el QR</title>
  </head>
  <body style="text-align: center; font-family: Arial, sans-serif;">
    <h1>Escanea el código QR con tu WhatsApp</h1>
    {% if qr_img %}
      <img src="data:image/png;base64,{{ qr_img }}" alt="Código QR">
    {% else %}
      <p>No se pudo generar el código QR.</p>
    {% endif %}
  </body>
</html>
"""

async def capture_qr_code():
    """
    Utiliza Playwright para abrir WhatsApp Web, esperar a que se muestre el código QR
    (se asume que se renderiza en un elemento <canvas>) y capturarlo como imagen.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await browser.new_page()
            # Navegar a WhatsApp Web
            await page.goto("https://web.whatsapp.com")
            # Esperar hasta 15 segundos a que aparezca algún elemento <canvas>
            await page.wait_for_selector("canvas", timeout=15000)
            # Seleccionar el primer canvas (el QR debería estar ahí)
            canvas = await page.query_selector("canvas")
            if not canvas:
                await browser.close()
                return None
            # Tomar una captura del elemento
            screenshot_bytes = await canvas.screenshot()
            await browser.close()
            # Convertir la imagen a base64 para poder incrustarla en HTML
            return base64.b64encode(screenshot_bytes).decode("utf-8")
    except Exception as e:
        print("Error al capturar el QR:", e)
        return None

@app.route("/")
def index():
    # Crear un nuevo loop de eventos para ejecutar la función asíncrona
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        qr_img = loop.run_until_complete(capture_qr_code())
    except Exception as e:
        print("Error en la generación del QR:", e)
        qr_img = None
    return render_template_string(HTML_TEMPLATE, qr_img=qr_img)

if __name__ == "__main__":
    # En Railway el puerto se establece en la variable de entorno PORT
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
