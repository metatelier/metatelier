# -*- coding: utf-8 -*-
"""
Capa de Controladores / Vistas para la aplicación modelos.
Re-exporta todas las vistas para mantener retrocompatibilidad total con las URLs existentes.
"""
from modelos.views.web_views import Index
from modelos.views.api_auth import _is_admin, api_admin_login
from modelos.views.api_catalog import api_productos, api_productos_detail, api_textos
from modelos.views.api_orders import api_pedidos, api_pedidos_detail
from modelos.views.api_git import api_git_backup, api_git_versions, api_git_restore

__all__ = [
    'Index',
    '_is_admin',
    'api_admin_login',
    'api_productos',
    'api_productos_detail',
    'api_textos',
    'api_pedidos',
    'api_pedidos_detail',
    'api_git_backup',
    'api_git_versions',
    'api_git_restore',
]
