# -*- coding: utf-8 -*-
"""
Servicio para la gestión del catálogo, configuración del sitio y renderizado.
"""
from modelos.models import CONF_WEB, CATEGORIA, PRODUCTO

def get_menu_config():
    """
    Obtiene la configuración activa de CONF_WEB.
    Si la base de datos está vacía, crea un registro por defecto para evitar caídas.
    """
    conf = CONF_WEB.objects.first()
    if not conf:
        conf = CONF_WEB.objects.create()
    return conf.renderJson()

def get_site_context():
    """
    Retorna el contexto necesario para renderizar la página principal de la tienda.
    """
    return {
        'CONF_WEB': get_menu_config(),
        'CATEGORIAS': CATEGORIA.objects.all(),
        'PRODUCTOS': PRODUCTO.objects.all(),
    }
