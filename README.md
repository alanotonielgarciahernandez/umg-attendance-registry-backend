# UMG Attendance Registry — Backend

Backend en Django (6.x) para gestionar registros de asistencia de la Universidad Mariano Gálvez.

## Resumen rápido
- API REST enfocada a catedráticos.
- Autenticación por JWT.
- Generación de reportes PDF de asistencia.
- Preparado para ejecución local, Docker y Kubernetes.

## Estado
Funcional — endpoints implementados y conexión a base de datos.

## Características principales
- Login y emisión de JWT.
- Endpoints para consultas y reportes (puertas, salones, asistencia).
- Generación y envío de PDFs con reportes de asistencia.
- Firma electrónica de PDFs.

## Requisitos
- Python 3.14+
- Django 6.x
- reportlab
- mssql-django (conector SQL Server)
- Otros (ver `requirements.txt`)

## Instala dependencias
```bash
python -m pip install -r requirements.txt
```

## Configuración de entorno
Define las variables de entorno requeridas (o crea un `.env` en la raíz):

```bash
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
DJANGO_SECRET_KEY=tu-clave-secreta-segura
DB_NAME=tu-nombre-de-base-de-datos-sql-server
DB_USER=tu-usuario-sql-server
DB_PASSWORD=tu-contraseña-de-usuario-sql-server
DB_HOST=tu-host-sql-server
DB_PORT=puerto-de-sql-server
EMAIL_EMISOR=tu-correo-electrónico

# Opcionales para firma digital (PKCS#12 / .pfx)
CERT_PATH=./tu_certificado.pfx    # ruta al archivo .pfx o .p12 (puede ser absoluta)
CERT_PASSWORD=tu-contraseña-pfx     # contraseña del archivo .pfx
```

## Envío de correo con Gmail API (opcional)
El envío de reportes por correo se realiza usando Gmail API y OAuth 2.0.

### Requisitos en Google Cloud
1. Crea o usa un proyecto en Google Cloud.
2. Habilita la Gmail API.
3. Configura la pantalla de consentimiento OAuth.
4. Crea credenciales OAuth para una aplicación de escritorio o el flujo que uses para autorizar al usuario.
5. Genera credenciales autorizadas con el scope `https://www.googleapis.com/auth/gmail.compose`.
6. Guarda el archivo resultante como `secrets/token.json`.

### Consideraciones importantes
- `EMAIL_EMISOR` debe coincidir con la cuenta de Gmail que autorizó el token.
- Si cambias los scopes, elimina `secrets/token.json` y vuelve a autorizar.
- No subas `secrets/token.json` a un repositorio público.
- Si el archivo `secrets/token.json` no existe o no es válido, el envío de correo no se completa.

## Firmas digitales (opcional)

El proyecto puede firmar digitalmente los PDFs de reporte usando un certificado PKCS#12 (`.pfx` / `.p12`) y la librería `pyhanko`.

- **Ruta del certificado**: configure `CERT_PATH` apuntando al archivo `.pfx` dentro del contenedor/host (ruta absoluta o relativa al proyecto).
- **Contraseña**: configure `CERT_PASSWORD` con la contraseña del archivo PKCS#12.

Notas:
- Si `CERT_PATH` no apunta a un archivo existente, no se firmarán los archivos PDF.
- Asegúrate de que el archivo `.pfx` tenga permisos restringidos y no lo subas a repositorios públicos.

## Ejecución (desarrollo)
```bash
py manage.py runserver
```

## Ejecución con Docker
```bash
docker build -t umg-assistance-registry .
docker run -d --rm -p 8000:80 \
  -e DJANGO_SECRET_KEY=tu-clave-secreta-segura \
  -e DJANGO_DEBUG=False \
  -e DJANGO_ALLOWED_HOSTS=tu-dominio.com,localhost,127.0.0.1 \
  -e DB_NAME=tu-nombre-de-base-de-datos-sql-server \
  -e DB_USER=tu-usuario-sql-server \
  -e DB_PASSWORD=tu-contraseña-de-usuario-sql-server \
  -e DB_HOST=tu-host-sql-server \
  -e DB_PORT=puerto-de-sql-server \
  -e EMAIL_EMISOR=tu-correo-electrónico \
  -e CERT_PATH=./tu_certificado.pfx \
  -e CERT_PASSWORD=tu-contraseña-pfx \
  umg-assistance-registry
```

Si vas a usar Gmail API dentro del contenedor, asegúrate de montar `secrets/token.json` en la ruta esperada por la aplicación o incluirlo en la imagen durante la construcción. Sin ese archivo, el envío de correo se detiene antes de llamar a Gmail.

## [ Endpoints ]( /ENDPOINTS.md )

## Estructura del proyecto
- `assets/` — imágenes y recursos estáticos usados por los reportes.
- `db/` — funciones para consultas a la base de datos.
- `handlers/`, `routes/` — definición de rutas y controladores.
- `helpers/` — utilidades auxiliares.
- `models/` — modelos que mapean las tablas de la base de datos.
- `reports/` — sistema de reportería.
- `middlewares/` — validaciones y seguridad (JWT, roles).
- `tokens/` — manejo de JWT.

## Pruebas y verificación
- Asegúrate de que las variables de entorno de DB estén correctas.
- Ejecuta migraciones si aplican y prueba endpoints con `curl` o Postman.
