# -*- coding: utf-8 -*-
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from modelos.views.api_auth import _is_admin
from modelos.services.git_service import (
    create_backup,
    get_versions_list,
    restore_version
)

@csrf_exempt
def api_git_backup(request):
    """
    Endpoint para crear un nuevo respaldo correlativo en GitHub desde el panel web.
    """
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'POST':
        try:
            nota = ''
            if request.body:
                try:
                    data = json.loads(request.body)
                    nota = data.get('nota', '').strip()
                except Exception:
                    pass
            
            next_ver = create_backup(nota)
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
    """
    Endpoint para listar las versiones disponibles en GitHub.
    """
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    try:
        versions = get_versions_list(limit=40)
        return JsonResponse({'status': 'ok', 'versions': versions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_git_restore(request):
    """
    Endpoint para restaurar la tienda a una versión seleccionada de GitHub.
    """
    if not _is_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target_hash = str(data.get('hash', '')).strip()
            
            next_ver = restore_version(target_hash)
            return JsonResponse({
                'status': 'ok',
                'version': next_ver,
                'message': f'Tienda restaurada exitosamente a la versión [{target_hash}]. Quedó registrada como {next_ver}.'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)
