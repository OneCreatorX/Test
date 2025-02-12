import os
import logging
from playwright.sync_api import sync_playwright
from whatsapp_webpy import WhatsApp
import qrcode

# Configurar logging para ver el QR en Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WhatsAppManager:
    def __init__(self):
        self.session_path = "session"
        self.client = None
        self.setup_directories()
        
    def setup_directories(self):
        if not os.path.exists(self.session_path):
            os.makedirs(self.session_path)

    def generate_qr(self, qr_data):
        """Genera y muestra el QR en terminal/logs"""
        qr = qrcode.QRCode()
        qr.add_data(qr_data)
        qr.print_ascii(tty=True)
        logging.info("\nScan este QR en WhatsApp ->")
        
    def start(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            self.client = WhatsApp(
                browser=browser,
                session_path=self.session_path,
                qr_callback=self.generate_qr
            )
            
            self.client.wait_for_login()
            logging.info("¡Sesión de WhatsApp iniciada exitosamente!")
            
            # Mantener la conexión activa
            self.client.wait_until_disconnected()

if __name__ == "__main__":
    manager = WhatsAppManager()
    manager.start()
