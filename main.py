import os
import threading
import time
from flask import Flask, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'

# Variables globales para controlar el estado
qr_path = "static/qr.png"  # La imagen del QR se guardará aquí
session_active = False
test_message_sent = False

def whatsapp_automation():
    """
    Automatiza la apertura de WhatsApp Web, captura el QR,
    espera que el usuario se autentique y luego envía un mensaje de prueba.
    """
    global session_active, test_message_sent

    # Asegurarse de que exista la carpeta 'static'
    if not os.path.exists("static"):
        os.makedirs("static")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        print("Abriendo WhatsApp Web...")

        # Espera hasta que aparezca el QR (canvas)
        try:
            page.wait_for_selector("canvas", timeout=30000)
            page.locator("canvas").screenshot(path=qr_path)
            print("QR capturado y guardado en", qr_path)
        except Exception as e:
            print("Error al capturar el QR:", e)
            browser.close()
            return

        # Esperamos un tiempo para que el usuario escanee el QR.
        # (En un caso real, se debería detectar la ausencia del canvas o la aparición de un elemento propio de la sesión activa)
        print("Esperando 60 segundos para la autenticación...")
        time.sleep(60)
        session_active = True
        print("Sesión activa. Procediendo a enviar mensaje de prueba...")

        try:
            # Ejemplo: buscar y abrir un chat con el título "Test Chat"
            # Los selectores a continuación son referenciales; deberás adaptarlos.
            # 1. Hacer clic en el icono de búsqueda (este selector puede variar)
            page.click("div[title='Buscar o empezar un chat']")  
            time.sleep(2)
            # 2. Escribir "Test Chat" en el campo de búsqueda
            page.fill("div[contenteditable='true']", "Test Chat")
            time.sleep(2)
            # 3. Presionar Enter para abrir el chat
            page.keyboard.press("Enter")
            time.sleep(3)
            # 4. En el área de entrada de texto, escribir el mensaje
            page.fill("div[contenteditable='true'][data-tab]", "Mensaje de prueba automático")
            time.sleep(1)
            # 5. Presionar Enter para enviar el mensaje
            page.keyboard.press("Enter")
            test_message_sent = True
            print("Mensaje de prueba enviado.")
        except Exception as e:
            print("Error al enviar mensaje:", e)

        # Esperar un poco y cerrar el navegador
        time.sleep(10)
        browser.close()

@app.route("/")
def index():
    # Muestra el estado según si la sesión está activa y si se envió el mensaje
    if not session_active:
        msg = "Escanea el código QR para iniciar sesión en WhatsApp Web."
        qr_html = f'<img src="/static/qr.png" alt="QR Code">' if os.path.exists(qr_path) else "<p>Generando QR...</p>"
    else:
        msg = "Sesión activa en WhatsApp Web."
        qr_html = ""

    test_status = "Mensaje de prueba enviado." if test_message_sent else "Mensaje de prueba no enviado aún."
    
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
        <p>{{ test_status }}</p>
    </body>
    </html>
    """, msg=msg, qr_html=qr_html, test_status=test_status)

if __name__ == "__main__":
    # Inicia la automatización de WhatsApp en un hilo en segundo plano
    threading.Thread(target=whatsapp_automation, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
