# -*- coding: utf-8 -*-
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from modelos.models import PEDIDO
from modelos.views.api_auth import _is_admin

@csrf_exempt
def api_pedidos(request):
    """
    POST: Registra una nueva solicitud de pedido desde el checkout del cliente.
    GET: Lista todos los pedidos recibidos (para el buzón del administrador).
    """
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
    """
    POST: Modifica el estado de un pedido (ej. 'Pendiente', 'Atendido', 'Entregado').
    DELETE: Elimina una solicitud del buzón de pedidos.
    """
    if request.method not in ['POST', 'DELETE']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'DELETE':
        PEDIDO.objects.filter(id=pid).delete()
        return JsonResponse({'status': 'ok'})
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pedido = PEDIDO.objects.get(id=pid)
            if 'estado' in data:
                pedido.estado = data['estado']
                pedido.save()
            return JsonResponse({'status': 'ok', 'pedido': pedido.renderJson()})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
