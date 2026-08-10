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

def api_productos(request):
    from django.http import JsonResponse
    prods = []
    for p in PRODUCTO.objects.all():
        prods.append(p.renderJson())
    return JsonResponse(prods, safe=False)

@csrf_exempt
def api_productos_detail(request, pid):
    from django.http import JsonResponse
    if request.method == 'DELETE':
        PRODUCTO.objects.filter(id=pid).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

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
    if request.method == 'DELETE':
        PEDIDO.objects.filter(id=pid).delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

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
