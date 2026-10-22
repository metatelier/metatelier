# -*- coding: utf-8 -*-
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from modelos.models import CONF_WEB

def _is_admin(request):
    """
    Verifica si el PIN enviado en la cabecera 'x-admin-pin' coincide con el configurado en CONF_WEB.
    """
    pin = request.headers.get('x-admin-pin', '')
    conf = CONF_WEB.objects.first()
    valid_pin = conf.admin_password if conf and conf.admin_password else 'G89qpjksr**'
    return pin == valid_pin

@csrf_exempt
def api_admin_login(request):
    """
    Valida el PIN de administración enviado desde el modal del frontend.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pin = str(data.get('pin', '')).strip()
            conf = CONF_WEB.objects.first()
            valid_pin = conf.admin_password if conf and conf.admin_password else 'G89qpjksr**'
            
            if pin == valid_pin:
                return JsonResponse({'status': 'ok'})
        except Exception:
            pass
    return JsonResponse({'error': 'Unauthorized'}, status=401)
