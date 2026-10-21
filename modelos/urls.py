# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import include, path
from .views import *

urlpatterns = [
    path('', Index.as_view() , name='index'),
    path('api/productos', api_productos, name='api_productos'),
    path('api/productos/<int:pid>', api_productos_detail, name='api_productos_detail'),
    path('api/textos', api_textos, name='api_textos'),
    path('api/pedidos', api_pedidos, name='api_pedidos'),
    path('api/pedidos/<int:pid>', api_pedidos_detail, name='api_pedidos_detail'),
    path('api/admin/login', api_admin_login, name='api_admin_login'),
    path('api/git/backup', api_git_backup, name='api_git_backup'),
    path('api/git/versions', api_git_versions, name='api_git_versions'),
    path('api/git/restore', api_git_restore, name='api_git_restore'),
]

app_name = "modelos"
