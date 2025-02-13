import os
import asyncio
import base64
from flask import Flask, render_template_string
from playwright.async_api import async_playwright

app = Flask(__name__)

# Plantillas HTML para los distintos estados

HTML_QR = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Escanea el QR</title>
  </head>
  <body style="text-align: center; font-family: Arial, sans-serif;">
    <h1>Escanea el código QR con WhatsApp</h1>
    <img src="data:image/png;base64,{{ qr }}" alt="QR">
  </body>
</html>
"""

HTML_LOGGED = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Sesión iniciada</title>
  </head>
  <body style="text-align: center; font-family: Arial, sans-serif;">
    <h1>La sesión ya está iniciada</h1>
  </body>
</html>
"""

HTML_ERROR = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Error</title>
  </head>
  <body style="text-align: center; font-family: Arial, sans-serif;">
    <h1>Error al capturar el QR o iniciar sesión</h1>
  </body>
</html>
"""

async def capture_qr_code():
    """
    Lanza un contexto persistente de Chromium para que, una vez escaneado el QR,
    la sesión se guarde en el directorio 'user_data'. Intenta:
      - Esperar el canvas que muestra el QR (15 segundos).
      - Si se encuentra, toma una captura del mismo y la devuelve.
      - Si no se encuentra el canvas, espera un elemento característico de la sesión iniciada (chat list).
    """
    user_data_dir = "./user_data"
    os.makedirs(user_data_dir, exist_ok=True)
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await browser.new_page()
            await page.goto("https://web.whatsapp.com")
            
            # Intenta esperar el canvas del QR (15 segundos)
            try:
                await page.wait_for_selector("canvas", timeout=15000)
                canvas = await page.query_selector("canvas")
                if canvas:
                    screenshot_bytes = await canvas.screenshot()
                    await browser.close()
                    return {"status": "qr", "data": base64.b64encode(screenshot_bytes).decode("utf-8")}
            except Exception as e:
                print("No se encontró el canvas del QR (posible sesión iniciada):", e)
            
            # Si no se encontró el canvas, intenta detectar que la sesión ya está iniciada.
            # Aquí se usa un selector representativo (por ejemplo, el de la lista de chats).
            try:
                await page.wait_for_selector("div[aria-label='Chat list']", timeout=5000)
                await browser.close()
                return {"status": "logged", "data": None}
            except Exception as e:
                print("No se detectó la lista de chats:", e)
                await browser.close()
                return {"status": "error", "data": None}
    except Exception as e:
        print("Error al iniciar el navegador:", e)
        return {"status": "error", "data": None}

@app.route("/")
def index():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(capture_qr_code())
    
    if result["status"] == "qr":
        return render_template_string(HTML_QR, qr=result["data"])
    elif result["status"] == "logged":
        return render_template_string(HTML_LOGGED)
    else:
        return render_template_string(HTML_ERROR)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
