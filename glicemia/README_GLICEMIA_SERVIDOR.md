# Sistema Glicemia -- Deploy y Mantenimiento

Servidor interno del sistema de cálculo de infusión de insulina.

## Dirección del sistema

http://192.168.6.254

------------------------------------------------------------------------

# Arquitectura del sistema

Navegador\
↓\
NGINX (puerto 80)\
↓\
Gunicorn (127.0.0.1:8001)\
↓\
Django (proyecto glicemia)

NGINX también sirve los archivos estáticos (CSS, JS, imágenes).

------------------------------------------------------------------------

# Ubicación del proyecto

/home/bere/proyectos/Glicemia-Calculadora/glicemia

Base de datos: db.sqlite3

------------------------------------------------------------------------

# Servicio del sistema

Nombre del servicio:

glicemia

Ver estado:

sudo systemctl status glicemia

Reiniciar aplicación:

sudo systemctl restart glicemia

Detener aplicación:

sudo systemctl stop glicemia

------------------------------------------------------------------------

# Nginx

Configuración:

/etc/nginx/sites-available/glicemia

Recargar configuración:

sudo systemctl reload nginx

Reiniciar nginx:

sudo systemctl restart nginx

------------------------------------------------------------------------

# Logs

Ver últimos logs del sistema:

sudo journalctl -u glicemia -n 50 --no-pager

Ver logs en vivo:

sudo journalctl -u glicemia -f

------------------------------------------------------------------------

# Si modificás el código Python

cd \~/proyectos/Glicemia-Calculadora/glicemia source venv/bin/activate
sudo systemctl restart glicemia

------------------------------------------------------------------------

# Si modificás CSS o archivos static

cd \~/proyectos/Glicemia-Calculadora/glicemia source venv/bin/activate
python manage.py collectstatic --noinput

Luego:

sudo systemctl restart glicemia sudo systemctl reload nginx

------------------------------------------------------------------------

# Backup de la base de datos

Archivo:

db.sqlite3

Crear copia:

cp db.sqlite3 db_backup.sqlite3

------------------------------------------------------------------------

# Reinicio del servidor

Si la PC servidor se reinicia:

Nginx y Gunicorn arrancan automáticamente.

No es necesario iniciar el proyecto manualmente.

------------------------------------------------------------------------

# Diagnóstico rápido si el sistema no abre

1.  Ver nginx sudo systemctl status nginx

2.  Ver aplicación sudo systemctl status glicemia

3.  Ver puerto ss -ltnp \| grep 8001

Debe mostrar 127.0.0.1:8001 escuchando.

------------------------------------------------------------------------

# URL del sistema

http://192.168.6.254
