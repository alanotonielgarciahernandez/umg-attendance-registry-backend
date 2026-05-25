# cursos_route.py
# Definición de la ruta para la tabla de cursos.

# Importar módulos de Python.
import json
from datetime import date

# Importar módulos de Django.
from django.http import JsonResponse
from django.views import View

# Importar middlewares.
from middlewares.validate_jwt import validateJWT

# Importar modelos.
from models.usuario_model import Usuario

# Importar funciones de la base de datos.
from db.get_asistencia import get_curso_asistencia_by_persona
from db.get_cursos import get_cursos_by_persona
from db.set_asistencia import save_asistencia

# Importar funciones de reportes.
from reports.asistencia_report import generar_registro_asistencia
from reports.email_report import enviar_email_registro_asistencia
from reports.signature_report import firmar_pdf

class CursosView( View ):
    def get( self, request ) -> JsonResponse:
        # Validar que el encabezado de autorización esté presente.
        auth_header: str = request.headers.get( 'Authorization' )
        if not auth_header:
            return JsonResponse( { 'detail': 'El encabezado de autorización es requerido.' }, status=401 )
        
        # Validar el token JWT.
        user: Usuario = validateJWT( auth_header )
        if user is None:
            return JsonResponse( { 'detail': 'Usuario no válido.' }, status=401 )

        # Obtener la lista de cursos desde la base de datos.
        curso_list: list[ dict ] = get_cursos_by_persona( user )

        return JsonResponse( curso_list, safe=False )

class AsistenciaView( View ):
    # Obtener la lista de asistencia para un curso específico.
    def get( self, request, id_asignacion: int ) -> JsonResponse:
        # Obtener la fecha de consulta de los parámetros de la solicitud, o usar la fecha actual si no se proporciona.
        fecha: date = request.GET.get( 'fecha', date.today() )

        # Validar que el encabezado de autorización esté presente.
        auth_header: str = request.headers.get( 'Authorization' )
        if not auth_header:
            return JsonResponse( { 'detail': 'El encabezado de autorización es requerido.' }, status=401 )
        
        # Validar el token JWT.
        user: Usuario = validateJWT( auth_header )
        if user is None:
            return JsonResponse( { 'detail': 'Usuario no válido.' }, status=401 )

        # Obtener la lista de asistencia desde la base de datos.
        list_asistencia: list[ dict ] = get_curso_asistencia_by_persona( id_asignacion, user, fecha )
        if list_asistencia is None:
            return JsonResponse( { 'detail': 'Curso no encontrado.' }, status=404 )

        return JsonResponse( list_asistencia, safe=False )
    
    def post( self, request, id_asignacion ) -> JsonResponse:
        # Validar que el encabezado de autorización esté presente.
        auth_header: str = request.headers.get( 'Authorization' )
        if not auth_header:
            return JsonResponse( { 'detail': 'El encabezado de autorización es requerido.' }, status=401 )
        
        # Validar el token JWT.
        user: Usuario = validateJWT( auth_header )
        if user is None:
            return JsonResponse( { 'detail': 'Usuario no válido.' }, status=401 )
        
        # Obtenemos datos de asistencia del cuerpo de la solicitud.
        body: dict = json.loads( request.body )

        # Guardar el registro de asistencia en la base de datos.
        status: dict = save_asistencia( id_asignacion, user, body.get( 'fecha', date.today() ), body.get( 'asistencias', [] ) )
        if status is None:
            return JsonResponse( { 'detail': 'Error al guardar el registro.' }, status=500 )
        
        # Generar el reporte de asistencia en PDF.
        pdf_path: str = generar_registro_asistencia( id_asignacion, body.get( 'fecha', date.today() ), body.get( 'asistencias', [] ) )
        if pdf_path is None:
            return JsonResponse( { 'detail': 'Error al generar el reporte.' }, status=500 )
        
        # Firmar digitalmente el PDF generado.
        firmar_pdf( pdf_path )

        # Enviar el PDF por correo electrónico al usuario.
        enviar_email_registro_asistencia( pdf_path, user.correo, id_asignacion, body.get( 'fecha', date.today() ), user )

        # Serializar manualmente.
        data: dict = {
            'confirmado': True,
            'total_presentes': status[ 'total_presentes' ],
            'total_ausentes': status[ 'total_ausentes' ],
            'pdf_url': pdf_path
        }

        return JsonResponse( data, safe=False )
    