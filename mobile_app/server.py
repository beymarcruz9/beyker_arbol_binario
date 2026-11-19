"""
Servidor local para probar la aplicación móvil en tu PC y en tu celular (mismo Wi-Fi).
Ejecución:
  python server.py
"""

import http.server
import socket
import socketserver
import webbrowser
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita ser alcanzable realmente
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    local_ip = get_local_ip()
    url_local = f"http://localhost:{PORT}"
    url_mobile = f"http://{local_ip}:{PORT}"

    print("=" * 65)
    print(" 📱 SERVIDOR DE LA APLICACIÓN BEYKER (ÁRBOLES)")
    print("=" * 65)
    print(f"  ➜ En tu Computadora: {url_local}")
    print(f"  ➜ En tu Celular (conectado al mismo Wi-Fi): {url_mobile}")
    print("=" * 65)
    print(" Presiona Ctrl + C en cualquier momento para detener el servidor.\n")

    # Abrir navegador automáticamente
    try:
        webbrowser.open(url_local)
    except Exception:
        pass

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Servidor detenido.")

if __name__ == "__main__":
    start_server()
