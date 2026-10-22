# -*- coding: utf-8 -*-
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from modelos.models import PRODUCTO, CATEGORIA, IMG_PRODUCTO, CONF_WEB
from modelos.views.api_auth import _is_admin

@csrf_exempt
def api_productos(request):
    """
    GET: Lista todos los productos en formato JSON.
    POST: Crea un nuevo producto (requiere autenticación con PIN de admin).
    """
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
            codigo_unico = f"MET-A-{uuid.uuid4().hex[:6].upper()}"
        agotado = request.POST.get('agotado', 'false').lower() == 'true'
        
        try:
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
        except IntegrityError:
            return JsonResponse({'error': f'El código único {codigo_unico} ya está en uso. Por favor, elige otro o déjalo en blanco.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_productos_detail(request, pid):
    """
    POST: Actualiza un producto existente por su ID.
    DELETE: Elimina un producto por su ID.
    """
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
        except IntegrityError:
            return JsonResponse({'error': 'El código único ya está en uso. Por favor, elige otro.'}, status=400)
        except PRODUCTO.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def api_textos(request):
    """
    Retorna la configuración visual y textos del modelo CONF_WEB.
    """
    conf = CONF_WEB.objects.first()
    return JsonResponse(conf.renderJson() if conf else {})
