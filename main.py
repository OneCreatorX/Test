import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>¡Bienvenido a Railway!</h1><p>Esta es una aplicación Flask simple desplegada en Railway.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
