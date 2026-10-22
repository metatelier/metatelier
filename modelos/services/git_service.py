# -*- coding: utf-8 -*-
"""
Servicio para la integración de Git y respaldos automáticos en GitHub.
Diseñado para entornos Windows / Django con protección de candados SQLite.
"""
import subprocess
import re
from django.db import connections

def _git_run(*args):
    """
    Ejecuta un comando de Git de forma segura con captura de pipes
    para evitar fallos por broken pipe o consolas no interactivas en Windows.
    """
    res = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if res.returncode != 0:
        err = res.stderr.strip() or res.stdout.strip()
        raise Exception(f"Git error ({res.returncode}): {err}")
    return res.stdout.strip()

def get_versions_list(limit=40):
    """
    Obtiene la lista de los últimos commits de Git formateados para el selector.
    """
    out = _git_run('git', 'log', f'-n', str(limit), '--pretty=format:%h|%s|%ad', '--date=format:%d/%m/%Y %H:%M')
    versions = []
    for line in out.splitlines():
        parts = line.strip().split('|', 2)
        if len(parts) == 3:
            versions.append({
                'hash': parts[0],
                'subject': parts[1],
                'date': parts[2]
            })
    return versions

def get_next_version():
    """
    Analiza el historial de versiones con formato 'vX.Y.Z' y calcula la siguiente versión correlativa.
    """
    out = _git_run('git', 'log', '-n', '50', '--pretty=format:%s')
    versions = []
    for line in out.splitlines():
        m = re.search(r'v(\d+)\.(\d+)\.(\d+)', line)
        if m:
            versions.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    
    latest = max(versions) if versions else (1, 0, 0)
    return f"v{latest[0]}.{latest[1]}.{latest[2] + 1}"

def create_backup(nota=''):
    """
    Empaqueta el estado actual de la tienda, genera el commit con la siguiente versión
    y sube los cambios a GitHub.
    """
    next_ver = get_next_version()
    commit_msg = f"{next_ver} - {nota if nota else 'Respaldo manual desde panel web'}"

    # 1. Agregar cambios al área de preparación
    _git_run('git', 'add', '.')

    # 2. Comprobar si hay cambios pendientes o hacer commit allow-empty
    status = _git_run('git', 'status', '--porcelain')
    if status:
        _git_run('git', 'commit', '-m', commit_msg)
    else:
        _git_run('git', 'commit', '--allow-empty', '-m', f"{commit_msg} (Sin cambios)")

    # 3. Push a GitHub
    _git_run('git', 'push', 'origin', 'main')

    return next_ver

def restore_version(target_hash):
    """
    Restaura la tienda al estado del commit indicado.
    Cierra conexiones SQLite para evitar el bloqueo 'unable to unlink db.sqlite3' en Windows.
    """
    if not target_hash or not re.match(r'^[a-fA-F0-9]{4,40}$', target_hash):
        raise ValueError('Hash de versión inválido.')

    next_ver = get_next_version()
    target_subject = _git_run('git', 'log', '-n', '1', '--pretty=format:%s', target_hash)

    # 1. Asegurar cambios pendientes actuales antes de restaurar
    _git_run('git', 'add', '.')
    status = _git_run('git', 'status', '--porcelain')
    if status:
        _git_run('git', 'commit', '-m', 'Auto-backup de seguridad antes de restaurar')

    # 2. CERRAR CONEXIONES SQLITE PARA LIBERAR ARCHIVO BLOQUEADO EN WINDOWS
    connections.close_all()

    # 3. Restaurar archivos al estado del commit seleccionado
    try:
        _git_run('git', 'checkout', target_hash, '--', '.')
    except Exception as e:
        if 'db.sqlite3' in str(e):
            _git_run('git', 'checkout', target_hash, '--', 'modelos/', 'templates/', 'static/', 'staticfiles/', 'productos/', 'LuxuryMonsei/')
            db_bytes = subprocess.check_output(['git', 'show', f"{target_hash}:db.sqlite3"])
            with open('db.sqlite3', 'wb') as f_db:
                f_db.write(db_bytes)
        else:
            raise

    # 4. Registrar la restauración como nueva versión en la secuencia
    restore_msg = f"{next_ver} - Restauracion a version [{target_hash}] ({target_subject})"
    _git_run('git', 'add', '.')
    _git_run('git', 'commit', '--allow-empty', '-m', restore_msg)

    # 5. Sincronizar archivos estáticos
    try:
        subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], capture_output=True)
    except:
        pass

    # 6. Sincronizar con GitHub
    _git_run('git', 'push', 'origin', 'main')

    return next_ver
