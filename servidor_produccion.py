import os
from waitress import serve
from LuxuryMonsei.wsgi import application

if __name__ == '__main__':
    print("Iniciando el servidor de producción para MET-ATELIER en el puerto 8080...")
    print("Por favor, NO cierres esta ventana. Si se cierra, la página dejará de funcionar.")
    # Escuchar en todas las interfaces de red (0.0.0.0) en el puerto 8080 con 8 hilos
    serve(application, host='0.0.0.0', port=8080, threads=8)
