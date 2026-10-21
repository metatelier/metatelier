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
from django.db import IntegrityError
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

def GetMenu():
    conf = CONF_WEB.objects.first()
    if not conf:
        conf = CONF_WEB.objects.create()
    return conf.renderJson()

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
        except IntegrityError:
            return JsonResponse({'error': f'El código único ya está en uso. Por favor, elige otro.'}, status=400)
        except PRODUCTO.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

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

@csrf_exempt
def api_git_backup(request):
    from django.http import JsonResponse
    import subprocess, re, json
    
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'POST':
        try:
            nota = ''
            if request.body:
                try:
                    data = json.loads(request.body)
                    nota = data.get('nota', '').strip()
                except:
                    pass
            
            # 1. Determinar siguiente version correlativa
            out = subprocess.check_output(['git', 'log', '-n', '50', '--pretty=format:%s'], text=True, encoding='utf-8')
            versions = []
            for line in out.splitlines():
                m = re.search(r'v(\d+)\.(\d+)\.(\d+)', line)
                if m:
                    versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
            
            latest = max(versions) if versions else (1, 0, 0)
            next_ver = f"v{latest[0]}.{latest[1]}.{latest[2] + 1}"
            
            commit_msg = f"{next_ver} - {nota if nota else 'Respaldo manual desde panel web'}"
            
            # 2. Agregar cambios
            subprocess.run(['git', 'add', '.'], check=True)
            
            # 3. Comprobar si hay cambios o hacer commit allow-empty
            status = subprocess.check_output(['git', 'status', '--porcelain'], text=True, encoding='utf-8')
            if status.strip():
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            else:
                subprocess.run(['git', 'commit', '--allow-empty', '-m', f"{commit_msg} (Sin cambios)"], check=True)
            
            # 4. Push a GitHub
            push_res = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True, encoding='utf-8')
            if push_res.returncode != 0:
                return JsonResponse({'error': f'Error al subir a GitHub: {push_res.stderr}'}, status=500)
                
            return JsonResponse({
                'status': 'ok',
                'version': next_ver,
                'message': f'Copia de seguridad {next_ver} creada y subida a GitHub exitosamente.'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_git_versions(request):
    from django.http import JsonResponse
    import subprocess
    
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    try:
        out = subprocess.check_output(
            ['git', 'log', '-n', '40', '--pretty=format:%h|%s|%ad', '--date=format:%d/%m/%Y %H:%M'],
            text=True, encoding='utf-8'
        )
        versions = []
        for line in out.splitlines():
            parts = line.strip().split('|', 2)
            if len(parts) == 3:
                versions.append({
                    'hash': parts[0],
                    'subject': parts[1],
                    'date': parts[2]
                })
        return JsonResponse({'status': 'ok', 'versions': versions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_git_restore(request):
    from django.http import JsonResponse
    import subprocess, json, re
    
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target_hash = str(data.get('hash', '')).strip()
            
            if not target_hash or not re.match(r'^[a-fA-F0-9]{4,40}$', target_hash):
                return JsonResponse({'error': 'Hash de versión inválido.'}, status=400)
                
            # Siguiente versión correlativa para el commit de restauración
            out = subprocess.check_output(['git', 'log', '-n', '50', '--pretty=format:%s'], text=True, encoding='utf-8')
            versions = []
            for line in out.splitlines():
                m = re.search(r'v(\d+)\.(\d+)\.(\d+)', line)
                if m:
                    versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
            latest = max(versions) if versions else (1, 0, 0)
            next_ver = f"v{latest[0]}.{latest[1]}.{latest[2] + 1}"
            
            # Obtener nombre/asunto del commit objetivo
            target_subject = subprocess.check_output(
                ['git', 'log', '-n', '1', '--pretty=format:%s', target_hash],
                text=True, encoding='utf-8'
            ).strip()
            
            # 1. Asegurar cambios pendientes actuales antes de restaurar
            subprocess.run(['git', 'add', '.'], check=True)
            status = subprocess.check_output(['git', 'status', '--porcelain'], text=True, encoding='utf-8')
            if status.strip():
                subprocess.run(['git', 'commit', '-m', f"Auto-backup de seguridad antes de restaurar"], check=True)
            
            # 2. Restaurar archivos al estado del commit seleccionado
            subprocess.run(['git', 'checkout', target_hash, '--', '.'], check=True)
            
            # 3. Registrar la restauración como nueva versión en la secuencia
            restore_msg = f"{next_ver} - Restauracion a version [{target_hash}] ({target_subject})"
            subprocess.run(['git', 'add', '.'], check=True)
            status_after = subprocess.check_output(['git', 'status', '--porcelain'], text=True, encoding='utf-8')
            if status_after.strip():
                subprocess.run(['git', 'commit', '-m', restore_msg], check=True)
            else:
                subprocess.run(['git', 'commit', '--allow-empty', '-m', f"{restore_msg} (Sin diferencias)"], check=True)
            
            # Sincronizar archivos estaticos
            try:
                subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=False)
            except:
                pass

            # 4. Sincronizar con GitHub
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            return JsonResponse({
                'status': 'ok',
                'version': next_ver,
                'message': f'Tienda restaurada exitosamente a la versión [{target_hash}]. Quedó registrada como {next_ver}.'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

