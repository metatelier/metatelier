# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.template.loader import render_to_string

# Create your models here.
class CONF_WEB(models.Model):

    title_one = models.TextField(blank=True)
    sub_title = models.TextField(blank=True)
    hero_des = models.TextField(blank=True)
    text_scroll = models.TextField(blank=True)
    etiqueta_cat = models.TextField(blank=True)
    titulo_sec_catalogo = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    footer_sub = models.TextField(blank=True)
    atelier = models.TextField(blank=True)
    contacto = models.TextField(blank=True)
    copy = models.TextField(blank=True)
    quiet = models.TextField(blank=True)
    hero_titulo = models.TextField(blank=True)
    hero_desc_main = models.TextField(blank=True)
    
    # --- Nuevos Campos Dinámicos ---
    # SEO & Metadata
    meta_title = models.TextField(blank=True, default='MET | ATELIER - Pura Elegancia a la Moda.')
    meta_description = models.TextField(blank=True, default='MET | ATELIER - Pura Elegancia a la Moda.')
    
    # Footer Sections
    footer_col1_title = models.TextField(blank=True, default='Atelier')
    footer_col2_title = models.TextField(blank=True, default='Navegación')
    footer_col3_title = models.TextField(blank=True, default='Contacto')
    footer_link_inicio = models.TextField(blank=True, default='Inicio')
    footer_link_catalogo = models.TextField(blank=True, default='Catálogo')
    footer_link_concierge = models.TextField(blank=True, default='Concierge Private')
    
    # Cart & Modals
    txt_bolsa_vacia = models.TextField(blank=True, default='Tu bolsa de compras está vacía.')
    txt_subtotal = models.TextField(blank=True, default='Subtotal Estimado')
    txt_btn_comprar = models.TextField(blank=True, default='Solicitar Adquisición')
    txt_modal_detalle_titulo = models.TextField(blank=True, default='Detalle de la Pieza')
    txt_modal_badge = models.TextField(blank=True, default='Pieza Única de Atelier')
    txt_modal_checkout_titulo = models.TextField(blank=True, default='Solicitud de Adquisición')
    txt_modal_checkout_intro = models.TextField(blank=True, default='Ingresa tus datos de Concierge para coordinar la entrega privada de tus piezas seleccionadas.')
    
    # Typography Settings
    font_family_titles = models.TextField(blank=True, default="'Playfair Display', serif")
    font_family_base = models.TextField(blank=True, default="'Lato', sans-serif")
    base_font_size = models.TextField(blank=True, default="14px")

    admin_password = models.CharField(max_length=100, default='G89qpjksr**')

    def renderJson(self):
        return {
            'id' : self.id,
            'title_one' : self.title_one,
            'sub_title' : self.sub_title,
            'hero_des' : self.hero_des,
            'text_scroll' : self.text_scroll,
            'etiqueta_cat' : self.etiqueta_cat,
            'titulo_sec_catalogo' : self.titulo_sec_catalogo,
            'footer' : self.footer,
            'footer_sub' : self.footer_sub,
            'atelier' : self.atelier,
            'contacto' : self.contacto,
            'copy' : self.copy,
            'quiet' : self.quiet,
            'hero_titulo': self.hero_titulo,
            'hero_desc_main': self.hero_desc_main,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'footer_col1_title': self.footer_col1_title,
            'footer_col2_title': self.footer_col2_title,
            'footer_col3_title': self.footer_col3_title,
            'footer_link_inicio': self.footer_link_inicio,
            'footer_link_catalogo': self.footer_link_catalogo,
            'footer_link_concierge': self.footer_link_concierge,
            'txt_bolsa_vacia': self.txt_bolsa_vacia,
            'txt_subtotal': self.txt_subtotal,
            'txt_btn_comprar': self.txt_btn_comprar,
            'txt_modal_detalle_titulo': self.txt_modal_detalle_titulo,
            'txt_modal_badge': self.txt_modal_badge,
            'txt_modal_checkout_titulo': self.txt_modal_checkout_titulo,
            'txt_modal_checkout_intro': self.txt_modal_checkout_intro,
            'font_family_titles': self.font_family_titles,
            'font_family_base': self.font_family_base,
            'base_font_size': self.base_font_size
        }

    class Meta:
        verbose_name = "Configuracion WEB"
        verbose_name_plural = "Configuracion WEB"

    def __str__(self):
        return str(self.title_one)


class CATEGORIA(models.Model):
    name = models.TextField(blank=True)
    def renderJson(self):
        return {
            'id' : self.id,
            'name' : self.name,
        }

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return str(self.name)


class IMG_PRODUCTO(models.Model):
    imagen = models.ImageField(upload_to='productos/')

    def renderJson(self):
        return {
            'id' : self.id,
            'url' : self.imagen.url
        }

    class Meta:
        verbose_name = "IMG PRODUCTO"
        verbose_name_plural = "IMG PRODUCTO"
    def __str__(self):
        return str(self.imagen.url)


class PRODUCTO(models.Model):
    nombre = models.TextField(blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.TextField(blank=True)
    material = models.TextField(blank=True)
    dimensiones = models.TextField(blank=True)
    codigo_unico = models.CharField(max_length=50, unique=True, null=True, blank=True)
    agotado = models.BooleanField(default=False)
    categorias = models.ManyToManyField(CATEGORIA, related_name='categorias')
    imagenes = models.ManyToManyField(IMG_PRODUCTO, related_name='imagenes')

    def GetCategorias(self):
        resp = []
        for C in self.categorias.all():
            resp.append(C.renderJson())
        return resp

    def GetImagnes(self):
        resp = []
        for I in self.imagenes.all():
            resp.append(I.renderJson())
        return resp

    def renderJson(self):
        cats = self.GetCategorias()
        cat_name = cats[0]['name'] if len(cats) > 0 else ""
        return {
            'id' : self.id,
            'nombre' : self.nombre,
            'descripcion' : self.descripcion,
            'precio' : self.precio,
            'material' : self.material,
            'dimensiones' : self.dimensiones,
            'codigo_unico' : self.codigo_unico,
            'agotado' : self.agotado,
            'categoria' : cat_name,
            'categorias' : cats,
            'imagenes' : self.GetImagnes(),
        }

    class Meta:
        verbose_name = "PRODUCTO"
        verbose_name_plural = "PRODUCTOS"

    def __str__(self):
        return str(self.nombre)

class PEDIDO(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    cliente_nombre = models.TextField(blank=True)
    cliente_email = models.TextField(blank=True)
    cliente_telefono = models.TextField(blank=True)
    cliente_direccion = models.TextField(blank=True)
    items_json = models.TextField(blank=True)
    total = models.TextField(blank=True)
    estado = models.CharField(max_length=20, default='Pendiente')

    def renderJson(self):
        import json
        return {
            'id': self.id,
            'fecha': self.fecha.strftime("%Y-%m-%d %H:%M"),
            'cliente': {
                'nombre': self.cliente_nombre,
                'email': self.cliente_email,
                'telefono': self.cliente_telefono,
                'direccion': self.cliente_direccion,
            },
            'items': json.loads(self.items_json) if self.items_json else [],
            'total': self.total,
            'estado': self.estado
        }






