from django.contrib import admin
from .models import CONF_WEB, CATEGORIA, PRODUCTO, IMG_PRODUCTO, PEDIDO

admin.site.register(CONF_WEB)
admin.site.register(CATEGORIA)
admin.site.register(PRODUCTO)
admin.site.register(IMG_PRODUCTO)
admin.site.register(PEDIDO)
