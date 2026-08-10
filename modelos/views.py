# -*- coding: utf-8 -*-
import os , json
from base64 import b64decode
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect , HttpResponse
from django.conf import settings as _settings
from django.views.generic import TemplateView
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from datetime import datetime, date, time, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import *
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

def GetMenu():
    return CONF_WEB.objects.all()[0].renderJson()

class Index(TemplateView):
    template_name = "index.html"
    def get(self, request, *args, **kwargs):
        if 'admin' in request.GET:
            return HttpResponseRedirect('/')
            
        DATA = {
            'CONF_WEB' : GetMenu(),
            'CATEGORIAS' : CATEGORIA.objects.all(),
            'PRODUCTOS' : PRODUCTO.objects.all(),
        }
        return render(request , self.template_name , DATA)

def _is_admin(request):
    pin = request.headers.get('x-admin-pin', '')
    conf = CONF_WEB.objects.first()
    valid_pin = conf.admin_password if conf and conf.admin_password else 'G89qpjksr**'
    return pin == valid_pin

@csrf_exempt
def api_productos(request):
    from django.http import JsonResponse
    if request.method == 'GET':
        prods = [p.renderJson() for p in PRODUCTO.objects.all()]
        return JsonResponse(prods, safe=False)
        
    if request.method == 'POST':
        if not _is_admin(request):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
            
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio', '')
        material = request.POST.get('material', '')
        dimensiones = request.POST.get('dimensiones', '')
        codigo_unico = request.POST.get('codigo_unico', '').strip()
        if not codigo_unico:
            import uuid
            codigo_unico = f"MET-A-{uuid.uuid4().hex[:6].upper()}"
        agotado = request.POST.get('agotado', 'false').lower() == 'true'
        
        producto = PRODUCTO.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            material=material,
            dimensiones=dimensiones,
            codigo_unico=codigo_unico,
            agotado=agotado
        )
        
        cats_str = request.POST.get('categoria', '')
        if cats_str:
            for cat_name in cats_str.split(','):
                cat_name = cat_name.strip()
                if cat_name:
                    c, _ = CATEGORIA.objects.get_or_create(name=cat_name)
                    producto.categorias.add(c)
        
        for f in request.FILES.getlist('imagenes'):
            img = IMG_PRODUCTO.objects.create(imagen=f)
            producto.imagenes.add(img)
            
        return JsonResponse({'status': 'ok', 'producto': producto.renderJson()})
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_productos_detail(request, pid):
    from django.http import JsonResponse
    if request.method not in ['POST', 'DELETE']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'DELETE':
        PRODUCTO.objects.filter(id=pid).delete()
        return JsonResponse({'status': 'ok'})
        
    if request.method == 'POST':
        try:
            producto = PRODUCTO.objects.get(id=pid)
            producto.nombre = request.POST.get('nombre', producto.nombre)
            producto.descripcion = request.POST.get('descripcion', producto.descripcion)
            producto.precio = request.POST.get('precio', producto.precio)
            producto.material = request.POST.get('material', producto.material)
            producto.dimensiones = request.POST.get('dimensiones', producto.dimensiones)
            
            new_codigo = request.POST.get('codigo_unico', '').strip()
            if new_codigo:
                producto.codigo_unico = new_codigo
            
            producto.agotado = request.POST.get('agotado', 'false').lower() == 'true'
            producto.save()
            
            cats_str = request.POST.get('categoria', '')
            if cats_str:
                producto.categorias.clear()
                for cat_name in cats_str.split(','):
                    cat_name = cat_name.strip()
                    if cat_name:
                        c, _ = CATEGORIA.objects.get_or_create(name=cat_name)
                        producto.categorias.add(c)
                        
            files = request.FILES.getlist('imagenes')
            if files:
                producto.imagenes.clear()
                for f in files:
                    img = IMG_PRODUCTO.objects.create(imagen=f)
                    producto.imagenes.add(img)
                    
            return JsonResponse({'status': 'ok', 'producto': producto.renderJson()})
        except PRODUCTO.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

def api_textos(request):
    from django.http import JsonResponse
    conf = CONF_WEB.objects.first()
    return JsonResponse(conf.renderJson() if conf else {})

@csrf_exempt
def api_pedidos(request):
    from django.http import JsonResponse
    import json
    if request.method == 'POST':
        data = json.loads(request.body)
        pedido = PEDIDO.objects.create(
            cliente_nombre=data.get('nombre', ''),
            cliente_email=data.get('email', ''),
            cliente_telefono=data.get('telefono', ''),
            cliente_direccion=data.get('direccion', ''),
            items_json=json.dumps(data.get('items', [])),
            total=data.get('total', '')
        )
        return JsonResponse({'pedido': pedido.renderJson()})
    elif request.method == 'GET':
        pedidos = [p.renderJson() for p in PEDIDO.objects.all().order_by('-id')]
        return JsonResponse(pedidos, safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_pedidos_detail(request, pid):
    from django.http import JsonResponse
    if request.method not in ['POST', 'DELETE']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'DELETE':
        PEDIDO.objects.filter(id=pid).delete()
        return JsonResponse({'status': 'ok'})
        
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            pedido = PEDIDO.objects.get(id=pid)
            if 'estado' in data:
                pedido.estado = data['estado']
                pedido.save()
            return JsonResponse({'status': 'ok', 'pedido': pedido.renderJson()})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def api_admin_login(request):
    from django.http import JsonResponse
    from .models import CONF_WEB
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pin = str(data.get('pin', '')).strip()
            conf = CONF_WEB.objects.first()
            valid_pin = conf.admin_password if conf and conf.admin_password else 'G89qpjksr**'
            
            if pin == valid_pin:
                return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'error': 'Unauthorized'}, status=401)
