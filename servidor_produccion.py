# -*- coding: utf-8 -*-
"""
Punto de Entrada para el Servidor de Producción WSGI (Waitress).
Diseñado específicamente para despliegues estables en sistemas Windows.
"""
import os
import sys
from waitress import serve
from LuxuryMonsei.wsgi import application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    threads = int(os.environ.get('THREADS', 8))
    
    print("=" * 65)
    print(f"Iniciando servidor de produccion MET-ATELIER en http://{host}:{port}")
    print(f"Configuracion: {threads} hilos de atencion concurrente (Waitress WSGI)")
    print("IMPORTANTE: No cierres esta ventana para mantener el portal activo.")
    print("=" * 65)
    
    serve(application, host=host, port=port, threads=threads)
