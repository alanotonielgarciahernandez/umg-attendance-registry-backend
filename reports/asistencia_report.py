# asistencia_report.py
# Script para generar un reporte de asistencia en formato PDF.

# Importar módulos de Python.
from datetime import date

# Importar módulos de terceros.
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image as PlatypusImage
import io
import os
import urllib.request

# Importar modelos.
from models.registro_model import Asistencia
from models.curso_model import Curso
from models.persona_model import Persona

# Carga imagen de la persona.
def _cargar_fotografia( path: str ):
    dimensiones: int = 40
    ruta_placeholder = os.path.abspath( os.path.join(os.path.dirname( __file__ ), '..', 'assets', 'images', 'pfp-placeholder.jpg' ) )
    
    # Extraer la imagen.
    if path:
        with urllib.request.urlopen( path, timeout=5 ) as resp:
            data = resp.read()
        return PlatypusImage( io.BytesIO( data ), width=dimensiones, height=dimensiones )

    # Si no hay ruta o no se pudo cargar la imagen, usar el placeholder.
    return PlatypusImage( ruta_placeholder, width=dimensiones, height=dimensiones )

def generar_registro_asistencia( id_asignacion: int, fecha_asistencia: date, lista_asistencia: list[ dict ] ) -> str:
    # Obtener información del curso desde la base de datos.
    curso: Curso = Curso.objects.get( id_asignacion=id_asignacion )

    # Convertir la lista de asistencia a objetos de tipo Asistencia.
    assitance_list: list[ Asistencia ] = [
        Asistencia(
            persona=Persona.objects.get( id_persona=assistance[ 'id_persona' ] ),
            estado=assistance[ 'estado' ],
        )
        for assistance in lista_asistencia
    ]

    # Calcular totales de asistencia.
    total_registros = len( assitance_list )
    total_presentes = sum( 1 for a in assitance_list if a.estado.lower() == 'presente' )
    total_ausentes = total_registros - total_presentes

    # Posición vertical en donde dibujar objetos.
    canvas_y_position: int = 710

    # Crear un nuevo PDF.
    pdf_path = f'media/asistencia-{ id_asignacion }-{ fecha_asistencia }.pdf'
    c: canvas.Canvas = canvas.Canvas( pdf_path, pagesize=letter )

    # Colores generales
    c.setStrokeColor( colors.HexColor( '#BDC3C7' ) ) # Gris claro

    # =============== PRIMERA TARJETA ===============
    c.setFillColor( colors.HexColor( '#2E5B88' ) ) # Azul oscuro para el fondo de la tarjeta.
    c.roundRect( 50, 660, 512, 100, 10, fill=1 ) # X, Y, Width, Height, Radius
    
    # Agregar el logo de la universidad.
    c.drawImage( 'assets/images/logo.png', 60, 670, width=80, height=80, preserveAspectRatio=True, mask='auto' )

    # Texto en blanco para el texto de la tarjeta.
    c.setFillColor( colors.white )
    
    c.setFont( 'Helvetica-Bold', 22 )
    c.drawString( 150, 720, 'Reporte de Asistencia' )
    
    c.setFont( 'Helvetica', 12 )
    c.drawString( 490, 720, f'{ fecha_asistencia }' )

    c.setFont( 'Helvetica', 14 )
    c.drawString( 150, 690, curso.nombre_curso )

    c.setFont( 'Helvetica', 12 )
    c.drawString( 400, 690, 'Universidad Mariano Gálvez' )

    # =============== SEGUNDA TARJETA ===============
    c.roundRect( 50, 510, 512, 130, 10, fill=0 )

    # Texto en negro para el texto de la tarjeta.
    c.setFillColor( colors.black )
    
    c.setFont( 'Helvetica-Bold', 12 )
    c.drawString( 60, 615, 'Información del Curso' )
    c.line( 60, 610, 270, 610 )

    # Info Curso
    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 60, 590, 'Nombre:' )
    c.setFont( 'Helvetica', 10 )
    c.drawString( 120, 590, str( curso.nombre_curso ) )

    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 60, 570, 'Horario:' )
    c.setFont( 'Helvetica', 10 )
    c.drawString( 120, 570, str( curso.horario ) )

    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 60, 550, 'Salón:' )
    c.setFont( 'Helvetica', 10 )
    c.drawString( 120, 550, str( curso.salon.nombre ) if curso.salon else '' )

    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 60, 530, 'Catedrático:' )
    c.setFont( 'Helvetica', 10 )
    catedratico_name = f'{ curso.persona.nombre } { curso.persona.apellido }' if hasattr( curso, 'persona' ) and curso.persona else 'No asignado'
    c.drawString( 120, 530, catedratico_name )

    # Resumen de Asistencia
    c.setFont( 'Helvetica-Bold', 12 )
    c.drawString( 300, 615, 'Resumen de Asistencia' )
    c.line( 300, 610, 510, 610 )

    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 300, 595, 'Registros:' )
    c.setFont( 'Helvetica', 10 )
    c.drawString( 370, 595, str( total_registros ) )

    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 300, 575, 'Presentes:' )
    c.setFont( 'Helvetica', 10 )
    c.setFillColor( colors.HexColor( '#27AE60' ) ) # Green
    c.drawString( 370, 575, str( total_presentes ) )

    c.setFillColor( colors.black )
    c.setFont( 'Helvetica-Bold', 10 )
    c.drawString( 300, 555, 'Ausentes:' )
    c.setFont( 'Helvetica', 10 )
    c.setFillColor( colors.HexColor( '#E74C3C' ) ) # Red
    c.drawString( 370, 555, str( total_ausentes ) )
    c.setFillColor( colors.black )

    # =============== TABLA DE ASISTENCIA ===============
    canvas_y_position = 490

    # Construir los datos para la tabla de asistencia.
    table_data = [ [ 'Foto', 'Nombre', 'Estado' ] ]
    
    # Estilos para la tabla de asistencia.
    style_list = [
        ( 'BACKGROUND', ( 0, 0 ), ( -1, 0 ), colors.HexColor('#2E5B88') ),
        ( 'TEXTCOLOR', ( 0, 0 ), ( -1, 0 ), colors.whitesmoke ),
        ( 'ALIGN', ( 0, 0 ), ( -1, -1 ), 'CENTER' ),
        ( 'FONTNAME', ( 0, 0 ), ( -1, 0 ), 'Helvetica-Bold' ),
        ( 'FONTSIZE', ( 0, 0 ), ( -1, 0 ), 12 ),
        ( 'BOTTOMPADDING', ( 0, 0 ), ( -1, 0 ), 8 ),
        ( 'TOPPADDING', ( 0, 0 ), ( -1, 0 ), 8 ),
        ( 'BACKGROUND', ( 0, 1 ), ( -1, -1 ), colors.HexColor('#F2F6FA') ),
        ( 'ALIGN', ( 1, 1 ), ( 1, -1 ), 'LEFT' ),
        ( 'GRID', ( 0, 0 ), ( -1, -1 ), 0.5, colors.HexColor('#BDC3C7') ),
        ( 'FONTNAME', ( 0, 1 ), ( -1, -1 ), 'Helvetica' ),
        ( 'FONTSIZE', ( 0, 1 ), ( -1, -1 ), 10 ),
        ( 'VALIGN', ( 0, 0 ), ( -1, -1 ), 'MIDDLE' )
    ]

    # Agregar filas de asistencia a la tabla.
    for index, assistance in enumerate( assitance_list, 1 ):
        # Obtener imagen (usar placeholder si no hay ruta).
        img_cell = _cargar_fotografia( assistance.persona.path_photo )

        # Agregar la fila a la tabla (Foto, Nombre, Estado).
        table_data.append([
            img_cell,
            f'{ assistance.persona.nombre } { assistance.persona.apellido }',
            assistance.estado.capitalize(),
        ])

        # Cambiar el color del texto del estado según si es presente o ausente.
        if assistance.estado.lower() == 'presente':
            status_color = colors.HexColor( '#27AE60' )
        else:
            status_color = colors.HexColor( '#E74C3C' )

        # Agregar estilos para la celda del estado (columna 2 ahora).
        style_list.append( ( 'TEXTCOLOR', ( 2, index ), ( 2, index ), status_color ) )
        style_list.append( ( 'FONTNAME', ( 2, index ), ( 2, index ), 'Helvetica-Bold' ) )

    # Crear la tabla de asistencia con los datos y estilos definidos.
    table: Table = Table(
        data=table_data,
        colWidths=[ 48, 324, 140 ],
        style=TableStyle( style_list )
    )

    # Alternar el color de fondo de las filas para mejorar la legibilidad.
    for i in range( 1, len( table_data ) ):
        if i % 2 == 0:
            table.setStyle( TableStyle( [ ( 'BACKGROUND', ( 0, i ), ( -1, i ), colors.white ) ] ) )
    
    # Dibujar la tabla en el PDF.
    table_width, table_height = table.wrapOn( c, 512, canvas_y_position )
    table.drawOn( c, ( 612 - table_width ) / 2.0, canvas_y_position - table_height )

    # Guardar el PDF.
    c.save()

    return pdf_path
