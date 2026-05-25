# email_report.py
# Reporte de asistencia por correo electrónico.

# Importar módulos de Python.
import base64
import os.path
from datetime import date
from email.message import EmailMessage

# Importar módulos de Google.
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Importar modelos.
from models.curso_model import Curso
from models.usuario_model import Usuario

# Scopes para la API de Gmail. Eliminar el archivo token.json en caso de modificación a los Scopes.
SCOPES = [ 'https://www.googleapis.com/auth/gmail.compose' ]

def enviar_email_registro_asistencia( pdf_path: str, email_receptor: str, id_asignacion: int, fecha: date, user: Usuario ):
  # Obtener información del curso desde la base de datos.
  curso: Curso = Curso.objects.get( id_asignacion=id_asignacion )

  credenciales = None
  
  # Cargar credenciales desde el archivo token.json si existe.
  if os.path.exists( 'secrets/token.json' ):
    credenciales = Credentials.from_authorized_user_file( 'secrets/token.json', SCOPES )
  
  # Si no hay credenciales válidas, iniciar el proceso de autenticación.
  if not credenciales or not credenciales.valid:
    if credenciales and credenciales.expired and credenciales.refresh_token:
      credenciales.refresh( Request() )
    else:
      print( 'No se encontraron credenciales válidas. Por favor, autentíquese para generar el archivo token.json.' )
      return
    
    # Guardar las credenciales para la próxima ejecución.
    with open( 'secrets/token.json', 'w' ) as token:
      token.write( credenciales.to_json() )

  try:
    # Crear el servicio de Gmail y el mensaje de correo electrónico.
    service = build( 'gmail', 'v1', credentials=credenciales )
    message = EmailMessage()

    # Encabezados del correo electrónico.
    message[ 'To' ] = email_receptor
    message[ 'From' ] = os.getenv( 'EMAIL_EMISOR' )
    message[ 'Subject' ] = f'Registro de Asistencia - { fecha } - { curso.nombre_curso }'

    # Cuerpo del correo electrónico.
    message.set_content(
        f'Estimado/a { user.persona.nombre } { user.persona.apellido },\n\n'
        f'Le informamos que se ha registrado su asistencia para el curso: { curso.nombre_curso } el día { fecha }.\n\n'
        'Por favor revise el documento y confirme la recepción.\n\n'
        'Saludos cordiales,\nUniversidad Mariano Gálvez de Guatemala'
    )

    # Agregar un archivo adjunto al correo electrónico.
    attachment_filename = os.path.basename( pdf_path )

    with open( pdf_path, "rb" ) as fp:
      attachment_data = fp.read()
    message.add_attachment( attachment_data, 'application', 'pdf', filename=attachment_filename )

    encoded_message = base64.urlsafe_b64encode( message.as_bytes() ).decode()

    create_message = { "raw": encoded_message }

    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send( userId='me', body=create_message )
        .execute()
    )
  except HttpError as error:
    print( f'An error occurred: { error }' )
